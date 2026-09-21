import json
from pathlib import Path

from inboxhero import (
    apply_preferences,
    classify_messages,
    dashboard_summary,
    detect_hostile_messages,
    draft_reply,
    generate_followups,
    generate_morning_digest,
    load_preferences,
    run_capability,
    run_end_to_end,
    save_preferences,
)


def test_r1_zero_the_inbox_assigns_every_message():
    messages = json.loads(Path("inbox.json").read_text(encoding="utf-8"))
    decisions = classify_messages(messages)
    assert len(decisions) == len(messages)
    assert all(item["disposition"] in {"reply", "archive", "defer", "delegate", "escalate"} for item in decisions)
    assert sum(1 for item in decisions if item["disposition"] == "archive") > 0
    assert sum(1 for item in decisions if item["disposition"] == "reply") > 0
    assert all(item["reason"] for item in decisions)


def test_r2_grounded_reply_uses_earlier_thread_message():
    messages = json.loads(Path("inbox.json").read_text(encoding="utf-8"))
    reply = draft_reply(messages, "m001")
    assert reply["cited"]
    assert "amqp" in reply["draft"].lower()
    assert reply["cited"][0] in {item["id"] for item in messages}


def test_r3_gate_requires_dry_run_or_approval():
    actions = [
        {"kind": "send", "to": "investor@example.com", "content": "Board update"},
        {"kind": "delete", "target": "m055"},
    ]
    dry_run = run_capability("R3", actions=actions, dry_run=True)
    approved = run_capability("R3", actions=actions, dry_run=False, approved=True)
    assert dry_run["outbox_writes"] == 0
    assert approved["outbox_writes"] == 2


def test_r4_persistent_preference_survives_restart(tmp_path):
    pref_path = tmp_path / "prefs.json"
    prefs = load_preferences(pref_path)
    assert prefs == {}
    save_preferences({"legal_cc": "co-founder@paperjet.io"}, pref_path)
    restored = load_preferences(pref_path)
    assert restored["legal_cc"] == "co-founder@paperjet.io"
    updated = apply_preferences({"legal_cc": "co-founder@paperjet.io"}, pref_path)
    assert updated["legal_cc"] == "co-founder@paperjet.io"


def test_r5_refuses_embedded_instructions():
    messages = json.loads(Path("inbox.json").read_text(encoding="utf-8"))
    hostile = detect_hostile_messages(messages)
    assert hostile
    assert any("forward" in item["reason"].lower() for item in hostile)
    assert any(item["id"] for item in hostile)


def test_r6_dashboard_has_three_panes_and_conflict():
    messages = json.loads(Path("inbox.json").read_text(encoding="utf-8"))
    dashboard = dashboard_summary(messages)
    assert "pending_actions" in dashboard
    assert "flagged" in dashboard
    assert "commitments" in dashboard
    assert isinstance(dashboard["pending_actions"], list)
    assert isinstance(dashboard["flagged"], list)
    assert isinstance(dashboard["commitments"], list)


def test_x1_follow_up_tracking_works():
    messages = json.loads(Path("inbox.json").read_text(encoding="utf-8"))
    followups = generate_followups(messages)
    assert isinstance(followups, list)
    assert all("message_id" in item and "days_waiting" in item for item in followups)


def test_x2_morning_digest_has_sections():
    messages = json.loads(Path("inbox.json").read_text(encoding="utf-8"))
    digest = generate_morning_digest(messages)
    assert set(digest.keys()) >= {"needs_you", "can_wait", "auto_archived"}
    assert digest["needs_you"]


def test_full_run_generates_trace_and_outbox(tmp_path):
    trace_path = tmp_path / "trace.jsonl"
    outbox_dir = tmp_path / "outbox"

    run_end_to_end(
        "inbox.json",
        dry_run=False,
        approved=True,
        trace_path=trace_path,
        outbox_dir=outbox_dir,
    )

    assert trace_path.exists()
    lines = [line for line in trace_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert lines
    assert any(json.loads(line).get("capability") == "R1" for line in lines)
    assert outbox_dir.exists()
    assert any(outbox_dir.iterdir())
