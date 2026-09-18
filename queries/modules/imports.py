import csv
import pandas as pd
import networkx as nx
from networkx.drawing.nx_agraph import to_agraph
from fsl_utils import fsl_graph, fsl_prefixes, local_name

# Retrieve the ontology graph
g = fsl_graph()

# Query of interest
query = fsl_prefixes + """

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
        writer.writerow([local_name(row['o1']), local_name(row['o2'])])

df = pd.read_csv("imports.csv", header=None, names=["source", "target"])

G = nx.DiGraph()

for _, row in df.iterrows():
    G.add_edge(row["source"], row["target"])

agraph = to_agraph(G)
agraph.draw("imports.png", prog="dot")
