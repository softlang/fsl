import argparse
import json
import urllib.request
import urllib.error
from datetime import date, datetime
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker
from rdflib import Graph, Namespace

TIME = Namespace("http://www.w3.org/2006/time#")

FEED_FETCHERS = {}


def feed_fetcher(name):
    def register(fn):
        FEED_FETCHERS[name] = fn
        return fn
    return register


@feed_fetcher("endoflife")
def fetch_endoflife(product: str) -> list[dict]:
    url = f"https://endoflife.date/api/{product}.json"
    request = urllib.request.Request(url, headers={"User-Agent": "fsl-version-detector/1.0"})
    with urllib.request.urlopen(request, timeout=15) as response:
        data = json.load(response)
    return [{"cycle": entry["cycle"], "releaseDate": entry["releaseDate"]} for entry in data]


def read_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def version_key(tag: str) -> tuple:
    parts = []
    for chunk in tag.replace("-", ".").split("."):
        digits = "".join(ch for ch in chunk if ch.isdigit())
        parts.append(int(digits) if digits else 0)
    return tuple(parts)


def existing_versions(repo_root: Path, module: str, parent_curie: str, ns: dict) -> dict:
    prefix, local = parent_curie.split(":", 1)
    parent_iri = ns[prefix] + local

    g = Graph()
    g.parse(repo_root / module, format="turtle")

    query = """
    PREFIX tbox: <%s>
    PREFIX time: <%s>
    SELECT ?v ?tag ?dateLit WHERE {
        ?v tbox:versionOf <%s> ;
           tbox:versionTag ?tag .
        OPTIONAL { ?v tbox:releaseDate ?inst . ?inst time:inXSDDate ?dateLit . }
    }
    """ % (ns["tbox"], TIME, parent_iri)

    result = {}
    for row in g.query(query):
        tag = str(row.tag)
        result[tag] = {
            "iri": to_curie(str(row.v), ns),
            "releaseDate": str(row.dateLit) if row.dateLit is not None else None,
        }
    return result


def to_curie(iri: str, ns: dict) -> str:
    for prefix, base in ns.items():
        if iri.startswith(base):
            return f"{prefix}:{iri[len(base):]}"
    return iri


def synthesize_iri(parent_curie: str, tag: str) -> str:
    prefix, local = parent_curie.split(":", 1)
    safe_tag = tag.replace(".", "_").replace("-", "_")
    return f"{prefix}:{local}_{safe_tag}"


def build_candidate(entity: dict, tag: str, feed_entry: dict, predecessor_iri: str, today: str) -> dict:
    prefix, local = entity["parentEntity"].split(":", 1)
    version_nodot = tag.replace(".", "") + "0"
    return {
        "runId": f"{local.lower()}-{tag}",
        "parentEntity": entity["parentEntity"],
        "entityKind": entity["entityKind"],
        "targetModule": entity["targetModule"],
        "version": tag,
        "releaseDate": feed_entry["releaseDate"],
        "predecessor": predecessor_iri,
        "officialSource": entity["officialSourceTemplate"].format(version_nodot=version_nodot),
        "evidenceRetrievedAt": today,
        "notes": (
            f"Auto-detected via {entity['feed']['type']} feed on {today}. "
            "Predecessor and official source URL were inferred by convention, "
            "not confirmed against the source. Verify before use as LLM input."
        ),
    }


def validate_candidate(candidate: dict, schema_path: Path) -> list[str]:
    schema = read_json(schema_path)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    return [error.message for error in validator.iter_errors(candidate)]


