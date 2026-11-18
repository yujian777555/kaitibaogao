"""CLI for D-092 Probe; execution requires a pre-existing exact-environment lock."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from d092_probe import execute_probe, write_execution_lock


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--outdir", type=Path, default=Path(__file__).resolve().parent / "results" / "probe")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--lock-only", action="store_true")
    mode.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    if args.lock_only:
        path = write_execution_lock(args.outdir)
        print(json.dumps({"status": "LOCKED_BEFORE_ROLLOUT", "path": str(path)}))
        return
    summary = execute_probe(args.outdir)
    print(json.dumps({"status": summary["status"], "episode_count": summary["episode_count"], "outdir": str(args.outdir)}))


if __name__ == "__main__":
    main()
