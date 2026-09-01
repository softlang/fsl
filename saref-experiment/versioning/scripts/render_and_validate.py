#!/usr/bin/env python3
"""Render an LLM candidate version-addition into a reviewable patch, and validate it.

Never writes to the real ontology module. On a full pass, writes a patched
copy of the target module plus a unified diff and review notes to
results/versioning/candidate-patches/ -- still a human-reviewed candidate,
not an instruction to merge. On any failure, writes only the validation
report to results/versioning/validation/ and exits non-zero.

Validation runs in three stages, each gating the next:
  1. the response matches its JSON schema and its evidence-derived fields
     (reuses validate_response.check_fields)
  2. turtleBlock parses as Turtle and declares the triples it claims to
  3. the version, merged into a copy of the target module plus the two
     links (parent hasVersion, predecessor hasSuccessor) this tooling adds
     deterministically, keeps the module OWL-consistent and does not
     duplicate an existing version tag for the same parent
"""

import argparse
import difflib
import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker
from rdflib import Graph, URIRef
from rdflib.namespace import RDF

sys.path.insert(0, str(Path(__file__).resolve().parent))
from validate_response import check_fields  # noqa: E402

TIME_NS = "http://www.w3.org/2006/time#"
TBOX_VERSION_CLASS = {"language": "LanguageVersion", "tool": "ToolVersion"}


def read_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def curie_to_uri(curie: str, ns: dict) -> str:
    prefix, local = curie.split(":", 1)
    return ns[prefix] + local


def local_name(curie: str) -> str:
    return curie.split(":", 1)[1]


def extract_prefix_header(module_text: str) -> str:
    lines = []
    for line in module_text.splitlines():
        stripped = line.strip()
        if stripped.startswith("@prefix") or stripped.startswith("@base"):
            lines.append(line)
        elif stripped == "":
            continue
        else:
            break
    return "\n".join(lines)


def obj_values(graph: Graph, subject: URIRef, predicate: URIRef) -> list[str]:
    return [str(o) for o in graph.objects(subject, predicate)]


class ValidationReport:
    def __init__(self, run_id: str):
        self.run_id = run_id
        self.checks: list[dict] = []

    def add(self, name: str, ok: bool, detail: str = "") -> bool:
        self.checks.append({"name": name, "status": "PASS" if ok else "FAIL", "detail": detail})
        return ok

    @property
    def passed(self) -> bool:
        return all(c["status"] == "PASS" for c in self.checks)

    def to_dict(self) -> dict:
        return {"runId": self.run_id, "overall": "PASS" if self.passed else "FAIL", "checks": self.checks}


