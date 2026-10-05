# B-trees and B+ trees

A balanced binary search tree gives logarithmic lookup in memory. Why do databases use wider trees? Storage reads operate on pages, so following one pointer per comparison can waste most of each fetched page. A wide tree spends a page read to choose among many children.

## Fanout reduces expensive levels

An internal node stores ordered separator keys and child references. If a page can hold hundreds of references, the tree can address a huge dataset in a few levels. With approximate fanout `f` and `N` entries, height grows roughly with `log_f(N)`, subject to occupancy and leaf capacity. The root and upper levels often remain cached, further reducing I/O.

```text
                 [ 30 | 70 ]
                /     |     \
       [10,20] <-> [30,40,60] <-> [70,80,90]
                    linked leaves
```

B-trees and B+ trees are families with implementation variations. In the common B+ model, internal nodes guide search and record entries live in leaves, with links supporting ordered scans. Internal nodes can therefore use compact separators rather than full records. Database documentation may call a B+-style implementation a “B-tree”; do not infer exact layout from the marketing name alone.

## Lookup and range scan

For key 40, compare against root separators, follow the middle child, and search its entries. For a range `[35,85]`, find the first qualifying leaf position and then traverse adjacent leaves until the upper bound. This reuses locality rather than restarting a root search for each result.

Secondary-index leaves may contain row identifiers rather than full rows. Fetching rows then adds table-page access. A covering index can avoid some lookups, subject to visibility rules in MVCC engines. A clustered organization keeps row data in key order under the engine's design, changing locality and secondary-reference trade-offs.

## Writes maintain structural invariants

Insert into the target leaf. If it has room, add the entry. If full, split it and insert a separator into the parent; splits can propagate upward and occasionally create a new root. Deletion can leave sparse pages; implementations may merge, redistribute, or defer cleanup. The tree remains balanced through explicit structural maintenance.

Page modifications require concurrency control. Engines use short-lived internal latches for structural memory safety and separate transaction mechanisms for user-visible isolation. A latch protecting a page is not the same thing as a transaction lock held to preserve a business invariant. Logging and recovery must make structural changes recoverable across crashes.

Sequential inserts can concentrate writes at one edge, creating a hotspot while benefiting locality. Random keys spread insertion locations but can increase page splits and scattered writes. Fill factors reserve space for future changes at the cost of a larger initial structure. The right setting depends on update patterns, not a universal “random IDs are bad” rule.

## Why not a binary tree or hash table?

A binary tree can be excellent in memory but has lower fanout and potentially many cache/page misses for disk data. A hash index is useful for equality access but does not naturally support ordered ranges and sorting. B+ trees balance point lookup, range scans, and incremental updates, which matches many relational workloads.

Why not index every field with one? Each tree consumes storage, cache, maintenance CPU, and WAL. Composite keys encode a particular ordering; one tree cannot efficiently satisfy every unrelated ordering. Query design and index design must be paired.

## Exercises

1. **Predict:** If fanout is approximately 200, why can a tree with millions of entries remain shallow? State why a rough height calculation is not an exact I/O count.
2. **Implementation:** Draw insertions into a tiny B+ tree with leaf capacity three, including a split that reaches the root.
3. **Design:** Compare equality lookup, ordered pagination, and prefix text search across B+ tree, hash table, and inverted index.
4. **Interview:** Explain page size, fanout, locality, and write amplification in one database-index example.

<details><summary>Hints</summary>

Cached upper levels, leaf occupancy, table fetches, and visibility checks alter actual I/O. Ordered pagination can scan neighboring leaves; arbitrary text search needs a matching key transformation or another index structure.

</details>

## Further reading and connections

[PostgreSQL B-tree implementation](https://www.postgresql.org/docs/current/btree.html), [SQLite file format](https://www.sqlite.org/fileformat.html), and [CMU database course materials](https://15445.courses.cs.cmu.edu/). Connect to [query plans](../06-databases/indexes-and-query-plans.md), [WAL](../06-databases/storage-and-recovery.md), and [LSM trees](lsm-trees.md).
