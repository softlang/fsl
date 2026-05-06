import csv
from pathlib import Path
from rdflib import Graph

def local_name(value):
    if value is None:
        return ""
    text = str(value)
    if "#" in text:
        return text.rsplit("#", 1)[1]
    return text

def property_type(value):
    ln = local_name(value)
    if ln == "AnnotationProperty":
        return "A"
    elif ln == "ObjectProperty":
        return "O"
    else:
        return ""

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
  ?p ?t ?d ?r ?l ?c ?i ?a
WHERE {
  ?p rdf:type tbox:PropertyEntity .
  ?p rdf:type ?t .
  FILTER(?t IN (
      owl:AnnotationProperty,
      owl:ObjectProperty
  ))
  OPTIONAL {
    ?p rdfs:domain ?d .
    FILTER(isIRI(?d))
  }
  OPTIONAL {
    ?p rdfs:range ?r .
    FILTER(isIRI(?r))
  }
  OPTIONAL {
    ?p rdfs:label ?l .
  }
  OPTIONAL {
    ?p rdfs:comment ?c .
  }
  OPTIONAL {
    ?p owl:inverseOf ?i .
  }
  OPTIONAL {
    SELECT ?p (COUNT(*) AS ?a)

    WHERE
      {
        SELECT DISTINCT ?p ?sub ?obj
        WHERE
          {
            ?sub ?p ?obj .
          }
      }
    GROUP BY ?p
  }
}
ORDER BY DESC(?a)
"""

result = g.query(query)

# Reporting query result
with open("summary.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f, delimiter=";")
    writer.writerow(["Property","Type","Domain","Range","Label","Comment","Inverse","Assertions"])
    for row in result:
        if row["a"]:
            writer.writerow([
                local_name(row["p"]),
                property_type(row["t"]),
                local_name(row["d"]),
                local_name(row["r"]),
                row["l"],
                row["c"],
                local_name(row["i"]),
                row["a"]
                ])
