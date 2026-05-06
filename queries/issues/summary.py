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

ttl9b = Path("../../ontologies/versions/phase9b/ontologies/ie.ttl")
g9b = Graph()
g9b.parse(ttl9b, format="turtle")

ttl9e = Path("../../ontologies/versions/phase9e/ontologies/ie.ttl")
g9e = Graph()
g9e.parse(ttl9e, format="turtle")

# Query of interest
query = """
PREFIX rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX tbox: <http://www.softlang.org/ontologies/tbox#>
PREFIX ie: <http://www.softlang.org/ontologies/ie#>

SELECT DISTINCT ?i
WHERE {
  ?i rdf:type tbox:IssueEntity .
  FILTER(?i NOT IN (
    ie:IssueOnResourceByTargetExample,
    ie:IssueOnAssertionObjectRoleExample,
    ie:IssueOnAssertionSubjectRoleExample,
    ie:IssueOnModuleByTargetExample
  ))
}
ORDER BY ?i
"""

result9b = g9b.query(query)
result9e = g9e.query(query)

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
