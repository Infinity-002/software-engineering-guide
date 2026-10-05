# Checkpoint: Data structures inside systems

Attempt without notes. Explain mechanisms and draw histories before opening the rubric.

## Scenario

A write-heavy store has many sorted files, expensive negative lookups, growing compaction debt, and replicas that need efficient comparison.

## Questions

1. Explain Bloom insertion/query, false-positive sizing, no-false-negative assumptions, and deletion limits.
2. Compare B+ tree and LSM read/write/space behavior using pages and compaction.
3. Explain consistent hashing movement, virtual nodes, hot keys, and why placement is not migration.
4. Show skip-list search and Merkle replica comparison, including what each hierarchy skips.
5. Compare exact sets, HLL cardinality, Bloom membership, and inverted-index search.

## Evidence to produce

Run the Bloom lab, calculate a target size, and draw a compaction/tombstone history plus a Merkle proof.

Score each answer: 0 = names only; 1 = correct happy path; 2 = failure mechanism and repair; 3 = assumptions, trade-offs, and validation. Pass when every question reaches 2 and the evidence is reproducible. Revisit weak chapters before advancing.

<details><summary>Review rubric after attempting</summary>

The structure is chosen for a specific query and cost model. Approximation assumptions and error scope are stated. Hash agreement does not decide authority, and balanced key count does not imply balanced traffic.

</details>

[Section reading order](README.md) · [Progress](../PROGRESS.md) · [Project briefs](../projects/README.md)
