"""Print why RunLedger failed, straight from its own artifacts.

`runledger run` prints a PASS/FAIL table and exits non-zero; the failure
reasons live in runledger_out/<suite>/<run_id>/run.jsonl. This script just
echoes the assertion_failure / case_error events from the latest run so the
reason is visible in the CI log. It adds no checks of its own.
"""
import json
import sys
from pathlib import Path

runs = sorted(Path("runledger_out").glob("*/*/run.jsonl"), key=lambda p: p.stat().st_mtime)
if not runs:
    print("No RunLedger run.jsonl found.")
    sys.exit(0)

run = runs[-1]
print(f"RunLedger failures from {run}:")
found = False
for line in run.read_text(encoding="utf-8").splitlines():
    event = json.loads(line)
    case = event.get("case_id")
    if event.get("type") == "assertion_failure":
        for f in event.get("failures", []):
            found = True
            print(f"::error title=RunLedger {f['type']} ({case})::{f['message']}")
            print(f"  case:     {case}")
            print(f"  type:     {f['type']}")
            print(f"  message:  {f['message']}")
            details = f.get("details") or {}
            if "expected_order" in details:
                print(f"  expected: {' -> '.join(details['expected_order'])}")
                print(f"  observed: {' -> '.join(details['observed_calls'])}")
            elif details:
                print(f"  details:  {json.dumps(details)}")
    elif str(event.get("type", "")).endswith(("failure", "error")):
        found = True
        print(f"  {case}: {json.dumps(event)}")
if not found:
    print("  (no assertion failures recorded)")
