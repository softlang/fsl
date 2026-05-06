from pathlib import Path
from rdflib import Graph
import csv
import pandas as pd
import networkx as nx
from networkx.drawing.nx_agraph import to_agraph

# Let's remove common base URIs.
def strip_base(uri):
    uri = str(uri)
    return uri.removeprefix("http://www.softlang.org/ontologies/")

# Parse all Turtle files of the ontology
ttl_dir = Path("../../ontologies")
ttl_files = sorted(ttl_dir.glob("*.ttl"))
g = Graph()
for ttl in ttl_files:
    g.parse(ttl, format="turtle")

# Query of interest
query = """
PREFIX owl: <http://www.w3.org/2002/07/owl#>

SELECT
  DISTINCT ?o1 ?o2
WHERE {
  ?o1 owl:imports ?o2 .
}
ORDER BY ?o1 ?o2
"""

result = g.query(query)

with open("imports.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    for row in result:
        writer.writerow([strip_base(row['o1']), strip_base(row['o2'])])

df = pd.read_csv("imports.csv", header=None, names=["source", "target"])

G = nx.DiGraph()

for _, row in df.iterrows():
    G.add_edge(row["source"], row["target"])

agraph = to_agraph(G)
agraph.draw("imports.png", prog="dot")
