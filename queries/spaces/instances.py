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
PREFIX rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX tbox: <http://www.softlang.org/ontologies/tbox#>

SELECT
  DISTINCT ?i
WHERE {
  ?i rdf:type tbox:TechnologicalSpace .
}
ORDER BY ?i
"""

# Reporting query result
for row in g.query(query):
    print(row['i'])
