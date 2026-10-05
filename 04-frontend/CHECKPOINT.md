# Checkpoint: Frontend engineering

Attempt without notes. Explain mechanisms and draw histories before opening the rubric.

## Scenario

A task editor shows stale search results, loses an input when sorting, and freezes while typing. Its server-rendered date also mismatches during hydration.

## Questions

1. Explain task/microtask scheduling and why completion order differs from request order.
2. Assign ownership to URL filters, form drafts, server entities, and local UI state. Design stable query keys.
3. Explain React identity, render versus commit, effect cleanup, and the cost of derived-state effects.
4. Diagnose the freeze with browser/React traces and repair the hydration data contract.
5. Specify keyboard accessibility and behavior tests for failure and concurrent edits.

## Evidence to produce

Build a small page with deliberately delayed out-of-order responses, then demonstrate correct behavior and one measured performance improvement.

Score each answer: 0 = names only; 1 = correct happy path; 2 = failure mechanism and repair; 3 = assumptions, trade-offs, and validation. Pass when every question reaches 2 and the evidence is reproducible. Revisit weak chapters before advancing.

<details><summary>Review rubric after attempting</summary>

Correct answers preserve user intent, use stable identity, validate runtime data, and distinguish network, JavaScript, layout, and paint. They avoid treating memoization as a universal fix or TypeScript as runtime validation.

</details>

[Section reading order](README.md) · [Progress](../PROGRESS.md) · [Project briefs](../projects/README.md)
