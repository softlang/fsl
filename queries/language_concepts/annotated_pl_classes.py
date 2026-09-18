from fsl_utils import fsl_graph, fsl_prefixes

# Retrieve the ontology graph
g = fsl_graph()

# Query of interest
query = fsl_prefixes + """

SELECT DISTINCT ?l
WHERE {

  # An assertiom between programming language and concept
  {
    ?c ?p ?l
  }
  UNION
  {
    ?l ?p ?c
  }

  # A programming language type
  {
    SELECT DISTINCT ?l
    WHERE {
      ?l rdfs:subClassOf* pe:ProgrammingLanguage .
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
