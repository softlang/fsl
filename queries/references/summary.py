import csv
from rdflib import Graph
from common import fsl_graph, fsl_prefixes, local_name

# Retrieve the ontology graph
g = fsl_graph()

# Query of interest
query = f"""
{fsl_prefixes}
SELECT ?e ?r
WHERE {{
  ?e tbox:hasBibTeX ?r
}}
ORDER BY ?e
"""

result = g.query(query)

# Reporting query result
with open("summary.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["Entity","Reference"])
    for row in result:
        writer.writerow([local_name(row["e"]), row["r"]])