def process_entity(entity: dict, repo_root: Path, ns: dict, today: str, include_backfill: bool = False) -> dict:
    parent = entity["parentEntity"]
    feed_type = entity["feed"]["type"]
    if feed_type not in FEED_FETCHERS:
        return {"parentEntity": parent, "status": "error", "detail": f"no fetcher for feed type '{feed_type}'"}

    try:
        feed_entries = FEED_FETCHERS[feed_type](entity["feed"]["product"])
    except (urllib.error.URLError, TimeoutError, ValueError) as exc:
        return {"parentEntity": parent, "status": "error", "detail": f"feed fetch failed: {exc}"}

    existing = existing_versions(repo_root, entity["targetModule"], parent, ns)
    feed_map = {e["cycle"]: e for e in feed_entries}
    known_tags = set(existing)

    if include_backfill:
        candidate_tags = sorted((t for t in feed_map if t not in known_tags), key=version_key)
    else:
        newest_known = max((version_key(t) for t in known_tags), default=None)
        candidate_tags = sorted(
            (t for t in feed_map if t not in known_tags and (newest_known is None or version_key(t) > newest_known)),
            key=version_key,
        )

    if not candidate_tags:
        return {"parentEntity": parent, "status": "no-change", "candidates": []}

    timeline = sorted(known_tags | set(candidate_tags), key=version_key)
    candidates = []
    for tag in candidate_tags:
        idx = timeline.index(tag)
        predecessor_tag = timeline[idx - 1] if idx > 0 else None
        if predecessor_tag is None:
            candidates.append({"version": tag, "status": "needs-review", "detail": "no predecessor found in FSL or feed"})
            continue
        predecessor_iri = existing[predecessor_tag]["iri"] if predecessor_tag in existing else synthesize_iri(parent, predecessor_tag)
        candidate = build_candidate(entity, tag, feed_map[tag], predecessor_iri, today)
        candidates.append({"version": tag, "status": "candidate", "record": candidate})

    return {"parentEntity": parent, "status": "candidates-found", "candidates": candidates}


def main() -> None:
    default_repo_root = Path(__file__).resolve().parents[3]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=Path(__file__).resolve().parent.parent / "state" / "tracked-entities.json")
    parser.add_argument("--schema", type=Path, default=Path(__file__).resolve().parent.parent / "src" / "release-evidence.schema.json")
    parser.add_argument("--repo-root", type=Path, default=default_repo_root)
    parser.add_argument("--out-dir", type=Path, default=Path(__file__).resolve().parents[2] / "results" / "versioning" / "detected")
    parser.add_argument("--entity", default=None, help="Only process entities whose parentEntity contains this substring")
    parser.add_argument("--dry-run", action="store_true", help="Print candidates without writing files")
    parser.add_argument("--include-backfill", action="store_true",
                         help="Also report releases older than FSL's newest tracked version for that entity "
                              "(FSL tracks a curated sample, so this is usually noise -- off by default)")
    args = parser.parse_args()

    config = read_json(args.config)
    ns = config["namespaces"]
    entities = config["entities"]
    if args.entity:
        entities = [e for e in entities if args.entity in e["parentEntity"]]

    today = date.today().isoformat()
    had_error = False
    written = 0

    for entity in entities:
        result = process_entity(entity, args.repo_root, ns, today, include_backfill=args.include_backfill)
        print(f"[{result['status']}] {result['parentEntity']}")

        if result["status"] == "error":
            print(f"    {result['detail']}")
            had_error = True
            continue

        for item in result.get("candidates", []):
            if item["status"] == "needs-review":
                print(f"    {item['version']}: needs-review -- {item['detail']}")
                continue

            record = item["record"]
            errors = validate_candidate(record, args.schema)
            if errors:
                print(f"    {item['version']}: schema validation failed -- {'; '.join(errors)}")
                had_error = True
                continue

            print(f"    {item['version']}: candidate (predecessor {record['predecessor']}, released {record['releaseDate']})")
            if not args.dry_run:
                args.out_dir.mkdir(parents=True, exist_ok=True)
                out_path = args.out_dir / f"{record['runId']}.json"
                out_path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
                print(f"      -> wrote {out_path.relative_to(args.repo_root)}")
                written += 1

    print(f"\n{written} candidate evidence file(s) written." if not args.dry_run else "\nDry run -- no files written.")
    if had_error:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
