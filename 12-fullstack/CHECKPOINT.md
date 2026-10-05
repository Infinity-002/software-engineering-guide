# Checkpoint: End-to-end application engineering

Attempt without notes. Explain mechanisms and draw histories before opening the rubric.

## Scenario

A user saves a task, uploads a file, and receives a live notification, but then loses the network before seeing confirmations.

## Questions

1. Trace click through runtime, network, auth, SQL, response, query cache, React commit, and pixels.
2. Diagnose login success with missing subsequent cookies using browser policy evidence.
3. Define mutation unknown outcomes and reconnect recovery through durable cursors.
4. Model upload intent, object version, quarantine, verification, publication, and orphan cleanup.

## Evidence to produce

Capture one complete request trace and one interrupted upload or live-message recovery history.

Score each answer: 0 = names only; 1 = correct happy path; 2 = failure mechanism and repair; 3 = assumptions, trade-offs, and validation. Pass when every question reaches 2 and the evidence is reproducible. Revisit weak chapters before advancing.

<details><summary>Review rubric after attempting</summary>

The explanation joins frontend and backend authority rather than treating fetch as a magical boundary. Live delivery is separate from durable history, and an upload capability does not certify content safety.

</details>

[Section reading order](README.md) · [Progress](../PROGRESS.md) · [Project briefs](../projects/README.md)
