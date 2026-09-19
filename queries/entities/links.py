import json
from fsl_utils import fsl_graph, fsl_prefixes_sparql

# Retrieve the ontology graph
g = fsl_graph()

# Measure compliance with the linking policy for instances of tbox:Entity.
# N/A is an acceptable foaf:page, but not a primary-topic link.
# An entity succeeds if it has at least one acceptable link.
query = fsl_prefixes_sparql + """

SELECT ?failing ?page ?isPrimaryTopicOf ?succeeding ?naPage ?naIsPrimaryTopicOf
WHERE {
  {
    SELECT (COUNT(DISTINCT ?entity) AS ?failing)
    WHERE {
      ?entity rdf:type/rdfs:subClassOf* tbox:Entity .
      FILTER NOT EXISTS {
        ?entity ?predicate ?target .
        VALUES ?predicate { foaf:page foaf:isPrimaryTopicOf }
        FILTER (?predicate = foaf:page || ?target != <https://en.wikipedia.org/wiki/N/A>)
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
      FILTER (?target != <https://en.wikipedia.org/wiki/N/A>)
    }
  }
  {
    SELECT (COUNT(DISTINCT ?entity) AS ?succeeding)
    WHERE {
      ?entity rdf:type/rdfs:subClassOf* tbox:Entity .
      ?entity ?predicate ?target .
      VALUES ?predicate { foaf:page foaf:isPrimaryTopicOf }
      FILTER (?predicate = foaf:page || ?target != <https://en.wikipedia.org/wiki/N/A>)
    }
  }
  {
    SELECT (COUNT(DISTINCT ?entity) AS ?naPage)
    WHERE {
      ?entity rdf:type/rdfs:subClassOf* tbox:Entity .
      ?entity foaf:page <https://en.wikipedia.org/wiki/N/A> .
    }
  }
  {
    SELECT (COUNT(DISTINCT ?entity) AS ?naIsPrimaryTopicOf)
    WHERE {
      ?entity rdf:type/rdfs:subClassOf* tbox:Entity .
      ?entity foaf:isPrimaryTopicOf <https://en.wikipedia.org/wiki/N/A> .
    }
  }
}
"""

result = next(iter(g.query(query)))
failing = int(result["failing"])
page = int(result["page"])
is_primary_topic_of = int(result["isPrimaryTopicOf"])
succeeding = int(result["succeeding"])
na_page = int(result["naPage"])
na_is_primary_topic_of = int(result["naIsPrimaryTopicOf"])
total = failing + succeeding
percentage = succeeding / total * 100 if total else 0

# Count N/A links separately; an entity using both predicates contributes two.
report = {
    "na": {
        "page": na_page,
        "isPrimaryTopicOf": na_is_primary_topic_of,
        "sum": na_page + na_is_primary_topic_of,
    },
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
