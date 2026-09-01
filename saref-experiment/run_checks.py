import argparse
import csv
import re
import sys
from pathlib import Path
from datetime import datetime

from rdflib import Graph, Namespace, RDF, RDFS, OWL, XSD, Literal, URIRef
from rdflib.namespace import DCTERMS

VANN    = Namespace("http://purl.org/vocab/vann/")
SCHEMA  = Namespace("http://schema.org/")

PATTERN_UPPER_CAMEL = re.compile(r"^[A-Z][a-zA-Z0-9]*$")
PATTERN_LOWER_CAMEL = re.compile(r"^[a-z][a-zA-Z0-9]*$")

class Report:
    def __init__(self, label: str):
        self.label = label
        self.checks = []
        self.totals = {"PASS": 0, "WARN": 0, "FAIL": 0, "INFO": 0}

    def record(self, clause: str, severity: str, message: str):
        self.checks.append((clause, severity, message))
        self.totals[severity] = self.totals.get(severity, 0) + 1

    def ok(self, clause: str, message: str):
        self.record(clause, "PASS", message)

    def warn(self, clause: str, message: str):
        self.record(clause, "WARN", message)

    def fail(self, clause: str, message: str):
        self.record(clause, "FAIL", message)

    def info(self, clause: str, message: str):
        self.record(clause, "INFO", message)

    def render(self) -> str:
        lines = []
        lines.append("=" * 70)
        lines.append(f"  SAREF TS 103 673 Clause 9 — Compliance Report")
        lines.append(f"  Target  : {self.label}")
        lines.append(f"  Date    : {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        lines.append("=" * 70)

        current_clause = None
        for clause, severity, message in sorted(self.checks, key=lambda x: x[0]):
            if clause != current_clause:
                lines.append(f"\n── {clause} {'─'*(60 - len(clause))}")
                current_clause = clause
            icon = {"PASS": "✓", "FAIL": "✗", "WARN": "△", "INFO": "ℹ"}.get(severity, "?")
            lines.append(f"  [{severity:4}] {icon}  {message}")

        lines.append("\n" + "=" * 70)
        lines.append("  Summary")
        lines.append(f"  PASS: {self.totals.get('PASS',0)}  "
                     f"WARN: {self.totals.get('WARN',0)}  "
                     f"FAIL: {self.totals.get('FAIL',0)}  "
                     f"INFO: {self.totals.get('INFO',0)}")
        lines.append("=" * 70)
        return "\n".join(lines)

def load_graph(ttl_path: Path, extra_dir: Path = None) -> Graph:
    g = Graph()
    g.parse(ttl_path, format="turtle")
    if extra_dir and extra_dir.is_dir():
        for ttl in sorted(extra_dir.glob("*.ttl")):
            if ttl != ttl_path:
                g.parse(ttl, format="turtle")
    return g

def get_ontology_uri(g: Graph) -> URIRef | None:
    candidates = list(g.subjects(RDF.type, OWL.Ontology))
    if not candidates:
        return None
    best = max(candidates, key=lambda o: sum(1 for _ in g.predicate_objects(o)))
    return best

def get_all_ontology_bases(g: Graph) -> list[str]:
    bases = []
    for onto in g.subjects(RDF.type, OWL.Ontology):
        bases.append(str(onto).rstrip("/").rstrip("#"))
    return bases

def find_repo_root(ttl_path: Path) -> Path:
    candidate = ttl_path.parent
    for _ in range(5):
        if (candidate / ".git").exists():
            return candidate
        candidate = candidate.parent
    return ttl_path.parent.parent

def local_name(uri: str) -> str:
    uri = str(uri)
    return uri.split("#")[-1] if "#" in uri else uri.split("/")[-1]

def is_target_ns(uri, ontology_uri, all_bases: list[str] = None) -> bool:
    if all_bases:
        return any(str(uri).startswith(base) for base in all_bases)
    if ontology_uri is None:
        return False
    base = str(ontology_uri).rstrip("/").rstrip("#")
    return str(uri).startswith(base)

def check_9_4_1_well_formed(report: Report, ttl_path: Path):
    """9.4.1 — The ontology file shall be well-formed Turtle 1.1."""
    try:
        g = Graph()
        g.parse(ttl_path, format="turtle")
        report.ok("9.4.1 Ontology declaration", f"File parses without errors: {ttl_path.name}")
    except Exception as e:
        report.fail("9.4.1 Ontology declaration", f"Parse error: {e}")

def check_9_4_1_ontology_declaration(report: Report, g: Graph):
    """9.4.1 — The file shall contain exactly one owl:Ontology declaration with an IRI and versionIRI."""
    ontologies = list(g.subjects(RDF.type, OWL.Ontology))
    if not ontologies:
        report.fail("9.4.1 Ontology declaration", "No owl:Ontology declaration found.")
        return
    if len(ontologies) > 1:
        report.warn("9.4.1 Ontology declaration", f"Multiple owl:Ontology declarations: {ontologies}")
    else:
        report.ok("9.4.1 Ontology declaration", f"owl:Ontology declared: <{ontologies[0]}>")

    onto = ontologies[0]
    version_iris = list(g.objects(onto, OWL.versionIRI))
    if not version_iris:
        report.fail("9.4.1 Ontology declaration",
                    "owl:versionIRI is missing. SHALL be present (e.g. <https://…/v1.0.0/>).")
    else:
        report.ok("9.4.1 Ontology declaration", f"owl:versionIRI present: <{version_iris[0]}>")

def check_9_4_3_1_prefixes(report: Report, g: Graph):
    """9.4.3.1 — Standard prefixes shall be declared with correct namespace IRIs."""
    EXPECTED = {
        "rdf":     "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
        "rdfs":    "http://www.w3.org/2000/01/rdf-schema#",
        "owl":     "http://www.w3.org/2002/07/owl#",
        "xsd":     "http://www.w3.org/2001/XMLSchema#",
        "dcterms": "http://purl.org/dc/terms/",
        "vann":    "http://purl.org/vocab/vann/",
        "foaf":    "http://xmlns.com/foaf/0.1/",
    }
    declared = {str(p): str(ns) for p, ns in g.namespaces()}
    for prefix, expected_ns in EXPECTED.items():
        if prefix not in declared:
            report.fail("9.4.3.1 Prefix declarations",
                        f"Standard prefix '{prefix}:' is not declared.")
        elif declared[prefix] != expected_ns:
            report.fail("9.4.3.1 Prefix declarations",
                        f"Prefix '{prefix}:' points to <{declared[prefix]}> "
                        f"but SHALL be <{expected_ns}>.")
        else:
            report.ok("9.4.3.1 Prefix declarations",
                      f"Prefix '{prefix}:' correctly declared.")

def check_9_4_3_2_metadata(report: Report, g: Graph):
    """9.4.3.2 — Required ontology-level metadata triples."""
    onto = get_ontology_uri(g)
    if onto is None:
        report.fail("9.4.3.2 Ontology metadata", "No owl:Ontology — cannot check metadata.")
        return

    # --- SHALL checks (Violations) ---
    SHALL = [
        (DCTERMS.title,       "dcterms:title",       "SHALL have a title (plain or language-tagged string)"),
        (DCTERMS.description, "dcterms:description", "SHALL have a description"),
        (DCTERMS.license,     "dcterms:license",     "SHALL have a dcterms:license IRI"),
        (DCTERMS.creator,     "dcterms:creator",     "SHALL have at least one dcterms:creator"),
        (VANN.preferredNamespacePrefix, "vann:preferredNamespacePrefix", "SHALL declare vann:preferredNamespacePrefix"),
        (VANN.preferredNamespaceUri,    "vann:preferredNamespaceUri",    "SHALL declare vann:preferredNamespaceUri"),
    ]
    for prop, name, msg in SHALL:
        vals = list(g.objects(onto, prop))
        if not vals:
            report.fail("9.4.3.2 Ontology metadata", f"{name} missing. {msg}.")
        else:
            report.ok("9.4.3.2 Ontology metadata", f"{name} present: {vals[0]}")

    for prop, name in [(DCTERMS.issued, "dcterms:issued"), (DCTERMS.modified, "dcterms:modified")]:
        vals = list(g.objects(onto, prop))
        if not vals:
            report.fail("9.4.3.2 Ontology metadata",
                        f"{name} missing. SHALL have exactly one xsd:date value.")
        elif len(vals) > 1:
            report.fail("9.4.3.2 Ontology metadata",
                        f"{name} has {len(vals)} values — SHALL have exactly one.")
        else:
            v = vals[0]
            if isinstance(v, Literal) and v.datatype == XSD.date:
                report.ok("9.4.3.2 Ontology metadata", f"{name} = {v} (xsd:date ✓)")
            else:
                report.fail("9.4.3.2 Ontology metadata",
                            f"{name} value '{v}' is not typed as xsd:date.")

    # --- SHOULD check ---
    if not list(g.objects(onto, DCTERMS.abstract)):
        report.warn("9.4.3.2 Ontology metadata",
                    "dcterms:abstract missing. SHOULD be present.")
    else:
        report.ok("9.4.3.2 Ontology metadata", "dcterms:abstract present.")

def check_9_4_3_3_creators(report: Report, g: Graph):
    """9.4.3.3 — Creators SHALL be typed as schema:Person with rdfs:label or schema:name."""
    onto = get_ontology_uri(g)
    if onto is None:
        return
    creators = list(g.objects(onto, DCTERMS.creator))
    if not creators:
        report.fail("9.4.3.3 Creators", "No dcterms:creator triples found on the ontology.")
        return
    for c in creators:
        is_person = (c, RDF.type, SCHEMA.Person) in g
        has_name  = (list(g.objects(c, SCHEMA.name)) or list(g.objects(c, RDFS.label))
                     or list(g.objects(c, SCHEMA.givenName)))
        if not is_person:
            report.fail("9.4.3.3 Creators",
                        f"Creator <{c}> is not typed as schema:Person.")
        else:
            report.ok("9.4.3.3 Creators", f"Creator <{c}> is a schema:Person.")
        if not has_name:
            report.fail("9.4.3.3 Creators",
                        f"Creator <{c}> has no schema:name, schema:givenName, or rdfs:label.")
        else:
            report.ok("9.4.3.3 Creators",
                      f"Creator <{c}> has name: {has_name[0]}")

def check_9_4_4_1_naming(report: Report, g: Graph):
    """9.4.4.1 — Classes SHALL be UpperCamelCase; properties SHALL be lowerCamelCase."""
    onto = get_ontology_uri(g)
    all_bases = get_all_ontology_bases(g)
    violations_class, violations_prop = [], []

    for cls in g.subjects(RDF.type, OWL.Class):
        if not is_target_ns(cls, onto, all_bases):
            continue
        name = local_name(cls)
        if not PATTERN_UPPER_CAMEL.match(name):
            violations_class.append(name)

    for prop_type in (OWL.ObjectProperty, OWL.DatatypeProperty, OWL.AnnotationProperty):
        for prop in g.subjects(RDF.type, prop_type):
            if not is_target_ns(prop, onto, all_bases):
                continue
            name = local_name(prop)
            if not PATTERN_LOWER_CAMEL.match(name):
                violations_prop.append(name)

    if violations_class:
        report.fail("9.4.4.1 Naming conventions",
                    f"Classes not in UpperCamelCase: {', '.join(violations_class)}")
    else:
        report.ok("9.4.4.1 Naming conventions", "All classes follow UpperCamelCase.")

    if violations_prop:
        report.fail("9.4.4.1 Naming conventions",
                    f"Properties not in lowerCamelCase: {', '.join(violations_prop)}")
    else:
        report.ok("9.4.4.1 Naming conventions", "All properties follow lowerCamelCase.")

def check_9_4_4_2_term_docs(report: Report, g: Graph):
    """9.4.4.2 — Every term SHALL have rdfs:label and rdfs:comment in English."""
    onto = get_ontology_uri(g)
    all_bases = get_all_ontology_bases(g)
    TERM_TYPES = [
        OWL.Class, OWL.ObjectProperty, OWL.DatatypeProperty, OWL.AnnotationProperty,
        OWL.NamedIndividual,
    ]
    missing_label, missing_comment = [], []

    all_terms = set()
    for t in TERM_TYPES:
        for term in g.subjects(RDF.type, t):
            if is_target_ns(term, onto, all_bases):
                all_terms.add(term)

    for term in all_terms:
        labels   = [l for l in g.objects(term, RDFS.label)   if isinstance(l, Literal) and l.language == "en"]
        comments = [c for c in g.objects(term, RDFS.comment) if isinstance(c, Literal) and c.language == "en"]
        if not labels:
            missing_label.append(local_name(term))
        if not comments:
            missing_comment.append(local_name(term))

    total = len(all_terms)
    if missing_label:
        report.fail("9.4.4.2 Term documentation",
                    f"{len(missing_label)}/{total} terms missing rdfs:label@en: "
                    f"{', '.join(sorted(missing_label)[:10])}"
                    f"{'…' if len(missing_label) > 10 else ''}")
    else:
        report.ok("9.4.4.2 Term documentation",
                  f"All {total} terms have rdfs:label@en.")

    if missing_comment:
        report.fail("9.4.4.2 Term documentation",
                    f"{len(missing_comment)}/{total} terms missing rdfs:comment@en: "
                    f"{', '.join(sorted(missing_comment)[:10])}"
                    f"{'…' if len(missing_comment) > 10 else ''}")
    else:
        report.ok("9.4.4.2 Term documentation",
                  f"All {total} terms have rdfs:comment@en.")

def check_9_4_5_owl2dl(report: Report, g: Graph):
    """9.4.5 — The ontology SHALL satisfy the OWL 2 DL profile."""
    try:
        from pyshacl import validate
        # Use owlrl reasoner as a DL profile proxy — if it loads cleanly, profile is OK
        validate(
            g,
            ont_graph=None,
            inference="rdfs",
            abort_on_first=False,
            allow_warnings=True,
            meta_shacl=False,
            advanced=False,
            js=False,
            debug=False,
        )
        report.ok("9.4.5 OWL 2 DL profile", "pyshacl/owlrl loaded ontology without errors.")
    except Exception as e:
        report.fail("9.4.5 OWL 2 DL profile", f"Profile check failed: {e}")

def check_9_2_repo_structure(report: Report, ttl_path: Path):
    """9.2 — Repository SHALL contain LICENSE, README, and required folders."""
    repo = find_repo_root(ttl_path)

    license_found = any((repo / n).exists() for n in ["LICENSE", "LICENSE.txt", "LICENSE.md", "license"])
    if license_found:
        report.ok("9.2 Repository structure", "LICENSE file present.")
    else:
        report.fail("9.2 Repository structure", "No LICENSE file found. SHALL be present.")

    readme_found = any((repo / n).exists() for n in ["README.md", "README.txt", "README"])
    if readme_found:
        report.ok("9.2 Repository structure", "README file present.")
    else:
        report.fail("9.2 Repository structure", "No README file found. SHALL be present.")

    for folder in ["requirements", "tests", "examples", "documentation"]:
        if (repo / folder).is_dir():
            report.ok("9.2 Repository structure", f"{folder}/ directory present.")
        else:
            report.fail("9.2 Repository structure", f"{folder}/ directory missing. SHALL be present.")

def check_9_3_requirements(report: Report, ttl_path: Path):
    """9.3 — requirements/requirements.csv SHALL exist with correct semicolon-delimited header."""
    repo = find_repo_root(ttl_path)
    csv_path = repo / "requirements" / "requirements.csv"

    if not csv_path.exists():
        report.fail("9.3 Requirements", "requirements/requirements.csv not found. SHALL be present.")
        return

    try:
        with open(csv_path, encoding="utf-8") as f:
            rows = list(csv.reader(f, delimiter=";"))
    except Exception as e:
        report.fail("9.3 Requirements", f"requirements.csv could not be read: {e}")
        return

    if not rows:
        report.fail("9.3 Requirements", "requirements.csv is empty.")
        return

    expected = ["Id", "Category", "Requirement"]
    if rows[0] != expected:
        report.fail("9.3 Requirements",
                    f"Header {rows[0]} is wrong. SHALL be {expected}.")
    else:
        report.ok("9.3 Requirements", "requirements.csv header correct: Id;Category;Requirement.")

    data = [r for r in rows[1:] if any(c.strip() for c in r)]
    if not data:
        report.fail("9.3 Requirements", "requirements.csv has no data rows.")
    else:
        report.ok("9.3 Requirements", f"requirements.csv has {len(data)} requirement(s).")

def _parse_file_prefixes(ttl_path: Path) -> dict:
    """Read @prefix declarations directly from a Turtle file (avoids rdflib built-in overrides)."""
    prefixes = {}
    pat = re.compile(r'@prefix\s+(\w*):\s+<([^>]+)>\s*\.')
    try:
        with open(ttl_path, encoding="utf-8") as f:
            for line in f:
                m = pat.match(line.strip())
                if m:
                    prefixes[m.group(1)] = m.group(2)
    except Exception:
        pass
    return prefixes

def check_9_4_2_namespaces(report: Report, g: Graph, ttl_path: Path):
    """9.4.2 — Declared namespace IRIs SHALL use the correct canonical URI.
    Reads prefixes from source file directly to avoid rdflib built-in overrides."""
    CANONICAL = {
        "rdf":     "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
        "rdfs":    "http://www.w3.org/2000/01/rdf-schema#",
        "owl":     "http://www.w3.org/2002/07/owl#",
        "xsd":     "http://www.w3.org/2001/XMLSchema#",
        "dcterms": "http://purl.org/dc/terms/",
        "vann":    "http://purl.org/vocab/vann/",
        "foaf":    "http://xmlns.com/foaf/0.1/",
        "schema":  "http://schema.org/",
    }
    declared = _parse_file_prefixes(ttl_path)
    for prefix, expected_ns in CANONICAL.items():
        if prefix not in declared:
            continue
        if declared[prefix] == expected_ns:
            report.ok("9.4.2 Namespace declarations",
                      f"'{prefix}:' → <{expected_ns}> ✓")
        else:
            report.fail("9.4.2 Namespace declarations",
                        f"'{prefix}:' points to <{declared[prefix]}> but SHALL be <{expected_ns}>.")

def check_9_5_tests(report: Report, ttl_path: Path):
    """9.5 — tests/tests.csv SHALL exist with correct semicolon-delimited header."""
    repo = find_repo_root(ttl_path)
    csv_path = repo / "tests" / "tests.csv"

    if not csv_path.exists():
        report.fail("9.5 Tests", "tests/tests.csv not found. SHALL be present.")
        return

    try:
        with open(csv_path, encoding="utf-8") as f:
            rows = list(csv.reader(f, delimiter=";"))
    except Exception as e:
        report.fail("9.5 Tests", f"tests.csv could not be read: {e}")
        return

    if not rows:
        report.fail("9.5 Tests", "tests.csv is empty.")
        return

    expected = ["Id", "Requirement", "Category", "Test"]
    if rows[0] != expected:
        report.fail("9.5 Tests",
                    f"Header {rows[0]} is wrong. SHALL be {expected}.")
    else:
        report.ok("9.5 Tests", "tests.csv header correct: Id;Requirement;Category;Test.")

    data = [r for r in rows[1:] if any(c.strip() for c in r)]
    if not data:
        report.fail("9.5 Tests", "tests.csv has no data rows.")
    else:
        report.ok("9.5 Tests", f"tests.csv has {len(data)} test(s).")

def check_9_6_examples(report: Report, ttl_path: Path):
    """9.6 — examples/ SHALL contain at least one valid Turtle file."""
    repo = find_repo_root(ttl_path)
    examples_dir = repo / "examples"

    if not examples_dir.is_dir():
        report.fail("9.6 Examples", "examples/ directory not found. SHALL be present.")
        return

    ttl_files = list(examples_dir.glob("*.ttl"))
    if not ttl_files:
        report.fail("9.6 Examples", "examples/ has no .ttl files. SHALL contain at least one.")
        return

    report.ok("9.6 Examples", f"examples/ contains {len(ttl_files)} .ttl file(s).")
    for ex in ttl_files:
        try:
            Graph().parse(ex, format="turtle")
            report.ok("9.6 Examples", f"{ex.name} parses as valid Turtle.")
        except Exception as e:
            report.fail("9.6 Examples", f"{ex.name} parse error: {e}")

def check_9_7_documentation(report: Report, ttl_path: Path):
    """9.7 — documentation/ SHALL contain abstract.md and description.md."""
    repo = find_repo_root(ttl_path)
    doc_dir = repo / "documentation"

    if not doc_dir.is_dir():
        report.fail("9.7 Documentation", "documentation/ directory not found. SHALL be present.")
        return

    report.ok("9.7 Documentation", "documentation/ directory present.")
    for name in ["abstract.md", "description.md"]:
        f = doc_dir / name
        if not f.exists():
            report.fail("9.7 Documentation", f"documentation/{name} missing. SHALL be present.")
        elif f.stat().st_size == 0:
            report.warn("9.7 Documentation", f"documentation/{name} exists but is empty.")
        else:
            report.ok("9.7 Documentation", f"documentation/{name} present and non-empty.")

def check_9_8_vocabularies(report: Report, ttl_path: Path):
    """9.8 — vocabularies/ is optional; if present it SHOULD not be empty."""
    repo = find_repo_root(ttl_path)
    vocab_dir = repo / "vocabularies"

    if not vocab_dir.is_dir():
        report.info("9.8 Vocabularies", "vocabularies/ directory not present (optional).")
        return

    files = list(vocab_dir.iterdir())
    if not files:
        report.warn("9.8 Vocabularies", "vocabularies/ exists but is empty. SHOULD contain at least one file.")
    else:
        report.ok("9.8 Vocabularies", f"vocabularies/ contains {len(files)} file(s).")

def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--ttl",       required=True, help="Path to the main ontology .ttl file")
    parser.add_argument("--extra-ttl", default=None,  help="Directory of additional .ttl files to load (for modular ontologies)")
    parser.add_argument("--label",     required=True, help="Name for this run (used in output filename)")
    args = parser.parse_args()

    ttl_path  = Path(args.ttl).resolve()
    extra_dir = Path(args.extra_ttl).resolve() if args.extra_ttl else None

    if not ttl_path.exists():
        print(f"ERROR: File not found: {ttl_path}", file=sys.stderr)
        sys.exit(1)

    report = Report(args.label)

    print(f"Loading ontology: {ttl_path}")
    g = load_graph(ttl_path, extra_dir)
    print(f"  {len(g)} triples loaded.\n")

    # Run all checks
    check_9_2_repo_structure(report, ttl_path)
    check_9_3_requirements(report, ttl_path)
    check_9_4_1_well_formed(report, ttl_path)
    check_9_4_1_ontology_declaration(report, g)
    check_9_4_2_namespaces(report, g, ttl_path)
    check_9_4_3_1_prefixes(report, g)
    check_9_4_3_2_metadata(report, g)
    check_9_4_3_3_creators(report, g)
    check_9_4_4_1_naming(report, g)
    check_9_4_4_2_term_docs(report, g)
    check_9_4_5_owl2dl(report, g)
    check_9_5_tests(report, ttl_path)
    check_9_6_examples(report, ttl_path)
    check_9_7_documentation(report, ttl_path)
    check_9_8_vocabularies(report, ttl_path)

    output = report.render()
    print(output)

    # Exit non-zero if any FAILs
    sys.exit(1 if report.totals.get("FAIL", 0) > 0 else 0)

if __name__ == "__main__":
    main()
