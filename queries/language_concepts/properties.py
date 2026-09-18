from fsl_utils import fsl_graph, fsl_prefixes

# Retrieve the ontology graph
g = fsl_graph()

# Query of interest
query = fsl_prefixes + """

SELECT DISTINCT ?p
WHERE {
  {
    ?sc rdfs:subClassOf+ tbox:LanguageConcept .
    ?c rdf:type ?sc .
  }
  UNION
  {
    ?c rdfs:subClassOf+ tbox:LanguageConcept .
  }
  {
    ?c ?p ?o
  }
  UNION
  {
    ?s ?p ?c
  }
  FILTER(?p != rdf:type) 
  FILTER(?p != rdfs:subClassOf)
  FILTER(?p != rdfs:domain)
  FILTER(?p != rdfs:range)
  FILTER(?p != rdfs:label)
  FILTER(?p != rdfs:comment)
  FILTER(?p != foaf:isPrimaryTopicOf)
  FILTER(?p != foaf:page)
}
ORDER BY ?p
"""

# Reporting query result
for row in g.query(query):
    print(row['p'])
