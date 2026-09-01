#!/usr/bin/env python3
"""Build one OpenAI Batch-compatible request from normalised release evidence.

This script deliberately writes a request file only. It does not submit it to an
LLM service and it never edits an ontology module.
"""

import argparse
import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker


def read_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def validate(instance: dict, schema_path: Path) -> None:
    schema = read_json(schema_path)
    errors = sorted(
        Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(instance),
        key=lambda error: list(error.path),
    )
    if errors:
        details = "; ".join(error.message for error in errors)
        raise ValueError(f"Input does not match {schema_path.name}: {details}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence", required=True, type=Path)
    parser.add_argument("--prompt", required=True, type=Path)
    parser.add_argument("--schema", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--model", default="MODEL_TO_BE_SELECTED")
    args = parser.parse_args()

    evidence = read_json(args.evidence)
    validate(evidence, args.evidence.parent / "release-evidence.schema.json")
    response_schema = read_json(args.schema)

    request = {
        "custom_id": evidence["runId"],
        "method": "POST",
        "url": "/v1/responses",
        "body": {
            "model": args.model,
            "instructions": args.prompt.read_text(encoding="utf-8"),
            "input": json.dumps(evidence, indent=2),
            "text": {
                "format": {
                    "type": "json_schema",
                    "name": "fsl_version_addition",
                    "strict": True,
                    "schema": response_schema,
                }
            },
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(request) + "\n", encoding="utf-8")
    print(f"Wrote request for {evidence['runId']} to {args.output}")


if __name__ == "__main__":
    main()
