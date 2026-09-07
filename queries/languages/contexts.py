import csv
from pathlib import Path
from rdflib import Graph

# Parse all Turtle files of the ontology
ttl_dir = Path("../../ontologies")
ttl_files = sorted(ttl_dir.glob("*.ttl"))
g = Graph()
for ttl in ttl_files:
    g.parse(ttl, format="turtle")

# Languages of interest
languages = [
    ("pe", "Java"),
    ("pe", "JavaScript"),
    ("le", "SQL"),
]

# Query template
query = """
PREFIX pe: <http://www.softlang.org/ontologies/pe#>
PREFIX le: <http://www.softlang.org/ontologies/le#>

SELECT DISTINCT ?s ?p ?o
WHERE {{
    ?s ?p ?o .
    FILTER (?s = {prefix}:{language} || ?o = {prefix}:{language})
}}
ORDER BY ?s ?p ?o
"""

# Query and report context for each language
output_dir = Path("contexts")
output_dir.mkdir(exist_ok=True)

for prefix, language in languages:
    result = g.query(query.format(
        prefix=prefix,
        language=language
    ))

    output_file = output_dir / f"{language}.csv"
    with output_file.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Subject", "Predicate", "Object"])

        for row in result:
            writer.writerow([
                str(row["s"]),
                str(row["p"]),
                str(row["o"])
            ])
