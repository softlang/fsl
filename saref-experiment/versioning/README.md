# LLM-assisted versioning experiment

This experiment extends the existing SAREF-inspired Python/CPython versioning proof of concept. It evaluates whether an LLM can propose a **single, reviewable version addition** for an entity that already exists in FSL.

The LLM is not an authority for release facts and must not edit FSL directly. Each run follows this pipeline:

```text
tracked-entities.json + release feed        <- detect_new_releases.py (no LLM)
  -> candidate release evidence
  -> structured LLM response
  -> deterministic schema and ontology validation
  -> candidate patch
  -> human review
```

## Layout

- `state/tracked-entities.json` lists the FSL entities this experiment watches and where to check for new releases.
- `src/` contains version-controlled, normalised release evidence and its schema.
- `prompts/` contains the human-readable LLM instructions.
- `schemas/` contains the required structured LLM output contract.
- `scripts/` contains local tooling that detects candidates, builds requests, validates output, and prepares review artefacts.
- `../results/versioning/` contains generated, reproducible run outputs. It must never be used as source input.

## Detecting new releases (no LLM)

From the repository root, diff FSL's tracked entities against their release feeds:

```bash
make -C saref-experiment versioning-detect
```

This is deterministic HTTP + SPARQL only. It writes one candidate evidence file per missing version to `saref-experiment/results/versioning/detected/<runId>.json` -- e.g. `python-3.13.json` -- shaped like `src/release-evidence.schema.json`, but the `predecessor` link and `officialSource` URL are inferred by convention and **must be confirmed by a human before use as LLM input.**

It defaults to frontier detection: only releases newer than the newest version FSL already tracks for that entity. FSL tracks a curated sample (e.g. Python 2.7, 3.6, 3.12, not every release), so a full backfill diff is mostly noise; pass `EXTRA=--include-backfill` to see it anyway.

## Running the full pipeline (Python example)

From the repository root:

```bash
make -C saref-experiment versioning-request           # build the LLM request (no LLM call)
make -C saref-experiment versioning-run MOCK=1        # replay a fixture response, no OpenAI call
make -C saref-experiment versioning-validate          # parse + validate + render a candidate patch
make -C saref-experiment versioning-pr                # dry run: prints what a PR would look like
```

- `versioning-request` only generates `saref-experiment/results/versioning/batches/python-3.13.jsonl`; it does not call an LLM or change an ontology module.
- `versioning-run` calls OpenAI's Batch API and needs `OPENAI_API_KEY` -- pass `MOCK=1` to instead replay `scripts/fixtures/python-3.13.response.json`, so the rest of the pipeline can be exercised without spending real API calls.
- `versioning-validate` never writes to the real ontology module. It checks the response against its JSON schema and its evidence, parses `turtleBlock`, and checks module-level invariants (predecessor exists, no duplicate version tag, OWL-consistent) against a scratch copy of the target module. Only on a full pass does it write a patched module, a unified diff, and review notes to `results/versioning/candidate-patches/`; any failure writes only a validation report to `results/versioning/validation/`.
- `versioning-pr` prints the branch/commit/PR it would create. Pass `PUSH=1` to actually branch, commit, and push; `PR=1` (implies `PUSH=1`) to also open a GitHub PR via `gh`. Nothing here merges anything -- a human reviews and merges the opened PR.

## Safety boundary

Only evidence for an existing FSL entity may be processed. A response is a candidate until a human reviews it and the deterministic parsing, module-invariant, and OWL-consistency validation stages pass. Automation stops at an opened pull request; nothing in this pipeline merges to `main`.
