# Indexes and query execution

A task query takes 20 ms at 100,000 rows and three seconds at 50 million. Adding memory or a random index may help accidentally, but the durable skill is explaining how the engine finds rows and why it chose that path.

## An index spends write work to save read work

Without a suitable access path, finding a few matching rows may require scanning the table. An index stores a separately organized representation of keys and row references. A B-tree-style index supports equality and ordered ranges through high fanout and balanced depth; [B+ trees](../11-system-data-structures/b-plus-trees.md) explains the page mechanics.

An index lookup is not free: traverse index pages, locate matching entries, and often fetch table pages. If most rows qualify, a sequential scan may be cheaper than many scattered lookups. “An index exists” does not imply “the planner should use it.” Selectivity concerns how much data a predicate filters; cardinality can mean distinct values or estimated row counts depending on context, so state which you mean.

## Design the index around a query

```sql
CREATE INDEX tasks_workspace_created
ON tasks (workspace_id, created_at DESC, id DESC)
INCLUDE (title, status);
```

For `WHERE workspace_id = ? ORDER BY created_at DESC, id DESC LIMIT 20`, the leading equality groups the relevant workspace entries, and the remaining order supports a bounded scan. Composite B-tree indexes are ordered lexicographically. Leading constraints often most effectively narrow the scanned range; predicates on later keys may still help, and implementations can support skip-scan optimizations. Avoid turning the “leftmost prefix” heuristic into an absolute ban on every other use. PostgreSQL documents these details in [multicolumn indexes](https://www.postgresql.org/docs/current/indexes-multicolumn.html).

Included columns can make a covering access path possible without using those columns for tree ordering. In PostgreSQL, an index-only scan also depends on visibility information; containing every requested column does not guarantee zero heap access. Wide included values increase index size and write work.

Clustered storage means row organization follows an index-like key structure in some engines. PostgreSQL's ordinary tables are heaps with separate indexes; its `CLUSTER` operation reorders a table at that time and does not continuously maintain that order. Do not transfer one engine's clustered-index assumptions to another.

## The planner estimates competing plans

The engine parses SQL, resolves names/types, rewrites where applicable, estimates possible access/join strategies, and executes a chosen plan. Statistics summarize distributions; stale statistics or correlations not captured by the model can produce bad estimates.

Nested-loop joins repeatedly probe an inner input and work well with a small outer input and useful index. Hash joins build a hash structure for an input and probe it, often useful for larger equality joins; memory limits can cause spilling. Merge joins exploit sorted inputs and suit ordered equality matching. No join algorithm is universally best.

```sql
EXPLAIN (ANALYZE, BUFFERS)
SELECT id, title
FROM tasks
WHERE workspace_id = 42
ORDER BY created_at DESC, id DESC
LIMIT 20;
```

`ANALYZE` executes the query. Be especially careful with mutations and costly queries; a rollback does not undo every external effect a function might trigger. Compare estimated and actual rows, loop counts, sort/spill behavior, buffer activity, and total time. Node times can include child work, so adding every displayed duration can double-count time. A warm-cache test differs from a cold-cache production path.

## Why indexes slow writes

An insert must maintain relevant index entries as well as table data. Updates to indexed values can create new entries and page splits. Deletes and MVCC cleanup create maintenance work. More structures generate more WAL, occupy cache, and amplify storage writes. Indexing every field can reduce overall throughput and crowd out useful pages.

A partial index stores only rows satisfying a predicate, such as open tasks, when queries can use that condition. An expression index can help searches over a computed value, but queries must use compatible expressions and semantics. Search substrings, full text, spatial data, and document fields may require specialized index types rather than a generic B-tree.

## A disciplined investigation

Capture the actual SQL and parameter distribution. Check whether the regression is query execution, pool wait, locks, storage latency, or transferred result size. Compare plans at realistic volume. Inspect missing filters, N+1 loops, functions/casts that change index usability, deep offsets, wide rows, and sorts. Change one factor, measure write cost too, and plan safe index creation for a live system.

## Exercises

1. **Design:** Choose an index for workspace/status filtering with newest-first pagination. Explain column order and the cost of including a large description.
2. **Predict:** Why might an index help one small workspace and hurt a query selecting 80% of all tasks?
3. **Implementation:** Compare plans before/after an index on realistic skewed data. Record estimates, actual rows, and buffers.
4. **Interview:** Explain why a database index improves some reads while making writes slower.

<details><summary>Hints</summary>

Consider equality prefixes, range/order requirements, and data skew. A scan reading most pages sequentially can beat random heap access. The best index is the one that pays for its maintenance across the actual workload, not the one with the most columns.

</details>

## Further reading

[PostgreSQL EXPLAIN](https://www.postgresql.org/docs/current/using-explain.html), [index-only scans](https://www.postgresql.org/docs/current/indexes-index-only-scans.html), and [planner statistics](https://www.postgresql.org/docs/current/planner-stats.html). Connect to [storage](storage-and-recovery.md) and [API pagination](../05-backend/api-design.md).
