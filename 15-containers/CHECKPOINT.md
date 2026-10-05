# Checkpoint: Containers

Attempt without notes. Explain mechanisms and draw histories before opening the rubric.

## Scenario

The API container cannot reach localhost:5432, loses uploaded files on replacement, and ignores graceful shutdown until forcibly killed.

## Questions

1. Explain namespaces, cgroups, image layers, writable state, and volumes.
2. Trace container network/service names versus host-published ports.
3. Review Dockerfile caching, build secrets, non-root execution, and signal delivery.
4. Distinguish process startup, readiness, persistent storage, and backups in Compose.

## Evidence to produce

Replace an API container without losing authoritative data and demonstrate a bounded SIGTERM drain.

Score each answer: 0 = names only; 1 = correct happy path; 2 = failure mechanism and repair; 3 = assumptions, trade-offs, and validation. Pass when every question reaches 2 and the evidence is reproducible. Revisit weak chapters before advancing.

<details><summary>Review rubric after attempting</summary>

A container is a packaged isolated process, not an independent-kernel VM by default. Images are immutable inputs, and durable state has an explicitly managed lifecycle.

</details>

[Section reading order](README.md) · [Progress](../PROGRESS.md) · [Project briefs](../projects/README.md)
