from fsl_utils import fsl_graph, fsl_prefixes

# Retrieve the ontology graph
g = fsl_graph()

# Query of interest
query = fsl_prefixes + """

SELECT
  DISTINCT ?t
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
ORDER BY ?t
"""

# Reporting query result
for row in g.query(query):
    print(row['t'])
