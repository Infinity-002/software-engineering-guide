# Relational modeling and SQL

Relay starts with a JSON object per workspace containing users, tasks, and comments. Editing one user's display name now requires changing many copies. Two writes can overwrite each other's unrelated changes. The relational model gives facts explicit structure and lets constraints express relationships the database can enforce under concurrency.

## Model facts and invariants

A table represents a kind of fact. Rows are instances; columns have domains and meanings. A primary key identifies a row. A foreign key constrains a reference to another table. A unique constraint expresses an identity rule, while `NOT NULL` and `CHECK` restrict acceptable values.

```sql
CREATE TABLE workspaces (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  name text NOT NULL CHECK (length(name) BETWEEN 1 AND 120)
);
CREATE TABLE tasks (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  workspace_id bigint NOT NULL REFERENCES workspaces(id),
  title text NOT NULL CHECK (length(title) BETWEEN 1 AND 120),
  status text NOT NULL CHECK (status IN ('open', 'done')),
  version bigint NOT NULL DEFAULT 1,
  created_at timestamptz NOT NULL DEFAULT now()
);
```

The schema establishes structural validity, not authorization. Any permitted database caller could still edit the wrong workspace unless queries and access policy enforce tenancy. For relationships across tenant-owned tables, composite keys/foreign keys can prevent cross-workspace references. An application-only “check then insert” cannot safely replace a unique constraint under concurrent requests.

## Normalization prevents update anomalies

Suppose every task stores the workspace name. Renaming a workspace requires many updates; partial failure leaves inconsistent names. Store the workspace identity on each task and its name once. Normalization organizes attributes around the facts they depend on. First normal form concerns relational values rather than repeating groups; later forms address dependencies that cause redundancy. The useful question is: “If this fact changes, how many places must be updated consistently?”

Denormalization deliberately duplicates or precomputes data for a measured access pattern. A task-count summary can make reads cheap, but now every create/delete must maintain it or an asynchronous projection must tolerate lag. Record the authority, update mechanism, and repair procedure. Do not call accidental duplication “denormalization” after inconsistencies appear.

## Queries combine facts

An inner join retains matching rows; a left join preserves the left side even without a match. Filters placed in `WHERE` after a left join can accidentally remove unmatched rows, effectively changing intended behavior. SQL uses three-valued logic around `NULL`: comparisons such as `x = NULL` do not work as ordinary equality; use `IS NULL` and define what absence means.

```sql
SELECT w.id, w.name, count(t.id) AS open_tasks
FROM workspaces AS w
LEFT JOIN tasks AS t
  ON t.workspace_id = w.id AND t.status = 'open'
GROUP BY w.id, w.name
ORDER BY w.id;
```

The filter in the join preserves workspaces with zero open tasks. `count(t.id)` counts matched non-null task IDs, while `count(*)` would count the preserved workspace row too. This is a semantic difference, not a performance tweak.

Use parameterized values. SQL identifiers such as sort-column names usually cannot be supplied through ordinary value placeholders; map user choices to a fixed allowlist. An ORM can reduce repetitive mapping, but generated queries still need inspection for joins, N+1 requests, transaction boundaries, and data-volume behavior.

## Data modeling is workload-aware

Choose types that express the domain: time-zone-aware instants for events, explicit currency and decimal/minor-unit rules for money, bounded state transitions where possible. Avoid a universal key/value table that moves every constraint into application code unless flexible attributes are actually required. JSON columns can hold evolving peripheral data while relational columns enforce core relationships.

Deletion requires a policy. Cascading child deletion can be right for disposable dependent rows but dangerous for audit or financial records. Soft deletion changes every visibility query and uniqueness rule. Large deletions create storage and maintenance work even when the logical operation is one statement.

Why not add every conceivable constraint immediately? Constraints should encode stable truths; rules that depend on external systems or complex temporal context may require application coordination. Still, use the database for invariants it can enforce directly, because all concurrent writers share that authority.

## Exercises

1. **Design:** Add users, memberships, and comments. Prevent a comment from referencing a task in a different workspace.
2. **Predict:** Move `t.status = 'open'` from the join to `WHERE`. Which workspaces disappear?
3. **Debug:** Two requests both see no existing membership and insert duplicates. Fix the schema and caller behavior.
4. **Implementation:** Write aggregate queries for open tasks per workspace and latest comment per task; inspect their behavior on empty groups.
5. **Interview:** Give one justified denormalization and its repair strategy.

<details><summary>Hints</summary>

Use a uniqueness constraint on membership identity and handle conflicts. Cross-tenant relationships can include `workspace_id` in referenced unique keys. A summary table needs a source of truth and a rebuild/reconciliation procedure.

</details>

## Further reading and connections

[PostgreSQL constraints](https://www.postgresql.org/docs/current/ddl-constraints.html), [table expressions](https://www.postgresql.org/docs/current/queries-table-expressions.html), and [data types](https://www.postgresql.org/docs/current/datatype.html). Continue to [indexes](indexes-and-query-plans.md), [transactions](transactions-and-mvcc.md), and [tenancy](../20-production-patterns/data-lifecycle-and-tenancy.md).
