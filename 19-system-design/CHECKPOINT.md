# Checkpoint: System design

Attempt without notes. Explain mechanisms and draw histories before opening the rubric.

## Scenario

Design a private file-sharing service, then add offline edits, a tenfold traffic peak, and a regional outage requirement one at a time.

## Questions

1. Apply all fourteen method steps, including APIs, authoritative data, capacity units, and skew.
2. Trace one write/read and crash between each durable boundary.
3. Defend consistency, authorization, deletion, observability, and recovery decisions.
4. Name a component you intentionally omit and the measured trigger for adding it.

## Evidence to produce

Produce a timed design document and revise only the assumptions affected by each new requirement.

Score each answer: 0 = names only; 1 = correct happy path; 2 = failure mechanism and repair; 3 = assumptions, trade-offs, and validation. Pass when every question reaches 2 and the evidence is reproducible. Revisit weak chapters before advancing.

<details><summary>Review rubric after attempting</summary>

Components follow requirements rather than a memorized diagram. The answer distinguishes metadata from blobs, authority from projections, and local atomicity from external effects. Estimates influence choices.

</details>

[Section reading order](README.md) · [Progress](../PROGRESS.md) · [Project briefs](../projects/README.md)
