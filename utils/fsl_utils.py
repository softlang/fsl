from pathlib import Path
from rdflib import Graph

def fsl_graph():
    ttl_dir = Path("../../ontologies")
    ttl_files = sorted(ttl_dir.glob("*.ttl"))

    g = Graph()
    for ttl in ttl_files:
        g.parse(ttl, format="turtle")

    return g

fsl_prefixes = """
PREFIX rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX owl:  <http://www.w3.org/2002/07/owl#>
PREFIX tbox: <http://www.softlang.org/ontologies/tbox#>
PREFIX ie:   <http://www.softlang.org/ontologies/ie#>
"""

def local_name(value):
    if value is None:
        return ""
    text = str(value)
    if "#" in text:
        return text.rsplit("#", 1)[1]
    return text
