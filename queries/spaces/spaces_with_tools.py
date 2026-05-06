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
  DISTINCT ?s
WHERE {
  ?s rdf:type tbox:TechnologicalSpace .
  ?t rdf:type tbox:ToolEntity .
  {
    ?s ?from ?t .
  }
  UNION
  {
    ?t ?to ?s .
  }
}
ORDER BY ?s
"""

# Reporting query result
for row in g.query(query):
    print(row['s'])
