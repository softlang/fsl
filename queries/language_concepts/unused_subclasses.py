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
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
PREFIX tbox: <http://www.softlang.org/ontologies/tbox#>
PREFIX ce: <http://www.softlang.org/ontologies/ce#>

SELECT DISTINCT ?sc
WHERE {
  ?sc rdfs:subClassOf+ ce:LanguageConcept .
  FILTER NOT EXISTS {
    {
      # ?sc is used as object, e.g. ?x rdf:type ?sc
      ?s ?p ?sc .
    }
    UNION
    {
      # ?sc is used as subject in non-ontological assertions
      ?sc ?p ?o .
      FILTER(?p != rdf:type)
      FILTER(?p != rdfs:subClassOf)
      FILTER(?p != rdfs:label)
      FILTER(?p != rdfs:comment)
      FILTER(?p != foaf:isPrimaryTopicOf)
      FILTER(?p != foaf:page)
    }
  }
}
ORDER BY ?sc
"""

# Reporting query result
for row in g.query(query):
    print(row['sc'])
