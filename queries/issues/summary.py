import csv
from fsl_utils import ONTOLOGIES_DIR, fsl_graph, fsl_prefixes, local_name

versions_dir = ONTOLOGIES_DIR / "versions"
g9b = fsl_graph(versions_dir / "phase9b/ontologies/ie.ttl")
g9e = fsl_graph(versions_dir / "phase9e/ontologies/ie.ttl")
g9j = fsl_graph(versions_dir / "phase9j/ontologies/ie.ttl")

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
