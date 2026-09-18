import csv
from pathlib import Path
from fsl_utils import fsl_graph, fsl_prefixes

# Retrieve the ontology graph
g = fsl_graph()

# Languages of interest
languages = [
    ("pe", "Java"),
    ("pe", "JavaScript"),
    ("le", "SQL"),
]

# Query template
query = fsl_prefixes + """

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
