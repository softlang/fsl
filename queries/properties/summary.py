import csv
from fsl_utils import fsl_graph, fsl_prefixes, local_name

def property_type(value):
    ln = local_name(value)
    if ln == "AnnotationProperty":
        return "A"
    elif ln == "ObjectProperty":
        return "O"
    elif ln == "DatatypeProperty":
        return "D"
    else:
        return ""

# Retrieve the ontology graph
g = fsl_graph()

# Query of interest
query = fsl_prefixes + """

SELECT
  ?p ?t ?d ?r ?l ?c ?i ?a
WHERE {
  ?p rdf:type tbox:PropertyEntity .
  ?p rdf:type ?t .
  FILTER(?t IN (
      owl:AnnotationProperty,
      owl:ObjectProperty,
      owl:DatatypeProperty
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
