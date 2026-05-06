from pathlib import Path
from rdflib import Graph

# Parse all Turtle files of the ontology
ttl_dir = Path("../../ontologies")
ttl_files = sorted(ttl_dir.glob("*.ttl"))
g = Graph()
for ttl in ttl_files:
    g.parse(ttl, format="turtle")

# Query of interest
query = """
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX tbox: <http://www.softlang.org/ontologies/tbox#>
PREFIX ce: <http://www.softlang.org/ontologies/ce#>

SELECT
  DISTINCT ?sc
WHERE {
  ?sc rdfs:subClassOf+ ce:LanguageConcept .
}
ORDER BY ?sc
"""

# Reporting query result
for row in g.query(query):
    print(row['sc'])
