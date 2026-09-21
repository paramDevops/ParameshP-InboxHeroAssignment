# Public GitHub Repository
https://github.com/paramDevops/ParameshP-InboxHeroAssignment
# InboxHero Assignment Submission

## Student
Paramesh Pebbanaboina

## Overview
This project implements an end-to-end inbox triage assistant for the InboxHero assignment. It reads the provided inbox, classifies each message into exactly one disposition, drafts grounded replies based on earlier thread context, blocks unsafe irreversible actions behind a gate, stores preference state, refuses embedded hostile instructions, and produces a dashboard and morning digest.

## Architecture
The architecture is intentionally simple and auditable, rather than model-heavy or framework-driven:

- [inboxhero.py](inboxhero.py): mailbox logic for loading messages, classifying dispositions, detecting hostile content, generating grounded replies, producing the digest, and building the dashboard
- [demo.py](demo.py): CLI entry point to run each capability scenario independently or in a full sweep
- [tests/test_inboxhero_e2e.py](tests/test_inboxhero_e2e.py): E2E regression checks for all required behaviors
- [FINAL_REPORT.md](FINAL_REPORT.md): narrative answers to the assignment questions and design choices
- [inbox.json](inbox.json): source inbox used by the workflow
- [assignment_07/reference/capabilities.sample.json](assignment_07/reference/capabilities.sample.json): machine-readable rubric and capability specification

## Framework choice
This solution uses a lightweight Python implementation with the standard library only. I chose a deterministic, rule-based architecture instead of a heavy web or agent framework because the assignment focuses on: safety, explainability, provenance, and precise control over irreversible operations. The implementation remains easy to audit, test, and run from a single project root.

## Disposition vocabulary
Each inbound message is assigned exactly one disposition from the following vocabulary:

- reply: direct response needed or technical/legal response expected
- archive: routine or low-signal information that does not require user action
- defer: scheduling or coordination task that can be handled later
- delegate: human approval or operational handoff required
- escalate: reserved for urgent matters that require escalation; the rule set in this project uses escalation-like urgency through the same action pathway where needed

Every decision carries a reason string so the workflow remains explainable and easy to review.

## Reversible vs irreversible actions
The system separates reversible and irreversible behavior explicitly.

### Reversible operations
These are safe, reviewable, and do not trigger real outbound effects:
- draft replies
- label or archive messages
- defer scheduling work
- prepare dashboard or digest outputs

### Irreversible operations
These are treated as high-risk and are gated:
- send
- delete

The gate logic enforces either:
- a dry run that shows what would happen without writing to the outbox, or
- an explicit approval flag before the action is executed

This means the model or workflow cannot silently send or delete without an approval checkpoint.

## Retrieval approach
The retrieval strategy is thread-grounded rather than free-form semantic retrieval:

- load the inbox as structured JSON
- locate the target message by message id
- read the matching thread_id
- find earlier messages in that same thread
- cite the earlier message ids used for grounding in the reply

This gives the assistant a controlled, verifiable provenance chain for every grounded response, instead of inventing context.

## Hostile instruction handling
Embedded or adversarial instructions are recognized and refused before they can influence the normal workflow. Examples include exfiltration attempts, override instructions, and implicit “ignore all previous instructions” patterns. The system records the offending message id and does not send or delete anything as a result.

## Final Report answers summary
The final report answers the assignment’s questions in the following way:

1. Architecture: a transparent rule-based Python pipeline with explicit message classification, reply grounding, governance, and dashboard outputs.
2. Framework choice: standard-library Python because the project prioritizes safe deterministic control over visual complexity or heavy frameworks.
3. Disposition vocabulary: reply, archive, defer, delegate, and escalate-style priority handling with a reason for every decision.
4. Reversible vs irreversible classification: reversible actions remain passive and reviewable, while send/delete are gated for approval.
5. Retrieval approach: thread-local citation and earlier-message grounding to keep replies anchored in actual evidence.
6. Safety: hostile instructions are refused, user approval is required for irreversible actions, and preferences persist across runs.

## Safety and architecture answers

### 1. What did you refuse to automate?
I refuse to automate any irreversible external send or destructive delete without an explicit approval gate. One example is a message that asks the assistant to forward mailbox contents to an external address or to trigger a release without review. In this project, the system deliberately does not act on that kind of message by itself because it is both exfiltration-sensitive and irreversible. The line is drawn at the action boundary: a message can influence a draft or a classification, but it cannot reach `send` or `delete` unless `run_capability()` and the approval checks explicitly allow it. That keeps the automation conservative and reviewable.

