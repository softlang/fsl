from pathlib import Path
from rdflib import Graph
import csv
import pandas as pd
import networkx as nx
from networkx.drawing.nx_agraph import to_agraph

# Let's make URIs fully unqualified.
def local_name(value):
    if value is None:
        return ""
    text = str(value)
    if "softlang" in text:
        return text.rsplit("http://www.softlang.org/ontologies/sle/", 1)[1]
    return text

# Parse all Turtle files of the ontology
ttl_dir = Path("../../ontologies/versions/phase2/ontologies")
ttl_files = sorted(ttl_dir.glob("*.ttl"))
g = Graph()
for ttl in ttl_files:
    g.parse(ttl, format="turtle")

seed = [
    "Class",
    "ContextFreeGrammar",
    "ParsingExpressionGrammar",
    "ExtendedBackusNaurForm",
    "RegularGrammar",
    "AttributeGrammar",
    "TermRewritingSystem",
    "LambdaCalculus",
    "UntypedLambdaCalculus",
    "SimplyTypedLambdaCalculus",
    "SystemF",
    "LambdaCube",
    "DenotationalSemantics",
    "OperationalSemantics",
    "AxiomaticSemantics",
    "ProcessCalculus",
    "CommunicatingSequentialProcesses",
    "CalculusOfCommunicatingSystems",
    "UMLStateMachine",
    "HoareLogic",
    "DescriptionLogic",
    "DependencyGrammar"
]
    
# Query of interest
query = """
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>

SELECT
  DISTINCT ?i ?c
WHERE {
  ?i rdf:type ?c .
  FILTER(isIRI(?i))
  FILTER(isIRI(?c))
  FILTER(STRSTARTS(STR(?i), "http://www.softlang.org/ontologies/"))
  FILTER(STRSTARTS(STR(?c), "http://www.softlang.org/ontologies/"))
}
ORDER BY ?i ?c
"""

result = g.query(query)

with open("categorization.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    for row in result:
        writer.writerow([local_name(row['i']), local_name(row['c'])])

df = pd.read_csv("categorization.csv", header=None, names=["source", "target"])

G = nx.DiGraph()

for _, row in df.iterrows():
    G.add_edge(row["source"], row["target"])
    
sources = set(df["source"])
targets = set(df["target"])

G.add_node("Class")

for node in targets:
    G.add_edge(node, "Class")

# To account for late seed-set changes
G.add_edge("DescriptionLogic", "Class")
targets.add("DescriptionLogic")
    
agraph = to_agraph(G)

#agraph.graph_attr.update(
#    rankdir="TB",        # Top -> Bottom
#    size="8.5,11!",      # portrait dimensions
#    ratio="fill",
#    dpi="200"
#)

agraph.graph_attr.update(
    rankdir="LR",        # Left -> Right instead of Top -> Bottom
    size="11,8.5!",      # width,height in inches; ! forces fit
    ratio="fill",        # stretch/fill the requested size
    dpi="200"
)

for node in G.nodes():
    n = agraph.get_node(node)

    if node in sources and node not in targets:
        n.attr["shape"] = "box"       # "from"-only nodes
    elif node in targets and node not in sources:
        n.attr["shape"] = "ellipse"   # "to"-only nodes
    else:
        n.attr["shape"] = "diamond"   # owl:class
    if node not in seed:
        n.attr["penwidth"] = 4
        n.attr["style"] = "filled"
        n.attr["fillcolor"] = "lightblue"

agraph.draw("categorization.png", prog="dot")
