from fsl_utils import fsl_graph, fsl_prefixes_sparql

# Retrieve the ontology graph
g = fsl_graph()

# Query of interest
query = fsl_prefixes_sparql + """

SELECT DISTINCT ?l
WHERE {

  # An assertiom between software language and concept
  {
    ?c ?p ?l
  }
  UNION
  {
    ?l ?p ?c
  }

  # An actual language
  {
    SELECT DISTINCT ?l 
    WHERE {
      ?lsc rdfs:subClassOf+ tbox:LanguageEntity .
      ?l rdf:type ?lsc .
    }
  }

  # A concept entity
  { 
    SELECT DISTINCT ?c
    WHERE {
      {
        ?csc rdfs:subClassOf+ tbox:LanguageConcept .
        ?c rdf:type ?csc .
      }
      UNION
      {
        ?c rdfs:subClassOf+ tbox:LanguageConcept .
      }
    }
  }
  FILTER(STRSTARTS(STR(?p), STR(fsl:)))
}
ORDER BY ?l
"""

# Reporting query result
for row in g.query(query):
    print(row['l'])
