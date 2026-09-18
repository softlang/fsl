import csv
import pandas as pd
import networkx as nx
from networkx.drawing.nx_agraph import to_agraph
from fsl_utils import ONTOLOGIES_DIR, fsl_graph, fsl_prefixes, local_name

# Phase 2 graph
g2 = fsl_graph(ONTOLOGIES_DIR / "versions/phase2/ontologies")

# Phase 3 graph
g3 = fsl_graph(ONTOLOGIES_DIR / "versions/phase3/ontologies")
    
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

result2 = g2.query(query)
result3 = g3.query(query)

with open("categorization.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    for row in result2:
        writer.writerow([2, local_name(row['i']), local_name(row['c'])])
    for row in result3:
        writer.writerow([3, local_name(row['i']), local_name(row['c'])])

df = pd.read_csv("categorization.csv", header=None, names=["phase", "source", "target"])

G = nx.DiGraph()

phase2 = set()
for _, row in df.iterrows():
    phase = row["phase"]
    source = row["source"]
    target = row["target"]
    if phase == 2:
        phase2.add(source)
        phase2.add(target)
    G.add_edge(source, target)

sources = set(df["source"])
targets = set(df["target"])

G.add_node("Class")
phase2.add("Class")
for node in targets:
    G.add_edge(node, "Class")

# To account for late seed-set changes
phase2.add("DescriptionLogic")
    
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
    if node not in phase2:
        n.attr["penwidth"] = 4
        n.attr["style"] = "filled"
        n.attr["fillcolor"] = "lightblue"

agraph.draw("categorization.png", prog="dot")
