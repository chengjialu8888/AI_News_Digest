#!/usr/bin/env python3
"""Append a human visual review to the persistent artist Lottery case store."""

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "ralph-daily-loop"))

from style_contracts import CASE_MEMORY_VERSION, return_route  # noqa: E402


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--entry", required=True, help="art-style-lottery-entry.json")
    parser.add_argument("--status", required=True, choices=("accepted", "rework_requested", "rejected"))
    parser.add_argument("--cases", default=None, help="case store; defaults to data/art-style-cases.json")
    parser.add_argument("--finding", action="append", default=[], help="observable finding; repeatable")
    parser.add_argument("--return-to", choices=("catalog", "mechanism_extract", "trend_translation", "prompt", "craft"), default="craft")
    parser.add_argument("--fix", default="记录下一次修复动作或重新抽签条件")
    parser.add_argument("--surface-fidelity", default="N/A")
    parser.add_argument("--mechanism-fidelity", default="N/A")
    parser.add_argument("--fidelity-verdict", default="pending")
    parser.add_argument("--reviewer", default="human-review")
    parser.add_argument("--note", default="")
    return parser.parse_args()


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def main():
    args = parse_args()
    entry_path = Path(args.entry)
    entry = read_json(entry_path)
    lottery = entry.get("style_lottery") or {}
    case_memory = entry.get("case_memory") or lottery.get("case_memory") or {}
    current = case_memory.get("current_case") or {}
    case_id = current.get("case_id") or entry.get("case_id")
    if not case_id:
        raise SystemExit("entry does not contain case_memory.current_case.case_id")

    cases_path = Path(args.cases) if args.cases else Path(
        case_memory.get("store_path_config") or ROOT / "data" / "art-style-cases.json"
    )
    if cases_path.exists():
        payload = read_json(cases_path)
    else:
        payload = {"schema_version": CASE_MEMORY_VERSION, "cases": []}
    if isinstance(payload, list):
        payload = {"schema_version": CASE_MEMORY_VERSION, "cases": payload}
    payload.setdefault("schema_version", CASE_MEMORY_VERSION)
    payload.setdefault("cases", [])

    finding_text = args.finding or ["No blocking finding recorded"]
    review = {
        "case_id": case_id,
        "date": entry.get("date"),
        "selected_style": lottery.get("selected_style"),
        "catalog_id": lottery.get("catalog_id"),
        "status": args.status,
        "reviewed_at": datetime.now(timezone.utc).isoformat(),
        "reviewer": args.reviewer,
        "surface_fidelity": args.surface_fidelity,
        "mechanism_fidelity": args.mechanism_fidelity,
        "fidelity_verdict": args.fidelity_verdict,
        "findings": finding_text,
        "return_plan": return_route(args.return_to, finding_text[0], args.fix),
        "note": args.note,
        "contract_version": lottery.get("contract_version") or entry.get("style_contract_version"),
        "source_case": str(entry_path),
    }
    payload["cases"] = [case for case in payload["cases"] if case.get("case_id") != case_id]
    payload["cases"].append(review)
    cases_path.parent.mkdir(parents=True, exist_ok=True)
    cases_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(json.dumps({"case_id": case_id, "status": args.status, "cases_path": str(cases_path)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
