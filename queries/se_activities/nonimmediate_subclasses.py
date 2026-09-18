from fsl_utils import fsl_graph, fsl_prefixes

# Retrieve the ontology graph
g = fsl_graph()

# Query of interest
query = fsl_prefixes + """

SELECT
  DISTINCT ?sc
WHERE {
  ?sc rdfs:subClassOf+ tbox:EngineeringActivity .
  FILTER NOT EXISTS {
    ?sc rdfs:subClassOf tbox:EngineeringActivity .
  }
}
ORDER BY ?sc
"""

# Reporting query result
for row in g.query(query):
    print(row['sc'])
