from pathlib import Path

template = Path("languages.prompt.template").read_text(encoding="utf-8")
ontology = "https://github.com/softlang/fsl/tree/main/ontologies"
tbox = "https://github.com/softlang/fsl/blob/main/ontologies/tbox.ttl"

languages = [
    {
        "language": "Java",
        "abox": "https://github.com/softlang/fsl/blob/main/queries/languages/contexts/Java.csv",
        "wikipedia": "https://en.wikipedia.org/wiki/Java_(programming_language)",
    },
]

for item in languages:
    prompt = template.format(
        ontology=ontology,
        tbox=tbox,
        **item,
    )

    Path(f"languages/{item['language']}.prompt").write_text(
        prompt,
        encoding="utf-8",
    )
