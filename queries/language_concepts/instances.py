from fsl_utils import fsl_graph, fsl_prefixes_sparql

# Retrieve the ontology graph
g = fsl_graph()

# Query of interest
query = fsl_prefixes_sparql + """

SELECT
  DISTINCT ?i
WHERE {
  ?sc rdfs:subClassOf+ tbox:LanguageConcept .
  ?i rdf:type ?sc .
}
ORDER BY ?i
"""

# Reporting query result
for row in g.query(query):
    print(row['i'])
