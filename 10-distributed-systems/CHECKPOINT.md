# Checkpoint: Distributed systems

Attempt without notes. Explain mechanisms and draw histories before opening the rubric.

## Scenario

A network partition isolates a leader. A new leader is elected, while the old one resumes after a long pause and still reaches storage.

## Questions

1. Explain partial failure and why a timeout does not prove death.
2. State CAP using a concrete partitioned read/write history and distinguish formal availability from an SLO.
3. Show what R + W > N proves and which protocol assumptions remain.
4. Walk through lease expiry, renewal, ownership checks, fencing, and the maximum-seen-token limitation.
5. Compare wall, monotonic, Lamport, and vector clocks; explain how consensus preserves committed history.

## Evidence to produce

Run the lease/fencing model and draw both a safe rejected stale write and an old write arriving before the newer fence is installed.

Score each answer: 0 = names only; 1 = correct happy path; 2 = failure mechanism and repair; 3 = assumptions, trade-offs, and validation. Pass when every question reaches 2 and the evidence is reproducible. Revisit weak chapters before advancing.

<details><summary>Review rubric after attempting</summary>

Authority is enforced at the accepting resource, not by a process's belief. Safety and liveness are separate. Clock, durability, membership, and failure assumptions are explicit.

</details>

[Section reading order](README.md) · [Progress](../PROGRESS.md) · [Project briefs](../projects/README.md)
