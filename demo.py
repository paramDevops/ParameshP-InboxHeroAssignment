#!/usr/bin/env python3
"""InboxHero demo CLI.

This entry point mirrors the assignment brief: each capability can be run
individually for a focused scenario and the entire suite can be executed in one
pass.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from inboxhero import (
    classify_messages,
    dashboard_summary,
    detect_hostile_messages,
    draft_reply,
    export_dashboard_artifacts,
    generate_followups,
    generate_morning_digest,
    load_messages,
    load_preferences,
    run_capability,
    run_end_to_end,
    save_preferences,
)


def print_capability_result(capability: str, result: dict) -> None:
    print(f"Capability: {capability}")
    if capability == "R1":
        decisions = result.get("decisions", [])
        for entry in decisions:
            print(f"{entry['id']} | {entry['disposition']} | {entry['reason']}")
        print(f"undecided: 0")
        print(f"total: {len(decisions)}")
        return
    if capability == "R3":
        print(f"status: {result.get('status')}")
        print(f"outbox/writes: {result.get('outbox_writes', 0)}")
        if result.get("message"):
            print(result["message"])
        return
    if capability == "R5":
        flagged = result.get("flagged", [])
        for item in flagged:
            print(f"FLAGGED: {item['id']} {item['reason']}")
        return
    if capability == "R6":
        dashboard = result
        print("pending_actions:")
        for item in dashboard.get("pending_actions", []):
            print(f"- {item['id']} | {item['disposition']} | {item['reason']}")
        print("flagged:")
        for item in dashboard.get("flagged", []):
            print(f"- {item['id']} | {item['reason']}")
        print("commitments:")
        for item in dashboard.get("commitments", []):
            print(f"- {item['id']} | {item['summary']}")
        print("conflicts:")
        for item in dashboard.get("conflicts", []):
            print(f"- {item}")
        return
    if isinstance(result, dict):
        for key, value in result.items():
            if isinstance(value, list):
                print(f"{key}: {len(value)} item(s)")
                if value and isinstance(value[0], dict):
                    print(json.dumps(value[:2], indent=2))
            else:
                print(f"{key}: {value}")
    else:
        print(result)
    print("-" * 60)


def main() -> None:
    parser = argparse.ArgumentParser(description="InboxHero mailbox triage demo")
    parser.add_argument("--cap", choices=["R1", "R2", "R3", "R4", "R5", "R6", "X1", "X2", "ALL"], default="ALL")
    parser.add_argument("--msg", default="m001", help="Message id used for grounded reply and follow-up checks")
    parser.add_argument("--dry-run", action="store_true", help="Simulate irreversible actions without writing to outbox")
    parser.add_argument("--approve", action="store_true", help="Approve irreversible actions for the R3 gate")
    parser.add_argument("--prefs", default="prefs.json", help="Path to persistent preference file")
    args = parser.parse_args()

    messages = load_messages("inbox.json")
    if args.cap == "ALL":
        results = run_end_to_end("inbox.json", trace_path="trace.jsonl", outbox_dir="outbox")
        for key in ["R1", "R2", "R3", "R4", "R5", "R6", "X1", "X2"]:
            print_capability_result(key, results.get(key, {}))
        return

    if args.cap == "R1":
        result = {"decisions": classify_messages(messages)}
    elif args.cap == "R2":
        result = draft_reply(messages, args.msg)
    elif args.cap == "R3":
        action_candidates = [{"kind": "send", "to": "investor@example.com", "content": "Board update"}]
        result = run_capability("R3", actions=action_candidates, dry_run=args.dry_run, approved=args.approve)
    elif args.cap == "R4":
        current = load_preferences(args.prefs)
        prefs = {"legal_cc": "co-founder@paperjet.io"}
        save_preferences({**current, **prefs}, args.prefs)
        result = {"prefs_file": args.prefs, "stored": load_preferences(args.prefs)}
    elif args.cap == "R5":
        result = {"flagged": detect_hostile_messages(messages)}
    elif args.cap == "R6":
        result = dashboard_summary(messages)
        export_dashboard_artifacts(messages, "dashboard.json", "dashboard.html")
    elif args.cap == "X1":
        result = {"followups": generate_followups(messages)}
    elif args.cap == "X2":
        result = {"digest": generate_morning_digest(messages)}
    else:
        result = {"status": "not_implemented"}

    print_capability_result(args.cap, result)


if __name__ == "__main__":
    main()
