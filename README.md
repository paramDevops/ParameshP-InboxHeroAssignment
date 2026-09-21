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
