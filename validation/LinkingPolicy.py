import json
from fsl_utils import fsl_graph, fsl_prefixes_sparql

# Retrieve the ontology graph
g = fsl_graph()

# Measure compliance with the linking policy for instances of tbox:Entity.
# N/A is an acceptable foaf:page, but not a primary-topic link.
# Acceptable targets start with "https://en.wikipedia.org" (literal prefix).
# Linked (formerly acceptable): entities with at least one acceptable link.
# Missing: entities with no acceptable link.
# Unacceptable: entities with at least one rejected link, independently counted.
# Acceptable: linked entities with no rejected links.
# Percentages use all entities (missing + linked) as their denominator.
query = fsl_prefixes_sparql + """

SELECT ?missing ?page ?isPrimaryTopicOf ?linked ?acceptable ?unacceptable ?naPage ?naIsPrimaryTopicOf
WHERE {
  {
    SELECT (COUNT(DISTINCT ?entity) AS ?missing)
    WHERE {
      ?entity rdf:type/rdfs:subClassOf* tbox:Entity .
      FILTER NOT EXISTS {
        ?entity ?predicate ?target .
        VALUES ?predicate { foaf:page foaf:isPrimaryTopicOf }
        FILTER (STRSTARTS(STR(?target), "https://en.wikipedia.org"))
        FILTER (?predicate = foaf:page || ?target != <https://en.wikipedia.org/wiki/N/A>)
      }
    }
  }
  {
    SELECT (COUNT(DISTINCT ?entity) AS ?page)
    WHERE {
      ?entity rdf:type/rdfs:subClassOf* tbox:Entity .
      ?entity foaf:page ?target .
      FILTER (STRSTARTS(STR(?target), "https://en.wikipedia.org"))
    }
  }
  {
    SELECT (COUNT(DISTINCT ?entity) AS ?isPrimaryTopicOf)
    WHERE {
      ?entity rdf:type/rdfs:subClassOf* tbox:Entity .
      ?entity foaf:isPrimaryTopicOf ?target .
      FILTER (STRSTARTS(STR(?target), "https://en.wikipedia.org"))
      FILTER (?target != <https://en.wikipedia.org/wiki/N/A>)
    }
  }
  {
    SELECT (COUNT(DISTINCT ?entity) AS ?linked)
    WHERE {
      ?entity rdf:type/rdfs:subClassOf* tbox:Entity .
      ?entity ?predicate ?target .
      VALUES ?predicate { foaf:page foaf:isPrimaryTopicOf }
      FILTER (STRSTARTS(STR(?target), "https://en.wikipedia.org"))
      FILTER (?predicate = foaf:page || ?target != <https://en.wikipedia.org/wiki/N/A>)
    }
  }
  {
    SELECT (COUNT(DISTINCT ?entity) AS ?acceptable)
    WHERE {
      ?entity rdf:type/rdfs:subClassOf* tbox:Entity .
      ?entity ?predicate ?target .
      VALUES ?predicate { foaf:page foaf:isPrimaryTopicOf }
      FILTER (STRSTARTS(STR(?target), "https://en.wikipedia.org"))
      FILTER (?predicate = foaf:page || ?target != <https://en.wikipedia.org/wiki/N/A>)
      FILTER NOT EXISTS {
        ?entity ?badPredicate ?badTarget .
        VALUES ?badPredicate { foaf:page foaf:isPrimaryTopicOf }
        FILTER (
          !STRSTARTS(STR(?badTarget), "https://en.wikipedia.org") ||
          (?badPredicate = foaf:isPrimaryTopicOf &&
           ?badTarget = <https://en.wikipedia.org/wiki/N/A>)
        )
      }
    }
  }
  {
    SELECT (COUNT(DISTINCT ?entity) AS ?unacceptable)
    WHERE {
      ?entity rdf:type/rdfs:subClassOf* tbox:Entity .
      ?entity ?predicate ?target .
      VALUES ?predicate { foaf:page foaf:isPrimaryTopicOf }
      FILTER (
        !STRSTARTS(STR(?target), "https://en.wikipedia.org") ||
        (?predicate = foaf:isPrimaryTopicOf &&
         ?target = <https://en.wikipedia.org/wiki/N/A>)
      )
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
missing = int(result["missing"])
page = int(result["page"])
is_primary_topic_of = int(result["isPrimaryTopicOf"])
linked = int(result["linked"])
acceptable = int(result["acceptable"])
unacceptable = int(result["unacceptable"])
na_page = int(result["naPage"])
na_is_primary_topic_of = int(result["naIsPrimaryTopicOf"])
# These two counts partition the entities; unacceptable is not added again.
total = missing + linked
linked_percentage = linked / total * 100 if total else 0
acceptable_percentage = acceptable / total * 100 if total else 0

# Count N/A links separately; an entity using both predicates contributes two.
report = {
    "total": total,
    "na": {
        "page": na_page,
        "isPrimaryTopicOf": na_is_primary_topic_of,
        "sum": na_page + na_is_primary_topic_of,
    },
    "missing": missing,
    "unacceptable": unacceptable,
    "linked": {
        "page": page,
        "isPrimaryTopicOf": is_primary_topic_of,
        "sum": linked,
        "percentage": round(linked_percentage, 2),
    },
    "acceptable": {
        "sum": acceptable,
        "percentage": round(acceptable_percentage, 2),
    },
}

with open("LinkingPolicy.json", "w", encoding="utf-8") as f:
    json.dump(report, f, indent=2)
    f.write("\n")
