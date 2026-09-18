from fsl_utils import fsl_graph, fsl_prefixes

# Retrieve the ontology graph
g = fsl_graph()

# Query of interest
query = fsl_prefixes + """

SELECT
  DISTINCT ?a
WHERE {
  ?s rdf:type tbox:TechnologicalSpace .
  ?a rdf:type tbox:ArtifactEntity .
  {
    ?s ?from ?a .
  }
  UNION
  {
    ?a ?to ?s .
  }
}
ORDER BY ?a
"""

# Reporting query result
for row in g.query(query):
    print(row['a'])
