from pathlib import Path

template = Path("activities.prompt.template").read_text(encoding="utf-8")

resources = [
    {
        "config": "ProckoCSV",
        "swebok": "https://github.com/PR0CK0/swebok-rebel-rdf/blob/main/02_single_SWEBOK_file/01-15_SWEBOK_post_construct_FIXED.ttl",
        "sle": "https://github.com/softlang/fsl/blob/main/queries/activies/instances.csv"
    },
]

for item in resources:
    prompt = template.format(
        **item,
    )

    Path(f"activities/{item['config']}.prompt").write_text(
        prompt,
        encoding="utf-8",
    )
