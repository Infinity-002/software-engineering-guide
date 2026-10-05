# Checkpoint: Operating systems and Linux

Attempt without notes. Explain mechanisms and draw histories before opening the rubric.

## Scenario

An API is slow with 15% host CPU on eight cores. It eventually reports too many open files, and restarting helps for twenty minutes.

## Questions

1. Choose evidence to distinguish one saturated core, descriptor leaks, memory pressure, disk latency, and network waiting.
2. Explain why low host-average CPU and free disk bytes do not rule out resource exhaustion.
3. Specify a SIGTERM shutdown sequence and what correctness must survive if SIGKILL follows.
4. Describe how you would preserve evidence before a necessary restart.

## Evidence to produce

Inspect a disposable server with process, descriptor, socket, and application timing tools. Record observations separately from hypotheses.

Score each answer: 0 = names only; 1 = correct happy path; 2 = failure mechanism and repair; 3 = assumptions, trade-offs, and validation. Pass when every question reaches 2 and the evidence is reproducible. Revisit weak chapters before advancing.

<details><summary>Review rubric after attempting</summary>

Use per-process/per-core measurements and descriptor trends. Identify the resource owner and cleanup path. Shutdown stops acquisition before bounded drain, and forced termination remains safe through durable state and retries.

</details>

[Section reading order](README.md) · [Progress](../PROGRESS.md) · [Project briefs](../projects/README.md)
