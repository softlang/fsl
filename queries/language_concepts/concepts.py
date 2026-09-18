from fsl_utils import fsl_graph, fsl_prefixes

# Retrieve the ontology graph
g = fsl_graph()

# Query of interest
query = fsl_prefixes + """

SELECT
  DISTINCT ?c
WHERE {
  {
    ?sc rdfs:subClassOf+ tbox:LanguageConcept .
    ?c rdf:type ?sc .
  }
  UNION
  {
    ?c rdfs:subClassOf+ tbox:LanguageConcept .
  }
}
ORDER BY ?c
"""

# Reporting query result
for row in g.query(query):
    print(row['c'])
