import csv
import pandas as pd
import networkx as nx
from networkx.drawing.nx_agraph import to_agraph
from fsl_utils import fsl_graph, fsl_prefixes

# Let's remove common base URIs.
def strip_base(uri):
    uri = str(uri)
    return uri.removeprefix("http://www.softlang.org/ontologies/")

# Retrieve the ontology graph
g = fsl_graph()

# Query of interest
query = fsl_prefixes + """

SELECT
  DISTINCT ?pfx1 ?pfx2
WHERE {
  ?s ?_ ?o .
  FILTER(isIRI(?s))
  FILTER(isIRI(?o))
  FILTER(STRSTARTS(STR(?s), "http://www.softlang.org/ontologies/"))
  FILTER(STRSTARTS(STR(?o), "http://www.softlang.org/ontologies/"))
  BIND(STRAFTER(STR(?s), "http://www.softlang.org/ontologies/") AS ?nobase1)
  BIND(STRAFTER(STR(?o), "http://www.softlang.org/ontologies/") AS ?nobase2)
  BIND(STRBEFORE(?nobase1, "#") AS ?pfx1)
  BIND(STRBEFORE(?nobase2, "#") AS ?pfx2)
  FILTER(?pfx1 != "")
  FILTER(?pfx2 != "")
  FILTER(?pfx1 != ?pfx2)
}
ORDER BY ?pfx1 ?pfx2
"""

result = g.query(query)

with open("namespaces.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    for row in result:
        writer.writerow([row['pfx1'], row['pfx2']])

result = g.query(query)

df = pd.read_csv("namespaces.csv", header=None, names=["source", "target"])

G = nx.DiGraph()

for _, row in df.iterrows():
    G.add_edge(row["source"], row["target"])

agraph = to_agraph(G)
agraph.draw("namespaces.png", prog="dot")
