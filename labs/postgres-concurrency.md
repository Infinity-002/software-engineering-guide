# PostgreSQL concurrency lab

Use a disposable local PostgreSQL database and two `psql` sessions connected to it. This lab changes only the explicitly created `se_lab` schema and its sample rows. It is an exercise to run in your own lab environment; the repository's Python model tests do not execute these SQL sessions.

## Setup

Run once in session A:

```sql
CREATE SCHEMA se_lab;
CREATE TABLE se_lab.accounts (
  id integer PRIMARY KEY,
  balance integer NOT NULL CHECK (balance >= 0),
  version integer NOT NULL DEFAULT 1
);
INSERT INTO se_lab.accounts (id, balance) VALUES (1, 100);
CREATE TABLE se_lab.doctors (
  id integer PRIMARY KEY,
  on_call boolean NOT NULL
);
INSERT INTO se_lab.doctors VALUES (1, true), (2, true);
```

If the schema already exists, use a fresh disposable database or inspect the existing lab state rather than deleting an unknown schema. Fully qualified names below keep the target explicit. Finish or roll back both sessions before resetting sample values between experiments.

## Experiment 1: lost update from an application-computed value

In both A and B, run:

```sql
BEGIN ISOLATION LEVEL READ COMMITTED;
SELECT balance FROM se_lab.accounts WHERE id = 1;
```

Both see 100 and independently compute `100 - 30 = 70`. In A:

```sql
UPDATE se_lab.accounts SET balance = 70 WHERE id = 1;
COMMIT;
```

After A commits, in B:

```sql
UPDATE se_lab.accounts SET balance = 70 WHERE id = 1;
COMMIT;
SELECT balance FROM se_lab.accounts WHERE id = 1;
```

The final balance is 70. PostgreSQL executed the requested assignments correctly; the application used an obsolete value. The transaction boundary alone did not express “subtract 30 from the latest balance.”

Reset in A after both transactions finish:

```sql
UPDATE se_lab.accounts SET balance = 100, version = 1 WHERE id = 1;
```

Now execute this transaction once in each session, overlapping if possible:

```sql
BEGIN;
UPDATE se_lab.accounts
SET balance = balance - 30, version = version + 1
WHERE id = 1 AND balance >= 30
RETURNING balance, version;
COMMIT;
```

One update can wait for the other. After both commit, balance is 40 and version is 3. The arithmetic and guard now operate at the authority. Generalize only with validated positive amounts and the correct domain invariant; this single-row example is not a complete transfer system.

## Experiment 2: optimistic conflict

Reset the sample balance/version after both sessions finish. Let both clients read version 1. In A, then B, attempt:

```sql
UPDATE se_lab.accounts
SET balance = 70, version = version + 1
WHERE id = 1 AND version = 1
RETURNING balance, version;
```

The first succeeds and the second returns no row. The stale assignment is detected rather than silently applied. A caller must choose to reload, merge, or reject; blindly substituting the new version and retrying the same stale value defeats the user-intent protection.

## Experiment 3: write skew under snapshot isolation

Ensure both doctors are on call, with no open transactions:

```sql
UPDATE se_lab.doctors SET on_call = true;
```

In both sessions, establish the snapshot before either updates:

```sql
BEGIN ISOLATION LEVEL REPEATABLE READ;
SELECT count(*) FROM se_lab.doctors WHERE on_call;
```

Both see two doctors, so each concludes it can remove its own doctor. In A:

```sql
UPDATE se_lab.doctors SET on_call = false WHERE id = 1;
```

In B:

```sql
UPDATE se_lab.doctors SET on_call = false WHERE id = 2;
```

Commit both, then count again. Both can commit because they changed different rows, leaving zero on call. Stable snapshots did not protect the cross-row invariant. Each transaction's decision depended on a fact the other changed.

Repeat after resetting both rows, replacing `REPEATABLE READ` with `SERIALIZABLE`. Preserve the same overlapping read-before-write schedule. Expect a serialization failure in one transaction, possibly during a statement or commit. Roll it back and retry the entire business operation from a fresh snapshot. The retry now sees only one doctor on call and should decline to remove the last one.

## Exercises and evidence

Record each session's statements, returned rows, waits, and errors. Explain why the second arithmetic update waits safely while the two-doctor invariant requires broader coordination. Add a shared guard row locked by both transactions and compare behavior with Serializable retry. Then reproduce the same histories through two API requests using a synchronization barrier in a test environment.

<details><summary>Review rubric</summary>

The lost-update fix moves computation into atomic state. Optimistic locking detects stale intent. Write skew spans multiple rows and requires a mechanism covering that invariant. A serialization retry repeats the decision from fresh reads and must not repeat irreversible external effects inside the retried closure.

</details>

## Further reading and connections

[Transactions and MVCC](../06-databases/transactions-and-mvcc.md), [backend integration testing](../05-backend/testing-and-evolution.md), and [PostgreSQL isolation documentation](https://www.postgresql.org/docs/current/transaction-iso.html). Continue with [Project 1](../projects/01-production-crud-api.md).
