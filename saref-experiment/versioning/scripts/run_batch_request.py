#!/usr/bin/env python3
"""Submit a built Batch request and retrieve its structured response.

Writes one file per custom_id to --out-dir. Real submission requires
OPENAI_API_KEY and calls OpenAI's Batch API. --mock-response skips OpenAI
entirely -- for local testing and CI, or whenever you want to exercise the
rest of the pipeline (render_and_validate.py, open_pr.py) without spending
real API calls.
"""

import argparse
import json
import os
import time
from pathlib import Path


def read_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def read_jsonl(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def load_mock_responses(path: Path, requests: list[dict]) -> dict[str, dict]:
    """Load mocked structured responses, keyed by custom_id.

    Accepts either {"<custom_id>": {...response...}, ...} or, for the common
    single-request case, a bare response object (its own "runId" is used as
    the custom_id key).
    """
    data = read_json(path)
    if "runId" in data:
        return {data["runId"]: data}
    return data


def submit_and_poll(requests: list[dict], poll_interval: int) -> dict[str, dict]:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise SystemExit(
            "OPENAI_API_KEY is not set. Pass --mock-response to exercise this "
            "pipeline without calling OpenAI."
        )
    from openai import OpenAI

    client = OpenAI(api_key=api_key)

    batch_input = "\n".join(json.dumps(r) for r in requests) + "\n"
    batch_file = client.files.create(
        file=("batch.jsonl", batch_input.encode("utf-8")), purpose="batch"
    )
    batch = client.batches.create(
        input_file_id=batch_file.id, endpoint="/v1/responses", completion_window="24h"
    )
    print(f"Submitted batch {batch.id} ({len(requests)} request(s)), polling every {poll_interval}s...")

    while batch.status not in ("completed", "failed", "expired", "cancelled"):
        time.sleep(poll_interval)
        batch = client.batches.retrieve(batch.id)
        print(f"  status: {batch.status}")

    if batch.status != "completed":
        raise SystemExit(f"Batch {batch.id} ended with status '{batch.status}', not 'completed'.")

    output_text = client.files.content(batch.output_file_id).text
    results: dict[str, dict] = {}
    for line in output_text.splitlines():
        if not line.strip():
            continue
        entry = json.loads(line)
        custom_id = entry["custom_id"]
        if entry.get("error"):
            raise SystemExit(f"Batch entry {custom_id} failed: {entry['error']}")
        body = entry["response"]["body"]
        # /v1/responses with a json_schema text format returns the structured
        # payload as a JSON string in the first output item's text content.
        structured_text = body["output"][0]["content"][0]["text"]
        results[custom_id] = json.loads(structured_text)
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--batch", required=True, type=Path, help="A *.jsonl file from build_batch_request.py")
    parser.add_argument("--out-dir", required=True, type=Path)
    parser.add_argument(
        "--mock-response",
        type=Path,
        help="Skip OpenAI entirely; use this JSON file as the structured response for testing",
    )
    parser.add_argument("--poll-interval", type=int, default=10)
    args = parser.parse_args()

    requests = read_jsonl(args.batch)
    args.out_dir.mkdir(parents=True, exist_ok=True)

    if args.mock_response:
        responses = load_mock_responses(args.mock_response, requests)
        for request in requests:
            custom_id = request["custom_id"]
            if custom_id not in responses:
                raise SystemExit(f"No mock response provided for custom_id '{custom_id}'")
            out_path = args.out_dir / f"{custom_id}.json"
            out_path.write_text(json.dumps(responses[custom_id], indent=2) + "\n", encoding="utf-8")
            print(f"[mock] wrote {out_path}")
        return

    responses = submit_and_poll(requests, args.poll_interval)
    for custom_id, structured in responses.items():
        out_path = args.out_dir / f"{custom_id}.json"
        out_path.write_text(json.dumps(structured, indent=2) + "\n", encoding="utf-8")
        print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