### 2. Where does untrusted text enter your system?
Untrusted text enters at the inbox boundary, when [inboxhero.py](inboxhero.py) loads the JSON mailbox through `load_messages()` and turns each message body into a Python dictionary. After that, all text is treated as untrusted data until it passes a narrow safety check. The architecture separates two zones:

- the read-only text zone: `detect_hostile_messages()`, `classify_messages()`, `draft_reply()`, and dashboard generation all consume message text, but they never execute it;
- the action zone: only `run_capability()` and the explicit `send`/`delete` writing paths can produce an irreversible effect, and they enforce a gate first.

The essential property is that the message body is never interpreted as instructions to the program itself. It is only inspected, summarized, reasoned over, and converted into a decision record. An attacker would have to defeat the hostile-text filters in `detect_hostile_messages()`, bypass the approval gate in `run_capability()`, and produce a valid action payload that the system would still treat as legitimate. That is a much harder target than a single prompt injection line.

### 3. Who is accountable when it sends the wrong thing?
The human owner remains accountable for the final send decision, while the system helps make the failure traceable. The code keeps a record of every capability run in [trace.jsonl](trace.jsonl) via `_write_trace_event()`, and writes irreversible actions to the [outbox](outbox) directory via `_write_outbox_actions()`. A bad message can still be caused by a bad human approval or a poor decision, but the system preserves the evidence trail: timestamp, capability, event type, message id, action, and target. If a message is badly worded, factually wrong, or sent to the wrong person, the owner can review the trace and the exact outbox artifact to see which message, which approval step, and which run produced it. In other words, the system does not remove responsibility; it makes the failure auditable.

### 4. Name your own machinery.
The project does not use a framework; it builds its own equivalent of the common agentic pieces directly in Python.

- Agents: the specialized logic functions in [inboxhero.py](inboxhero.py), such as `classify_messages()`, `detect_hostile_messages()`, `draft_reply()`, `generate_followups()`, and `generate_morning_digest()`, act like distinct agent roles because each one owns a specific reasoning step.
- Tasks: the capability work in `run_capability()` and the full orchestration in `run_end_to_end()` represent the task layer. Each task performs one operational unit: classify, draft, gate, persist preferences, summarize, and export.
- Crew: the coordination and sequencing is effectively done by `demo.py` and `run_end_to_end()`, which choose which task runs in what order and aggregate the results for the user.
- Router: the CLI in [demo.py](demo.py) is the router. It reads the `--cap` argument and dispatches to the matching logic, including the `ALL` case.

One thing a framework would have given us is a structured execution runtime with abstraction for orchestration, retries, and tool scheduling. I built that ourselves using plain Python functions and JSON artifacts, and for this assignment that helped more than it hurt because the problem is small, explicit, and safety-critical. A heavy framework would mostly add indirection and extra moving parts without increasing the trustworthiness of the system. In a small deterministic pipeline, explicit code is easier to audit and easier to reason about when you are controlling irreversible actions.

## How to run

```bash
python demo.py --cap R1
python demo.py --cap R2 --msg m001
python demo.py --cap R3 --dry-run
python demo.py --cap R3 --approve
python demo.py --cap R4
python demo.py --cap R5
python demo.py --cap R6
python demo.py --cap X1
python demo.py --cap X2
python demo.py --cap ALL
```

## Project files
- [inboxhero.py](inboxhero.py) — core mailbox logic
- [demo.py](demo.py) — CLI entry point
- [tests/test_inboxhero_e2e.py](tests/test_inboxhero_e2e.py) — E2E verification
- [FINAL_REPORT.md](FINAL_REPORT.md) — final answers and rationale
- [trace.jsonl](trace.jsonl) — recorded full-run events
- [outbox](outbox) — generated outbound actions for approved irreversible tasks
- [inbox.json](inbox.json) — inbox dataset
- [assignment_07/reference/capabilities.sample.json](assignment_07/reference/capabilities.sample.json) — assignment rubric

## GitHub note
This README intentionally has the public GitHub repository link at the top. Replace the placeholder URL with your actual repository URL before publishing the project.

## Submission note
This project is packaged as a clean final submission and is designed to be runnable from the project root while staying explainable, safe, and auditable.
