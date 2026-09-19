import csv
from fsl_utils import fsl_graph, fsl_prefixes_sparql, local_name

# Retrieve the ontology graph
g = fsl_graph()

# Query of interest
query = f"""
{fsl_prefixes_sparql}
SELECT ?p (COUNT(*) AS ?c)
WHERE {{
  SELECT DISTINCT ?p ?sub ?obj
  WHERE {{
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
  }}
}}
GROUP BY ?p
ORDER BY ?p
"""

result = g.query(query)

# Reporting query result
with open("summary.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["Property","Uses"])
    for row in result:
        writer.writerow([local_name(row["p"]), row["c"]])
