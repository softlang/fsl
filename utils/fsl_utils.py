import json
from pathlib import Path
from rdflib import Graph

ONTOLOGIES_DIR = Path(__file__).resolve().parents[1] / "ontologies"


def fsl_graph(source=ONTOLOGIES_DIR):
    source = Path(source)
    ttl_files = [source] if source.suffix == ".ttl" else sorted(source.glob("*.ttl"))

    g = Graph()
    for ttl in ttl_files:
        g.parse(ttl, format="turtle")

    return g

# Keep the namespace mapping reusable outside SPARQL queries.
with Path(__file__).with_name("fsl_prefixes.json").open(encoding="utf-8") as prefixes_file:
    fsl_prefixes_dict = json.load(prefixes_file)

fsl_prefixes_sparql = "\n".join(
    f"PREFIX {prefix}: <{namespace}>"
    for prefix, namespace in fsl_prefixes_dict.items()
) + "\n"


def local_name(value):
    if value is None:
        return ""
    text = str(value)
    if "#" in text:
        return text.rsplit("#", 1)[1]
    return text.rstrip("/").rsplit("/", 1)[-1]
