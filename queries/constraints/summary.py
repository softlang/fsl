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
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX tbox: <http://www.softlang.org/ontologies/tbox#>

SELECT ?p (COUNT(*) AS ?c)

WHERE {
  SELECT DISTINCT ?p ?sub ?obj
  WHERE {
    ?sub ?p ?obj .
    FILTER(?p IN (
      owl:intersectionOf,
      owl:unionOf,
      owl:complementOf,
      owl:oneOf,
      owl:Restriction,
      owl:onProperty,
      owl:someValuesFrom,
      owl:allValuesFrom,
      owl:hasValue,
      owl:minCardinality,
      owl:maxCardinality,
      owl:cardinality,
      owl:minQualifiedCardinality,
      owl:maxQualifiedCardinality,
      owl:qualifiedCardinality,
      owl:onClass,
      owl:onDataRange,
      owl:equivalentClass,
      owl:disjointWith,
      owl:disjointUnionOf,
      owl:equivalentProperty,
      owl:inverseOf,
      owl:propertyChainAxiom,
      owl:propertyDisjointWith
    ))    
  }
}

GROUP BY ?p
ORDER BY ?p
"""

result = g.query(query)

# Reporting query result
with open("summary.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["Property","Uses"])
    for row in result:
        writer.writerow([
            local_name(row["p"]),
            row["c"],
        ])
