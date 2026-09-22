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

def fsl_prefixed_name(graph, resource):
    value = str(resource)

    # Match longer namespaces first so the general fsl: namespace does not
    # hide a more specific namespace such as le: or tbox:.
    for prefix, namespace in sorted(
        fsl_prefixes_dict.items(),
        key=lambda item: len(item[1]),
        reverse=True,
    ):
        if value.startswith(namespace):
            return f"{prefix}:{value[len(namespace):]}"

    # Preserve any additional namespace binding supplied by the graph. If no
    # binding exists, the full IRI remains available both here and in "iri".
    try:
        prefix, _, local = graph.compute_qname(resource, generate=False)
        return f"{prefix}:{local}"
    except (KeyError, ValueError):
        return value
