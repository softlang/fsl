from fsl_utils import fsl_graph, fsl_prefixes_sparql

# Retrieve the ontology graph
g = fsl_graph()

# Query of interest
query = fsl_prefixes_sparql + """

SELECT DISTINCT ?t
WHERE {

  # An assertiom between a software tool and an SE activity
  {
    ?a ?p ?t
  }
  UNION
  {
    ?t ?p ?a
  }

  # An actual tool
  {
    SELECT DISTINCT ?t
    WHERE {
      ?tsc rdfs:subClassOf+ tbox:ToolEntity .
      ?t rdf:type ?tsc .
    }
  }

  # An SE activity as a non-immediate subclass of tbox:EngineeringActivity
  { 
    SELECT DISTINCT ?a
    WHERE {
      ?a rdfs:subClassOf+ tbox:EngineeringActivity .
      FILTER NOT EXISTS {
        ?a rdfs:subClassOf tbox:EngineeringActivity .
      }
    }
  }

  # Counting only ontological properties
  FILTER(?p != rdf:type) 
  FILTER(?p != rdfs:subClassOf)
  FILTER(?p != rdfs:domain)
  FILTER(?p != rdfs:range)
  FILTER(?p != rdfs:label)
  FILTER(?p != rdfs:comment)
  FILTER(?p != foaf:isPrimaryTopicOf)
  FILTER(?p != foaf:page)
}
ORDER BY ?t
"""

# Reporting query result
for row in g.query(query):
    print(row['t'])
