import csv
import pandas as pd
import networkx as nx
from networkx.drawing.nx_agraph import to_agraph
from fsl_utils import ONTOLOGIES_DIR, fsl_graph, fsl_prefixes, local_name

# Parse all Turtle files of the ontology
g = fsl_graph(ONTOLOGIES_DIR / "versions/phase2/ontologies")

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
query = fsl_prefixes + """

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
