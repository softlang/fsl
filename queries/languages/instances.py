from pathlib import Path
import csv
from fsl_utils import fsl_graph, fsl_prefixes, local_name

# Retrieve the ontology graph
g = fsl_graph()

# Query all direct and transitive instances of SoftwareLanguage
query = fsl_prefixes + """

SELECT DISTINCT ?language ?label ?classifier ?page
WHERE {
    ?classifier rdfs:subClassOf* tbox:SoftwareLanguage .
    ?language rdf:type ?classifier .
    OPTIONAL { ?language rdfs:label ?label . }
    OPTIONAL { ?language foaf:isPrimaryTopicOf ?page . }
}
ORDER BY ?language
"""

# Write query result to CSV
output_file = Path("instances.csv")
with output_file.open("w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["SoftwareLanguage", "Label", "Classifier", "Page"])
    for row in g.query(query):
        language = local_name(row["language"])
        label = row["label"]
        classifier = local_name(row["classifier"])
        page = row["page"]
        writer.writerow([language, label, classifier, page])
