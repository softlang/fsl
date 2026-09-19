from fsl_utils import fsl_graph, fsl_prefixes_sparql

# Retrieve the ontology graph
g = fsl_graph()

# Query of interest
query = fsl_prefixes_sparql + """

SELECT DISTINCT ?sc
WHERE {
  ?sc rdfs:subClassOf tbox:EngineeringActivity .
  {
    # ?sc is used as object, e.g. ?x rdf:type ?sc
    ?s ?p ?sc .
    FILTER(?p != rdfs:subClassOf)
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
ORDER BY ?sc
"""

# Reporting query result
for row in g.query(query):
    print(row['sc'])
