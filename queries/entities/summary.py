import csv
from pathlib import Path
from rdflib import Graph

# Parse all Turtle files of the ontology
ttl_dir = Path("../../ontologies")
ttl_files = sorted(ttl_dir.glob("*.ttl"))
g = Graph()
for ttl in ttl_files:
    g.parse(ttl, format="turtle")

# Query of interest
query = """
PREFIX rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX tbox: <http://www.softlang.org/ontologies/tbox#>

SELECT
  ?lei ?les
  ?fei ?fes
  ?cei ?ces
  ?tei ?tes
  ?aei ?aes
  ?pei ?pes
WHERE {
  {
    SELECT (COUNT(DISTINCT ?le) AS ?lei)
    WHERE {
      ?le rdf:type tbox:LanguageEntity .
    }
  }

  {
    SELECT (COUNT(DISTINCT ?lesc) AS ?les)
    WHERE {
      ?lesc rdfs:subClassOf+ tbox:LanguageEntity .
    }
  }

  {
    SELECT (COUNT(DISTINCT ?fe) AS ?fei)
    WHERE {
      ?fe rdf:type tbox:FormalEntity .
    }
  }

  {
    SELECT (COUNT(DISTINCT ?fesc) AS ?fes)
    WHERE {
      ?fesc rdfs:subClassOf+ tbox:FormalEntity .
    }
  }

  {
    SELECT (COUNT(DISTINCT ?ce) AS ?cei)
    WHERE {
      ?ce rdf:type tbox:ConceptualEntity .
    }
  }

  {
    SELECT (COUNT(DISTINCT ?cesc) AS ?ces)
    WHERE {
      ?cesc rdfs:subClassOf+ tbox:ConceptualEntity .
    }
  }

  {
    SELECT (COUNT(DISTINCT ?te) AS ?tei)
    WHERE {
      ?te rdf:type tbox:ToolEntity .
    }
  }

  {
    SELECT (COUNT(DISTINCT ?tesc) AS ?tes)
    WHERE {
      ?tesc rdfs:subClassOf+ tbox:ToolEntity .
    }
  }

  {
    SELECT (COUNT(DISTINCT ?ae) AS ?aei)
    WHERE {
      ?ae rdf:type tbox:ArtifactEntity .
    }
  }

  {
    SELECT (COUNT(DISTINCT ?aesc) AS ?aes)
    WHERE {
      ?aesc rdfs:subClassOf+ tbox:ArtifactEntity .
    }
  }

  {
    SELECT (COUNT(DISTINCT ?pe) AS ?pei)
    WHERE {
      ?pe rdf:type tbox:PropertyEntity .
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
    writer.writerow(["Entity type", 'Number of instances', 'Number of subclasses'])
    for row in result:
        writer.writerow(["Language entity", row['lei'], row['les']])
        writer.writerow(["Formal entity", row['fei'], row['fes']])
        writer.writerow(["Conceptual entity", row['cei'], row['ces']])
        writer.writerow(["Tool entity", row['tei'], row['tes']])
        writer.writerow(["Artifact entity", row['aei'], row['aes']])
        writer.writerow(["Property entity", row['pei'], row['pes']])
