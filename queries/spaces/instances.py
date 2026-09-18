from fsl_utils import fsl_graph, fsl_prefixes

# Retrieve the ontology graph
g = fsl_graph()

# Query of interest
query = fsl_prefixes + """

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
