#!/usr/bin/env python3
"""Validate a structured LLM candidate before any ontology patch is prepared."""

import argparse
import json
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker


def read_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


CANDIDATE_TO_EVIDENCE_KEY = {
    "versionTag": "version",
    "releaseDate": "releaseDate",
    "predecessor": "predecessor",
    "officialSource": "officialSource",
}


def check_fields(response: dict, evidence: dict) -> list[str]:
    """Check the response's identifying fields match the evidence exactly.

    Catches hallucination/drift from the source facts. Does not inspect
    turtleBlock content -- that requires parsing it, which render_and_validate.py
    does separately.
    """
    errors = []
    for key in ("runId", "targetModule", "parentEntity", "entityKind", "version"):
        if response.get(key) != evidence.get(key):
            errors.append(f"Response {key} does not match the release evidence.")
    candidate = response.get("candidate", {})
    for cand_key, ev_key in CANDIDATE_TO_EVIDENCE_KEY.items():
        if candidate.get(cand_key) != evidence.get(ev_key):
            errors.append(f"Candidate {cand_key} does not match the release evidence.")
    return errors


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--response", required=True, type=Path)
    parser.add_argument("--schema", required=True, type=Path)
    parser.add_argument("--evidence", required=True, type=Path)
    args = parser.parse_args()

    response = read_json(args.response)
    evidence = read_json(args.evidence)
    schema = read_json(args.schema)
    errors = sorted(
        Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(response),
        key=lambda error: list(error.path),
    )
    if errors:
        raise SystemExit("Schema validation failed: " + "; ".join(error.message for error in errors))

    field_errors = check_fields(response, evidence)
    if field_errors:
        raise SystemExit("Schema validation failed: " + "; ".join(field_errors))
    print("Structured response matches the release evidence. Ontology validation remains required.")


if __name__ == "__main__":
    main()
