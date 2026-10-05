# Merkle trees and efficient replica comparison

Two replicas hold millions of records. Comparing every record across the network after every interruption is expensive, while comparing only row counts misses changed values. A Merkle tree summarizes content recursively so equal regions can be skipped and differing regions investigated.

## Hash content, then hash the summaries

Each leaf contains a hash of a record or block. Each parent contains a hash derived from its children, continuing to one root. The exact encoding, ordering, partitioning, and node types are part of the protocol. Use unambiguous encodings and domain separation so a leaf cannot be confused with an internal-node encoding.

```text
                 root = H(left, right)
                    /             \
              H(hA, hB)         H(hC, hD)
               /    \            /    \
             h(A)  h(B)        h(C)  h(D)
```

Changing C changes h(C), its parent, and the root. It does not change A/B's subtree. A balanced tree therefore updates only a path for one leaf change, though dynamic insertion can also alter shape depending on the construction.

## Compare replicas by descending into disagreement

First exchange root hashes. If they match under the same structure, canonical encoding, and collision-resistant hash assumptions, treat the represented contents as equal with cryptographic confidence. If they differ, compare child hashes. Skip equal subtrees and recursively inspect differing ones until the divergent ranges/records are found.

For sparse changes, this can transfer far less data than a full comparison. If almost everything differs, the tree adds metadata overhead and a full streaming comparison may be competitive. The benefit depends on how often comparison happens and how localized changes are.

In a distributed key-value store, leaves may summarize key ranges rather than one record each. Tree boundaries must align across replicas. Hashing the same records into different ranges or serializing fields in different orders yields different roots without any business-data disagreement.

## Proofs establish inclusion under a trusted root

A Merkle proof for C contains the sibling hashes needed to recompute the path to the root. The verifier hashes C, combines it with h(D), then with the A/B subtree summary. If the result matches an independently trusted root, the proof establishes inclusion under that commitment and construction.

The proof does not establish that C is true, authorized, fresh, or the latest version. A malicious source can provide a self-consistent tree containing fabricated data if the verifier also trusts the root supplied by that source. Root distribution and signatures/checkpoints form a separate trust problem, as in transparency systems.

## Anti-entropy still needs a version policy

Hash disagreement locates a difference; it does not decide which value wins. Replicas need versions, causal metadata, tombstones, or domain merge rules. A deletion must remain represented long enough to prevent an old replica from reintroducing the removed value. See [replication repair](../10-distributed-systems/replication-and-quorums.md).

Build trees from a consistent snapshot or account for concurrent mutation. Otherwise one replica may hash a mixture of moments while another hashes a different mixture, producing repeated disagreement that is hard to interpret. Maintenance cost competes with foreground traffic, so repair should be paced and observable.

## Failure modes and trade-offs

A corrupted cached internal hash can falsely describe its subtree until recomputed; integrity mechanisms and rebuild procedures matter. Hash algorithm changes require versioning and coordinated comparison. Extremely skewed range partitions can make one differing leaf represent a huge repair transfer. Too fine a tree consumes more metadata; too coarse a tree saves less bandwidth.

Hashes are not encryption. They reveal equality, and low-entropy inputs can be guessed. Cross-tenant content deduplication can leak that two users possess the same content even without revealing the bytes. A content-addressed design must consider that privacy boundary separately.

Use Merkle trees for repeated comparison of large replicated/content-addressed datasets or efficient inclusion proofs. Do not add one to a tiny table where a version number or direct scan is simpler. Do not use a matching root as proof of current authorization or as a replacement for a consensus decision about authority.

## Exercises

1. **Implementation:** Build the four-leaf tree, change one leaf, and list exactly which hashes change.
2. **Predict:** Two trees contain the same records in different orders. Must their roots match? State the construction assumptions.
3. **Design:** Compare replicas while writes continue and define the snapshot/version boundary.
4. **Debug:** A deleted record reappears after repair. Explain why the tree correctly detected a difference but the merge policy was wrong.
5. **Interview:** Explain a Merkle proof and why the verifier must trust the expected root independently.

<details><summary>Hints</summary>

Tree shape, order, encoding, and hash version define the commitment. Repair needs a rule for authoritative or concurrent versions. A proof verifies a relationship to a root, not the honesty or freshness of the root itself.

</details>

## Further reading and connections

[Dynamo anti-entropy](https://www.allthingsdistributed.com/files/amazon-dynamo-sosp2007.pdf), [RFC 9162](https://www.rfc-editor.org/rfc/rfc9162), and [Git object model](https://git-scm.com/book/en/v2/Git-Internals-Git-Objects). Connect to [hashing](../01-foundations/data-and-time.md), [logical time](../10-distributed-systems/logical-time.md), and [Drive-style storage](../19-system-design/advanced-designs.md).
