from fsl_utils import fsl_graph, fsl_prefixes

# Retrieve the ontology graph
g = fsl_graph()

# Query of interest
query = fsl_prefixes + """

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
