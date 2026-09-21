# Final Report — InboxHero Submission

## Student
Paramesh Pebbanaboina

## Overview
This project implements an end-to-end inbox triage assistant for the assignment brief. The system reads the supplied inbox, classifies each message into a single disposition, grounds replies in earlier thread context, refuses hostile embedded instructions, enforces a gate before irreversible actions, persists preference state, and produces a dashboard and morning digest.

## Architecture
The implementation is deliberately lightweight and transparent:

- [inboxhero.py](inboxhero.py): message loading, message classification, hostile instruction detection, reply drafting, follow-up generation, digest creation, and dashboard export
- [demo.py](demo.py): CLI runner for each required capability
- [tests/test_inboxhero_e2e.py](tests/test_inboxhero_e2e.py): end-to-end checks covering the assignment scenarios
- [assignment_07/reference/inbox.json](assignment_07/reference/inbox.json): source inbox dataset
- [assignment_07/reference/capabilities.sample.json](assignment_07/reference/capabilities.sample.json): machine-readable capability specification

## Capability coverage

### R1 — Zero the inbox
The classifier assigns exactly one disposition to each message. The valid outputs are reply, archive, defer, delegate, and escalate. Every item also carries a short reason explaining the choice.

### R2 — Grounded reply
The draft reply logic searches inside the same thread for earlier evidence and uses that context to produce a grounded answer. The reply includes cited message IDs and a source excerpt so the statement is traceable.

### R3 — Gate the irreversible
The irreversible action path is blocked unless the user explicitly approves or uses a dry run. This prevents accidental send/delete behavior from slipping through without a governance check.

### R4 — Persistent preference
The implementation stores preferences in a JSON file so they can survive a restart-like reload. This makes preferences usable across multiple runs without requiring the original instruction to be repeated.

### R5 — Refuse embedded instructions
Messages that contain embedded override instructions are detected and refused. The system does not propagate those instructions into the normal workflow.

### R6 — Dashboard
The dashboard summarises pending actions, flagged items, commitments, and conflict markers. The dashboard is written to JSON and HTML so it exists as a reproducible artifact.

### X1 — Follow-up tracking
The follow-up generator identifies messages that need a response or check-in and creates a short draft for the user.

### X2 — Morning digest
The digest groups messages into what needs attention, what can wait, and what was auto-archived.

## Safety posture
The design follows a conservative rule set. Routine notifications are archived quickly, operational issues and legal requests remain visible for review, and any hostile or deceptive instruction is blocked before it can affect the final decision path.

## Submission status
This package is structured for a final hand-in and is designed to be easy to understand, run, and evaluate against the rubric.
