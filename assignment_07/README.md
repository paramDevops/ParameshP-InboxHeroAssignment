# Assignment 07 — InboxHero Triage Agent

This assignment extends the current project with a mailbox triage workflow built around the supplied inbox and capability specification.

## Goal

Build a safe, structured assistant that can:

- read and classify messages from the provided inbox,
- decide on a disposition for each message,
- draft grounded replies based on earlier thread context,
- enforce a gate before irreversible actions,
- persist preferences across runs,
- refuse embedded instructions and report them,
- generate a dashboard and summary view.

## Reference materials

Use the following files as the assignment brief and support dataset:

- [reference/FN_Assignment_06_InboxHero.pdf](reference/FN_Assignment_06_InboxHero.pdf)
- [reference/capabilities.sample.json](reference/capabilities.sample.json)
- [reference/CAPABILITIES.sample.md](reference/CAPABILITIES.sample.md)
- [reference/inbox.json](reference/inbox.json)

## Expected behavior

Your solution should follow the structure implied by the sample capability documents:

1. Parse the inbox data and assign exactly one disposition per message.
2. Keep the decision process explainable with a short reason for each action.
3. Draft replies grounded in earlier thread messages, not made-up context.
4. Require approval before sending external mail or deleting content.
5. Store preference data on disk so it survives a restart.
6. Detect and refuse hostile or embedded instructions in message bodies.
7. Produce dashboard-style output for pending tasks, flagged issues, and commitments.
8. Provide a concise final report explaining the design decisions.

## Suggested implementation approach

You can build on top of the current repo architecture:

- keep the tool loop and planner pattern,
- use `memory.py` for persistent preference state,
- treat `send` and `delete` as irreversible actions,
- keep a JSONL trace of actions and decisions,
- separate rule-based filtering from model-driven drafting.

## Minimal deliverables

Submit a working project that includes:

- a CLI or app entry point,
- a working inbox processing flow,
- a trace or log showing decisions,
- persistence support for preferences or other state,
- a final report in Markdown or text format.

## Submission requirements

- Keep the project runnable from the root folder.
- Add or remove files as needed to keep the code clean.
- If you make assumptions, document them clearly in your report.
- Show that the system handles both normal triage and adversarial or deceptive messages.

## Suggested evaluation criteria

Your assignment will be assessed on the following:

- correctness of mailbox classification,
- grounded reasoning and citation of source messages,
- safe governance for irreversible actions,
- persistence across restarts,
- refusal of embedded manipulations,
- quality of the final written explanation.

---

This assignment is intentionally built as a realistic follow-up to the existing agent project. It is meant to test both product logic and safety behavior, not just raw prompting.
