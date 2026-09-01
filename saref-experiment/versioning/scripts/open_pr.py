#!/usr/bin/env python3
"""Open a review PR for a validated candidate version-addition patch.

Never runs automatically as part of validation, and never merges anything.
By default this only prints what it would do. Pass --push to create a local
branch, copy the validated patch over the real module, commit, and push it.
Pass --create-pr (implies --push) to also open a GitHub PR via `gh`, whose
body is the candidate's review notes -- a human still reviews and merges it.
"""

import argparse
import json
import shutil
import subprocess
from pathlib import Path


def read_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def run(cmd: list[str], **kwargs) -> subprocess.CompletedProcess:
    print(f"$ {' '.join(cmd)}")
    return subprocess.run(cmd, check=True, **kwargs)


def main() -> None:
    versioning_dir = Path(__file__).resolve().parents[1]
    experiment_dir = versioning_dir.parent
    default_repo_root = experiment_dir.parent

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evidence", required=True, type=Path)
    parser.add_argument("--patch-dir", type=Path, default=experiment_dir / "results" / "versioning" / "candidate-patches")
    parser.add_argument("--repo-root", type=Path, default=default_repo_root)
    parser.add_argument("--base", default="main")
    parser.add_argument("--push", action="store_true", help="Create a local branch, commit, and push it")
    parser.add_argument("--create-pr", action="store_true", help="Also open a GitHub PR via `gh` (implies --push)")
    args = parser.parse_args()
    if args.create_pr:
        args.push = True

    evidence = read_json(args.evidence)
    run_id = evidence["runId"]
    module_rel = evidence["targetModule"]
    patched_module = args.patch_dir / f"{run_id}-{Path(module_rel).name}"
    review_notes = args.patch_dir / f"{run_id}.md"

    if not patched_module.exists():
        raise SystemExit(f"No validated patch at {patched_module} -- run render_and_validate.py first.")

    branch = f"versioning/{run_id}"
    target_module = args.repo_root / module_rel
    commit_message = f"Add {evidence['parentEntity']} {evidence['version']} version entry\n\nSource: {evidence['officialSource']}"
    pr_title = f"versioning: add {evidence['parentEntity']} {evidence['version']}"

    print(f"[{run_id}] would create branch '{branch}' from '{args.base}'")
    print(f"[{run_id}] would copy {patched_module} -> {target_module}")
    print(f"[{run_id}] would commit: {commit_message.splitlines()[0]}")
    body_note = f" using body from {review_notes}" if review_notes.exists() else " using the commit message as the body"
    print(f"[{run_id}] would open PR '{pr_title}' targeting '{args.base}'{body_note}")

    if not args.push:
        print("\nDry run only -- pass --push to actually branch/commit/push, --create-pr to also open a PR.")
        return

    run(["git", "-C", str(args.repo_root), "checkout", "-b", branch, args.base])
    shutil.copyfile(patched_module, target_module)
    run(["git", "-C", str(args.repo_root), "add", str(target_module.relative_to(args.repo_root))])
    run(["git", "-C", str(args.repo_root), "commit", "-m", commit_message])
    run(["git", "-C", str(args.repo_root), "push", "-u", "origin", branch])

    if args.create_pr:
        cmd = ["gh", "pr", "create", "--title", pr_title, "--base", args.base, "--head", branch]
        cmd += ["--body-file", str(review_notes)] if review_notes.exists() else ["--body", commit_message]
        run(cmd, cwd=str(args.repo_root))


if __name__ == "__main__":
    main()
