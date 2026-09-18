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

fsl_prefixes = """
PREFIX ae:   <http://www.softlang.org/ontologies/ae#>
PREFIX ce:   <http://www.softlang.org/ontologies/ce#>
PREFIX fe:   <http://www.softlang.org/ontologies/fe#>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
PREFIX fsl:  <http://www.softlang.org/ontologies/>
PREFIX ie:   <http://www.softlang.org/ontologies/ie#>
PREFIX le:   <http://www.softlang.org/ontologies/le#>
PREFIX owl:  <http://www.w3.org/2002/07/owl#>
PREFIX pe:   <http://www.softlang.org/ontologies/pe#>
PREFIX rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX tbox: <http://www.softlang.org/ontologies/tbox#>
PREFIX te:   <http://www.softlang.org/ontologies/te#>
PREFIX xsd:  <http://www.w3.org/2001/XMLSchema#>
"""


def local_name(value):
    if value is None:
        return ""
    text = str(value)
    if "#" in text:
        return text.rsplit("#", 1)[1]
    return text.rstrip("/").rsplit("/", 1)[-1]
