from fsl_utils import fsl_graph, fsl_prefixes

# Retrieve the ontology graph
g = fsl_graph()

# Query of interest
query = fsl_prefixes + """

SELECT
  ?i
WHERE {
  ?sc rdfs:subClassOf+ tbox:EngineeringActivity .
  ?i rdf:type ?sc .
}
ORDER BY ?i
"""

# Reporting query result
for row in g.query(query):
    print(row['i'])
