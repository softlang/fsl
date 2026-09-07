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

# Query all direct and transitive instances of SoftwareLanguage
query = """
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX tbox: <http://www.softlang.org/ontologies/tbox#>

SELECT DISTINCT ?language ?classifier
WHERE {
    ?classifier rdfs:subClassOf* tbox:SoftwareLanguage .
    ?language rdf:type ?classifier .
}
ORDER BY ?classifier ?language
"""

# Write query result to CSV
output_file = Path("instances.csv")
with output_file.open("w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["SoftwareLanguage", "Classifier"])
    for row in g.query(query):
        _, language = split_uri(row["language"])
        _, classifier = split_uri(row["classifier"])
        writer.writerow([language, classifier])
