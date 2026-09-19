from fsl_utils import fsl_graph, fsl_prefixes_sparql

# Retrieve the ontology graph
g = fsl_graph()

# Query of interest
query = fsl_prefixes_sparql + """

SELECT
  DISTINCT ?s
WHERE {
  ?s rdf:type tbox:TechnologicalSpace .
  ?l rdf:type tbox:LanguageEntity .
  {
    ?s ?from ?l .
  }
  UNION
  {
    ?l ?to ?s .
  }
}
ORDER BY ?s
"""

# Reporting query result
for row in g.query(query):
    print(row['s'])
