# Transactions, isolation, and MVCC

Two requests each read a balance of 100, subtract 30, and write 70. Both requests are individually sensible, but together they lose one debit. A transaction groups work; the isolation model determines what concurrent transactions can observe and how conflicts are handled.

## ACID names four different responsibilities

Atomicity means the transaction's database changes commit together or are rolled back. Consistency means transactions preserve declared invariants when their logic and constraints are correct; it is not the same meaning as replica consistency. Isolation constrains interference among concurrent transactions. Durability means acknowledged commits survive the failures covered by the configured storage/replication contract.

A transaction does not atomically include an arbitrary email or payment-provider call. If the database commits and the process crashes before sending an event, an ordinary SQL transaction cannot finish the external action. [Outbox and sagas](../20-production-patterns/outbox-inbox-and-sagas.md) address those boundaries.

## Different anomalies need different explanations

| Anomaly | Example |
|---|---|
| Dirty read | Read another transaction's uncommitted change, then it aborts |
| Non-repeatable read | Read the same row twice and see a committed change between reads |
| Phantom read | Repeat a predicate query and get a changed matching set |
| Lost update | Two read-modify-write operations overwrite one another |
| Write skew | Two transactions read a shared condition and update different rows, jointly breaking it |

Write skew is especially instructive. Two doctors are on call. Each transaction sees the other doctor on call and takes its own doctor off call. They write different rows, so avoiding same-row overwrite is insufficient. Both committing leaves nobody on call.

## MVCC makes reading a versioned decision

Multi-version concurrency control retains row versions and uses visibility rules to decide which versions a snapshot can see. Readers can often proceed without blocking writers merely to see a stable committed version. Writers still conflict, locks still exist, and old versions require cleanup. Long-lived transactions can retain old snapshots and prevent efficient reclamation.

In PostgreSQL, Read Committed gives an ordinary statement a fresh committed snapshot. Repeatable Read uses a transaction snapshot and prevents several read anomalies but can still allow serialization anomalies such as write skew. Serializable uses additional conflict detection and can abort transactions that must be retried. PostgreSQL's Read Uncommitted behaves as Read Committed, and its Repeatable Read is stronger than the SQL standard's minimum regarding phantoms. These implementation-specific guarantees are described in [transaction isolation](https://www.postgresql.org/docs/current/transaction-iso.html).

Do not infer guarantees from isolation-level names alone across engines. Serializable means results correspond to some serial execution; it does not inherently impose real-time ordering across all external observations, nor make a transaction faster.

## Protect the invariant directly

For a single bounded debit, an atomic conditional update is often enough:

```sql
UPDATE accounts
SET balance_minor = balance_minor - $2
WHERE id = $1 AND balance_minor >= $2
RETURNING balance_minor;
```

Validate that the debit is positive and use suitable exact numeric types. Zero returned rows means absent account or insufficient funds under this contract; distinguish externally only as appropriate. The engine coordinates concurrent updates rather than trusting an earlier application read.

For a workflow that must read then modify, pessimistic locking can acquire row locks with `SELECT ... FOR UPDATE` inside the transaction. All competing paths must obey the relevant locking discipline. Locking existing rows does not necessarily protect the absence of a row or an arbitrary predicate; use constraints, appropriate isolation, or a common guard row when justified.

Optimistic concurrency uses a version:

```sql
UPDATE tasks SET title = $3, version = version + 1
WHERE id = $1 AND version = $2
RETURNING version;
```

If zero rows change, the caller's view is stale or the row is absent. The caller must decide whether to merge, reload, or reject. Automatically retrying with the new version can silently discard the user's intent.

## Deadlocks, retries, and performance

Transactions A and B can each hold a row the other needs. The database detects many deadlocks and aborts a participant. Acquire resources in a consistent order, keep transactions short, and retry the whole transaction when the error is retryable. Replaying only the final statement can violate assumptions established by earlier reads.

Retries need bounded attempts, backoff, and idempotent external behavior. Do not send an email inside a transaction closure that may be rerun. Higher isolation can increase aborts under contention; lower isolation can shift more correctness work into application logic. Choose from invariants and measured conflict patterns, not “Serializable is always too slow” folklore.

## Exercises

1. **Predict:** Draw the two-doctor write-skew history. Why do independent row locks acquired only at update time fail to protect the invariant?
2. **Implementation:** Reproduce a lost update in two SQL sessions, then fix it with an atomic update, row lock, and version check.
3. **Debug:** A transaction is idle for an hour and table size grows. Connect snapshots to cleanup.
4. **Interview:** Explain three meanings of consistency: database invariants, replica visibility, and UI cache freshness.

<details><summary>Hints</summary>

The invariant spans both doctors. Serializable with retry, a shared locked guard, or another correctly designed coordination mechanism can protect it. MVCC reduces some blocking but creates version-retention obligations. None of these choices includes arbitrary external effects automatically.

</details>

## Further reading and connections

[PostgreSQL explicit locking](https://www.postgresql.org/docs/current/explicit-locking.html), [MVCC introduction](https://www.postgresql.org/docs/current/mvcc-intro.html), and [routine vacuuming](https://www.postgresql.org/docs/current/routine-vacuuming.html). Continue to [WAL](storage-and-recovery.md) and [distributed consistency](../10-distributed-systems/partial-failure-and-consistency.md).
