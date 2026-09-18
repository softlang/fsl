import csv
from pathlib import Path
from rdflib import Graph
from fsl_utils import fsl_prefixes, local_name

ttl9b = Path("../../ontologies/versions/phase9b/ontologies/ie.ttl")
g9b = Graph()
g9b.parse(ttl9b, format="turtle")

ttl9e = Path("../../ontologies/versions/phase9e/ontologies/ie.ttl")
g9e = Graph()
g9e.parse(ttl9e, format="turtle")

ttl9j = Path("../../ontologies/versions/phase9j/ontologies/ie.ttl")
g9j = Graph()
g9j.parse(ttl9j, format="turtle")

# Query of interest
query = f"""
{fsl_prefixes}

SELECT DISTINCT ?i
WHERE {{
  ?i rdf:type tbox:IssueEntity .
  FILTER(?i NOT IN (
    ie:IssueOnResourceByTargetExample,
    ie:IssueOnAssertionObjectRoleExample,
    ie:IssueOnAssertionSubjectRoleExample,
    ie:IssueOnModuleByTargetExample
  ))
}}
ORDER BY ?i
"""

result9b = g9b.query(query)
result9e = g9e.query(query)
result9j = g9j.query(query)

# Reporting query result
with open("summary.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    for row in result9b:
        writer.writerow([
            local_name(row["i"])
        ])
    for row in result9e:
        writer.writerow([
            local_name(row["i"])
        ])
    for row in result9j:
        writer.writerow([
            local_name(row["i"])
        ])
