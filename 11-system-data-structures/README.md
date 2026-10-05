# Data structures inside systems

**Prerequisites:** [Foundations](../01-foundations/README.md), [Databases](../06-databases/README.md). **Roadmap level:** 3.

Read in this order; the checkpoint asks you to combine the ideas rather than repeat definitions.

Chapter | Priority | Concepts
--- | --- | ---
[Bloom filters and negative knowledge](bloom-filters.md) | P1 | Bloom filters, bit arrays, hash functions, false positives, false negatives, Bloom sizing, counting Bloom filters
[Consistent hashing and placement](consistent-hashing.md) | P2 | consistent hashing, modulo hashing, hash ring, virtual nodes, placement, replica placement
[B-trees and B+ trees](b-plus-trees.md) | P1 | B-trees, B+ trees, fanout, page splits, linked leaves, balanced storage trees
[LSM trees and compaction](lsm-trees.md) | P2 | LSM trees, memtable, SSTables, compaction, read amplification, space amplification, tombstones
[Skip lists: ordered data without tree rotations](skip-lists.md) | P2 | skip lists, probabilistic levels, concurrent ordered structures
[Merkle trees and efficient replica comparison](merkle-trees.md) | P2 | Merkle trees, hash trees, anti-entropy, replica comparison, Merkle proofs
[HyperLogLog and approximate cardinality](hyperloglog.md) | P2 | HyperLogLog, approximate cardinality, mergeable sketches
[Inverted indexes and search mechanics](inverted-indexes.md) | P2 | inverted indexes, posting lists, tokenization, search ranking

## Checkpoint

Complete the [section checkpoint](CHECKPOINT.md) without opening the chapters, then revisit weak explanations.

[Roadmap](../ROADMAP.md) · [Progress](../PROGRESS.md) · [Exercises](../EXERCISES.md)
