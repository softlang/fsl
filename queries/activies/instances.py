from pathlib import Path
import csv
from fsl_utils import fsl_graph, fsl_prefixes_sparql, local_name

# Retrieve the ontology graph
g = fsl_graph()

# Query taxonomy below EngineeringActivity.
query = fsl_prefixes_sparql + """

SELECT DISTINCT ?superclass ?subclass
WHERE {
    ?superclass rdfs:subClassOf* tbox:EngineeringActivity .
    ?subclass rdfs:subClassOf ?superclass .
}
ORDER BY ?superclass ?subclass
"""

# Write taxonomy edges to CSV
output_file = Path("instances.csv")
with output_file.open("w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["Superclass", "Subclass"])
    for row in g.query(query):
        superclass = local_name(row["superclass"])
        subclass = local_name(row["subclass"])
        writer.writerow([superclass, subclass])
