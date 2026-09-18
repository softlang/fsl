from fsl_utils import fsl_graph, fsl_prefixes

# Retrieve the ontology graph
g = fsl_graph()

# Query of interest
query = fsl_prefixes + """

SELECT DISTINCT ?sc
WHERE {
  ?sc rdfs:subClassOf+ tbox:LanguageConcept .
  {
    ?s ?p ?sc .
  }
  UNION
  {
    ?sc ?p ?o .
  }
  FILTER(STRSTARTS(STR(?p), STR(fsl:)))
}
ORDER BY ?sc
"""

# Reporting query result
for row in g.query(query):
    print(row['sc'])
