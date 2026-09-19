import csv
from fsl_utils import fsl_graph, fsl_prefixes_sparql

# Retrieve the ontology graph
g = fsl_graph()

# Query of interest
query = fsl_prefixes_sparql + """

SELECT
  ?lee ?lei ?les
  ?fee ?fei ?fes
  ?cee ?cei ?ces
  ?tee ?tei ?tes
  ?aee ?aei ?aes
  ?pee ?pei ?pes
WHERE {
  {
    SELECT (COUNT(DISTINCT ?le) AS ?lee)
    WHERE {
      ?le rdf:type tbox:LanguageEntity .
    }
  }

  {
    SELECT (COUNT(DISTINCT ?le) AS ?lei)
    WHERE {
      ?le rdf:type tbox:LanguageEntity .
      FILTER NOT EXISTS {
        ?le rdfs:subClassOf+ tbox:LanguageEntity .
      }
    }
  }

  {
    SELECT (COUNT(DISTINCT ?lesc) AS ?les)
    WHERE {
      ?lesc rdfs:subClassOf+ tbox:LanguageEntity .
    }
  }

  {
    SELECT (COUNT(DISTINCT ?fe) AS ?fee)
    WHERE {
      ?fe rdf:type tbox:FormalEntity .
    }
  }

  {
    SELECT (COUNT(DISTINCT ?fe) AS ?fei)
    WHERE {
      ?fe rdf:type tbox:FormalEntity .
      FILTER NOT EXISTS {
        ?fe rdfs:subClassOf+ tbox:FormalEntity .
      }
    }
  }

  {
    SELECT (COUNT(DISTINCT ?fesc) AS ?fes)
    WHERE {
      ?fesc rdfs:subClassOf+ tbox:FormalEntity .
    }
  }

  {
    SELECT (COUNT(DISTINCT ?ce) AS ?cee)
    WHERE {
      ?ce rdf:type tbox:ConceptualEntity .
    }
  }

  {
    SELECT (COUNT(DISTINCT ?ce) AS ?cei)
    WHERE {
      ?ce rdf:type tbox:FormalEntity .
      FILTER NOT EXISTS {
        ?ce rdfs:subClassOf+ tbox:ConceptualEntity .
      }
    }
  }

  {
    SELECT (COUNT(DISTINCT ?cesc) AS ?ces)
    WHERE {
      ?cesc rdfs:subClassOf+ tbox:ConceptualEntity .
    }
  }

  {
    SELECT (COUNT(DISTINCT ?te) AS ?tee)
    WHERE {
      ?te rdf:type tbox:ToolEntity .
    }
  }

  {
    SELECT (COUNT(DISTINCT ?te) AS ?tei)
    WHERE {
      ?te rdf:type tbox:ToolEntity .
      FILTER NOT EXISTS {
        ?te rdfs:subClassOf+ tbox:ToolEntity .
      }
    }
  }

  {
    SELECT (COUNT(DISTINCT ?tesc) AS ?tes)
    WHERE {
      ?tesc rdfs:subClassOf+ tbox:ToolEntity .
    }
  }

  {
    SELECT (COUNT(DISTINCT ?ae) AS ?aee)
    WHERE {
      ?ae rdf:type tbox:ArtifactEntity .
    }
  }

  {
    SELECT (COUNT(DISTINCT ?ae) AS ?aei)
    WHERE {
      ?ae rdf:type tbox:ArtifactEntity .
      FILTER NOT EXISTS {
        ?ae rdfs:subClassOf+ tbox:ArtifactEntity .
      }
    }
  }

  {
    SELECT (COUNT(DISTINCT ?aesc) AS ?aes)
    WHERE {
      ?aesc rdfs:subClassOf+ tbox:ArtifactEntity .
    }
  }

  {
    SELECT (COUNT(DISTINCT ?pe) AS ?pee)
    WHERE {
      ?pe rdf:type tbox:PropertyEntity .
    }
  }

  {
    SELECT (COUNT(DISTINCT ?pe) AS ?pei)
    WHERE {
      ?pe rdf:type tbox:PropertyEntity .
      FILTER NOT EXISTS {
        ?pe rdfs:subClassOf+ tbox:PropertyEntity .
      }
    }
  }

  {
    SELECT (COUNT(DISTINCT ?pesc) AS ?pes)
    WHERE {
      ?pesc rdfs:subClassOf+ tbox:PropertyEntity .
    }
  }
}
"""

result = g.query(query)

# Reporting query result
with open("summary.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow([
        "Entity type",
        "Number of entities",
        "Number of instances",
        "Number of subclasses"])
    for row in result:
        writer.writerow(["Language entity", row['lee'], row['lei'], row['les']])
        writer.writerow(["Formal entity", row['fee'], row['fei'], row['fes']])
        writer.writerow(["Conceptual entity", row['cee'], row['cei'], row['ces']])
        writer.writerow(["Tool entity", row['tee'], row['tei'], row['tes']])
        writer.writerow(["Artifact entity", row['aee'], row['aei'], row['aes']])
        writer.writerow(["Property entity", row['pee'], row['pei'], row['pes']])
