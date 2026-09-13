from pathlib import Path
import csv
from rdflib import Graph
from rdflib.namespace import split_uri

# Parse all Turtle files of the ontology
ttl_dir = Path("../../ontologies")
ttl_files = sorted(ttl_dir.glob("*.ttl"))
g = Graph()
for ttl in ttl_files:
    g.parse(ttl, format="turtle")

# Query taxonomy below EngineeringActivity.
query = """
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX tbox: <http://www.softlang.org/ontologies/tbox#>

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
        _, superclass = split_uri(row["superclass"])
        _, subclass = split_uri(row["subclass"])
        writer.writerow([superclass, subclass])
