import csv
import json

FSL_FIELDS = ("SoftwareLanguage", "Label")
PLDB_FIELDS = ("id", "name")

# Read FSL
with open("../../queries/languages/instances.csv", encoding="utf-8-sig", newline="") as f:
    instances = list(csv.DictReader(f))

# Read PLDB
with open("./languages.json", encoding="utf-8-sig") as f:
    languages = json.load(f)

# Index both PLDB name fields; retain duplicate names and records.
name_index = {}
for index, language in enumerate(languages):
    for field in PLDB_FIELDS:
        value = language.get(field)
        if isinstance(value, str) and value:
            name_index.setdefault(value.lower(), []).append((index, field))

# Compute matching results
results = []

for row_number, instance in enumerate(instances, start=1):
    matched_records = {}

    for fsl_field in FSL_FIELDS:
        value = instance.get(fsl_field)
        if not value:
            continue

        for index, pldb_field in name_index.get(value.lower(), []):
            matched_records.setdefault(index, []).append({
                "fsl_field": fsl_field,
                "pldb_field": pldb_field,
                "value": value,
                })

    matches = []
    for index, name_matches in sorted(matched_records.items()):
        language = languages[index]
        csv_url = instance.get("Page")
        json_url = language.get("wikipedia")

        matches.append({
            "language": language,
            "name_matches": name_matches,
            # null means one or both URLs are missing.
            "url_equal": (
                csv_url == json_url
                if csv_url and json_url
                else None
            ),
        })

    results.append({
        "instance": instance,
        "matched": bool(matches),
        "match_count": len(matches),
        "matches": matches,
    })

with open("matches.csv", "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=[
        "FslLanguage", "FslLabel", "FslClassifier", "FslPage",
        "PldbId", "PldbName", "PldbWikipedia", 
        "matched", "match_count", "name_matches", "url_equal",
    ])
    writer.writeheader()

    for result in results:
        for match in result["matches"] or [None]:
            language = match["language"] if match else {}
            writer.writerow({
                "FslLanguage": result["instance"]["SoftwareLanguage"],
                "FslLabel": result["instance"]["Label"],
                "FslClassifier": result["instance"]["Classifier"],
                "FslPage": result["instance"]["Page"],
                "PldbId": language.get("id", ""),
                "PldbName": language.get("name", ""),
                "PldbWikipedia": language.get("wikipedia", ""),
                "matched": result["matched"],
                "match_count": result["match_count"],
                "name_matches": "; ".join(
                    f'{pair["fsl_field"]} -> {pair["pldb_field"]}'
                    for pair in match["name_matches"]
                ) if match else "",
                "url_equal": match["url_equal"] if match else "",
            })

matched = sum(result["matched"] for result in results)
print(f"{matched} matched; {len(results) - matched} unmatched")

print("\nUnmatched FSL languages:")
for result in results:
    if not result["matched"]:
        instance = result["instance"]
        print(f'- {instance["SoftwareLanguage"]} ({instance["Label"]})')