def write_report(report: ValidationReport, out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{report.run_id}.json"
    out_path.write_text(json.dumps(report.to_dict(), indent=2) + "\n", encoding="utf-8")
    return out_path


def split_turtle_block(turtle_block: str) -> tuple[str, str]:
    """Split into (version-individual chunk, release-instant chunk).

    Matches the shape prompts/system.md's worked example requires: the new
    version individual, one blank line, then its release-date time:Instant.
    """
    parts = turtle_block.strip().split("\n\n", 1)
    if len(parts) != 2:
        raise ValueError(
            "turtleBlock must contain the version individual and its release "
            "Instant, separated by exactly one blank line"
        )
    return parts[0].strip() + "\n", parts[1].strip() + "\n"


def find_block(text: str, subject_local: str) -> tuple[int, int]:
    start = text.find(f"\n:{subject_local} a ")
    if start == -1:
        raise ValueError(f"Could not find an existing block for :{subject_local}")
    end = text.find("\n\n", start)
    if end == -1:
        end = len(text)
    return start, end


def insert_after_block(text: str, subject_local: str, new_chunk: str) -> str:
    _, end = find_block(text, subject_local)
    tail = text[end:]
    # When the block is last in the file, `end == len(text)` and the head
    # already carries the block's own trailing newline -- strip it so the
    # separator below doesn't produce a double blank line at EOF.
    head = text[:end].rstrip("\n") if not tail else text[:end]
    suffix = "\n" if not tail else ""
    return head + "\n\n" + new_chunk.rstrip("\n") + suffix + tail


def append_object_to_property(text: str, subject_local: str, predicate: str, new_object_local: str) -> str:
    """Best-effort textual patch for the existing SAREF time-series version blocks.

    Handles the two cases seen in pe.ttl/te.ttl today: the predicate already
    has a comma-separated object list ending in ' ;' (append one more
    object), or the predicate is entirely absent from the subject's block
    (insert a new line right before 'tbox:hasArea', which every version
    block today shares). This is pattern-specific to blocks shaped like
    Python's/CPython's, not a general Turtle editor -- an entity being
    seeded for the first time (no prior version block) needs a different
    insertion strategy than this one.
    """
    start, end = find_block(text, subject_local)
    block = text[start:end]

    pred_marker = f"    {predicate} "
    pred_idx = block.find(pred_marker)
    if pred_idx != -1:
        terminator_idx = None
        for terminator in (" ;\n", " .\n", " ;", " ."):
            idx = block.find(terminator, pred_idx)
            if idx != -1 and (terminator_idx is None or idx < terminator_idx):
                terminator_idx = idx
        if terminator_idx is None:
            raise ValueError(f"Could not find a terminator for {predicate} in :{subject_local}'s block")
        new_block = block[:terminator_idx] + f",\n        :{new_object_local}" + block[terminator_idx:]
    else:
        anchor = "    tbox:hasArea"
        anchor_idx = block.find(anchor)
        if anchor_idx == -1:
            raise ValueError(f"Could not find an insertion anchor in :{subject_local}'s block")
        new_block = block[:anchor_idx] + f"    {predicate} :{new_object_local} ;\n" + block[anchor_idx:]

    return text[:start] + new_block + text[end:]


def main() -> None:
    versioning_dir = Path(__file__).resolve().parents[1]
    experiment_dir = versioning_dir.parent
    default_repo_root = experiment_dir.parent

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evidence", required=True, type=Path)
    parser.add_argument("--response", required=True, type=Path)
    parser.add_argument("--response-schema", type=Path, default=versioning_dir / "schemas" / "version-addition-response.schema.json")
    parser.add_argument("--config", type=Path, default=versioning_dir / "state" / "tracked-entities.json")
    parser.add_argument("--repo-root", type=Path, default=default_repo_root)
    parser.add_argument("--out-validation-dir", type=Path, default=experiment_dir / "results" / "versioning" / "validation")
    parser.add_argument("--out-patch-dir", type=Path, default=experiment_dir / "results" / "versioning" / "candidate-patches")
    args = parser.parse_args()

    evidence = read_json(args.evidence)
    response = read_json(args.response)
    schema = read_json(args.response_schema)
    ns = read_json(args.config)["namespaces"]

    report = ValidationReport(evidence["runId"])

    schema_errors = sorted(
        Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(response),
        key=lambda error: list(error.path),
    )
    report.add("response-matches-json-schema", not schema_errors, "; ".join(e.message for e in schema_errors))

    field_errors = check_fields(response, evidence)
    report.add("response-fields-match-evidence", not field_errors, "; ".join(field_errors))

    if not report.passed:
        write_report(report, args.out_validation_dir)
        print(f"[{report.run_id}] FAILED before ontology validation -- see validation report.")
        raise SystemExit(1)

    module_path = args.repo_root / response["targetModule"]
    module_text = module_path.read_text(encoding="utf-8")
    header = extract_prefix_header(module_text)
    candidate = response["candidate"]
    turtle_block = candidate["turtleBlock"]

    try:
        version_chunk, instant_chunk = split_turtle_block(turtle_block)
    except ValueError as exc:
        report.add("turtle-block-has-two-resources", False, str(exc))
        write_report(report, args.out_validation_dir)
        print(f"[{report.run_id}] FAILED -- see validation report.")
        raise SystemExit(1)
    report.add("turtle-block-has-two-resources", True)

    block_graph = Graph()
    try:
        block_graph.parse(data=header + "\n\n" + turtle_block, format="turtle")
        report.add("turtle-block-parses", True)
    except Exception as exc:
        report.add("turtle-block-parses", False, str(exc))
        write_report(report, args.out_validation_dir)
        print(f"[{report.run_id}] FAILED -- see validation report.")
        raise SystemExit(1)

    tbox = ns["tbox"]
    new_iri = URIRef(curie_to_uri(candidate["iri"], ns))
    parent_iri = URIRef(curie_to_uri(response["parentEntity"], ns))
    predecessor_iri = URIRef(curie_to_uri(candidate["predecessor"], ns))
    expected_class = URIRef(tbox + TBOX_VERSION_CLASS[response["entityKind"]])

    report.add(
        "declares-expected-version-class",
        (new_iri, RDF.type, expected_class) in block_graph,
        f"expected {expected_class}",
    )
    report.add(
        "declares-versionOf-parent",
        (new_iri, URIRef(tbox + "versionOf"), parent_iri) in block_graph,
    )
    report.add(
        "declares-versionTag",
        candidate["versionTag"] in obj_values(block_graph, new_iri, URIRef(tbox + "versionTag")),
    )
    report.add(
        "declares-hasPredecessor",
        (new_iri, URIRef(tbox + "hasPredecessor"), predecessor_iri) in block_graph,
    )

    release_dates = [
        str(date_lit)
        for instant in block_graph.objects(new_iri, URIRef(tbox + "releaseDate"))
        for date_lit in block_graph.objects(instant, URIRef(TIME_NS + "inXSDDate"))
    ]
    report.add(
        "release-date-instant-matches-evidence",
        candidate["releaseDate"] in release_dates,
        f"found: {release_dates}",
    )

    if not report.passed:
        write_report(report, args.out_validation_dir)
        print(f"[{report.run_id}] FAILED turtle-block content checks -- see validation report.")
        raise SystemExit(1)

    merged = Graph()
    merged.parse(data=module_text, format="turtle")
    merged.parse(data=header + "\n\n" + turtle_block, format="turtle")
    merged.add((parent_iri, URIRef(tbox + "hasVersion"), new_iri))
    merged.add((predecessor_iri, URIRef(tbox + "hasSuccessor"), new_iri))

    report.add(
        "predecessor-exists-in-module",
        any(merged.triples((predecessor_iri, None, None))),
    )

    siblings = set(merged.subjects(URIRef(tbox + "versionOf"), parent_iri))
    tag_counts: dict[str, int] = {}
    for sibling in siblings:
        for tag in merged.objects(sibling, URIRef(tbox + "versionTag")):
            tag_counts[str(tag)] = tag_counts.get(str(tag), 0) + 1
    report.add(
        "no-duplicate-versionTag-for-parent",
        tag_counts.get(candidate["versionTag"], 0) == 1,
        f"count={tag_counts.get(candidate['versionTag'], 0)}",
    )

    try:
        import owlrl

        owlrl.DeductiveClosure(owlrl.OWLRL_Semantics).expand(merged)
        report.add("owl-consistency-check", True)
    except Exception as exc:
        report.add("owl-consistency-check", False, str(exc))

    if not report.passed:
        write_report(report, args.out_validation_dir)
        print(f"[{report.run_id}] FAILED module-level invariants -- see validation report.")
        raise SystemExit(1)

    parent_local = local_name(response["parentEntity"])
    predecessor_local = local_name(candidate["predecessor"])
    new_local = local_name(candidate["iri"])

    try:
        patched_text = module_text
        patched_text = append_object_to_property(patched_text, parent_local, "tbox:hasVersion", new_local)
        patched_text = append_object_to_property(patched_text, predecessor_local, "tbox:hasSuccessor", new_local)
        patched_text = insert_after_block(patched_text, predecessor_local, version_chunk)
        patched_text = insert_after_block(patched_text, f"{predecessor_local}_release", instant_chunk)
        Graph().parse(data=patched_text, format="turtle")
        report.add("patched-module-still-parses", True)
    except Exception as exc:
        report.add("patch-construction", False, str(exc))
        write_report(report, args.out_validation_dir)
        print(f"[{report.run_id}] FAILED to construct a reviewable patch -- see validation report.")
        raise SystemExit(1)

    write_report(report, args.out_validation_dir)

    args.out_patch_dir.mkdir(parents=True, exist_ok=True)
    module_rel = response["targetModule"]
    patched_path = args.out_patch_dir / f"{report.run_id}-{Path(module_rel).name}"
    patched_path.write_text(patched_text, encoding="utf-8")

    diff_path = args.out_patch_dir / f"{report.run_id}.diff"
    diff = difflib.unified_diff(
        module_text.splitlines(keepends=True),
        patched_text.splitlines(keepends=True),
        fromfile=module_rel,
        tofile=f"{module_rel} (candidate: {report.run_id})",
    )
    diff_path.write_text("".join(diff), encoding="utf-8")

    notes_path = args.out_patch_dir / f"{report.run_id}.md"
    notes_path.write_text(
        f"# Candidate: {response['parentEntity']} {response['version']}\n\n"
        f"- Target module: `{module_rel}`\n"
        f"- Predecessor: `{candidate['predecessor']}`\n"
        f"- Release date: {candidate['releaseDate']}\n"
        f"- Official source: {candidate['officialSource']}\n\n"
        f"## LLM rationale\n\n{response['rationale']}\n\n"
        f"## Validation\n\nAll {len(report.checks)} checks passed -- "
        f"see `{report.run_id}.json` for the full report.\n\n"
        f"This is a candidate for human review, not a merged change. "
        f"See `{report.run_id}.diff` for the exact patch.\n",
        encoding="utf-8",
    )

    print(f"[{report.run_id}] PASSED all checks.")
    print(f"  patched module -> {patched_path}")
    print(f"  diff           -> {diff_path}")
    print(f"  review notes   -> {notes_path}")


if __name__ == "__main__":
    main()
