import json
from fsl_utils import fsl_graph, fsl_prefixes_sparql

# Retrieve the ontology graph
g = fsl_graph()

# Measure compliance with the linking policy for instances of tbox:Entity.
query = fsl_prefixes_sparql + """

SELECT ?failing ?page ?isPrimaryTopicOf ?succeeding
WHERE {
  {
    SELECT (COUNT(DISTINCT ?entity) AS ?failing)
    WHERE {
      ?entity rdf:type/rdfs:subClassOf* tbox:Entity .
      FILTER NOT EXISTS {
        ?entity (foaf:isPrimaryTopicOf|foaf:page) ?page .
      }
    }
  }
  {
    SELECT (COUNT(DISTINCT ?entity) AS ?page)
    WHERE {
      ?entity rdf:type/rdfs:subClassOf* tbox:Entity .
      ?entity foaf:page ?target .
    }
  }
  {
    SELECT (COUNT(DISTINCT ?entity) AS ?isPrimaryTopicOf)
    WHERE {
      ?entity rdf:type/rdfs:subClassOf* tbox:Entity .
      ?entity foaf:isPrimaryTopicOf ?target .
    }
  }
  {
    SELECT (COUNT(DISTINCT ?entity) AS ?succeeding)
    WHERE {
      ?entity rdf:type/rdfs:subClassOf* tbox:Entity .
      ?entity (foaf:isPrimaryTopicOf|foaf:page) ?page .
    }
  }
}
"""

result = next(iter(g.query(query)))
failing = int(result["failing"])
page = int(result["page"])
is_primary_topic_of = int(result["isPrimaryTopicOf"])
succeeding = int(result["succeeding"])
total = failing + succeeding
percentage = succeeding / total * 100 if total else 0

report = {
    "failing": failing,
    "succeeding": {
        "page": page,
        "isPrimaryTopicOf": is_primary_topic_of,
        "sum": succeeding,
        "percentage": round(percentage, 2),
    },
}

with open("links.json", "w", encoding="utf-8") as f:
    json.dump(report, f, indent=2)
    f.write("\n")
