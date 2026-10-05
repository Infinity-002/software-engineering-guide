# Tenancy, audit, deletion, and concurrency

Production data has ownership, history, lifecycle, and competing writers. These patterns make those concerns explicit. Each must be enforced at a boundary all relevant callers share, not only in one convenient UI path.

## Pattern 1: multi-tenancy

**Problem/naive failure.** Several workspaces share infrastructure. Filtering by `workspace_id` in most queries seems sufficient until one endpoint, cache key, background job, or export omits it and leaks data.

**Mechanism/example.** Carry verified tenant context through authorization, queries, cache keys, object keys/policies, and events. Use composite constraints where they prevent cross-tenant references. PostgreSQL row-level security can add defense in depth when correctly configured, but privileged roles, connection context, and policy composition must be understood. Separate schemas/databases or dedicated deployments provide stronger operational isolation at higher management cost.

**Failures/trade-offs.** A pooled connection can retain stale tenant context if setup/reset is wrong. Noisy tenants can exhaust shared pools even when data isolation is correct. Per-tenant encryption, residency, export, and deletion requirements affect architecture. Use pooled tenancy for efficient shared workloads with enforceable boundaries; choose stronger separation for concrete isolation requirements. Do not create a database per tiny tenant without accounting for migrations, connections, and operations.

## Pattern 2: soft deletion

**Problem/naive failure.** Users need undo or retention, so developers add `deleted_at` and assume deletion is solved. Lists filter it, but search, uniqueness checks, joins, and authorization paths still expose deleted data.

**Mechanism/example.** Define lifecycle states and default visibility, record deletion intent/time/actor, and propagate deletion to projections and object cleanup. A partial unique index may enforce uniqueness only among active rows if reuse is the intended rule. Restoration must recheck conflicts and permissions rather than blindly clearing the timestamp.

**Failures/trade-offs.** Soft-deleted personal data still exists and may remain in backups. Unbounded retention grows storage and query complexity. Cascades become explicit lifecycle workflows. Use soft deletion for genuine recovery/audit requirements with a final purge policy; avoid it as an automatic substitute for well-defined hard deletion or legal retention decisions. Product/legal requirements determine retention; the pattern does not decide them.

## Pattern 3: audit logs

**Problem/naive failure.** Debug logs are treated as a record of who changed permissions. Sampling, rotation, missing fields, and mutable log access make them unreliable for accountability.

**Mechanism/example.** Record principal, action, resource, outcome, relevant before/after facts, and trustworthy context under a defined retention/access policy. For database changes requiring atomic audit, insert the audit record in the same transaction or use a reliable change-capture/outbox path with clear guarantees. Protect append integrity and restrict who can read sensitive history.

**Failures/trade-offs.** Logging raw secrets creates a second breach surface. A compromised writer may forge actor fields unless identity provenance is controlled. Hash chaining can reveal some tampering only if trusted checkpoints are preserved; it does not make every event truthful. Use audit logs for accountable business/security events. Do not turn every debug message into permanent audit data or adopt event sourcing solely for an audit requirement.

## Pattern 4: optimistic locking

**Problem/naive failure.** Two editors read version 8 and each saves a full task. Last write wins silently erases the earlier editor's changes.

**Mechanism/example.** Include `expectedVersion=8`; atomically update only if the stored version still equals 8 and increment it. A conflict returns current context or a reload/merge path. HTTP validators such as `If-Match` can express a similar conditional contract at the API boundary.

**Failures/trade-offs.** Blind automatic retries with the new version defeat conflict protection. High contention causes repeated aborts and user frustration. Versions must cover the actual invariant; one row version does not protect an unrelated aggregate constraint. Use optimistic locking for relatively infrequent conflicts and user edits where stale intent matters. Avoid it alone for a hot shared counter that can use an atomic increment or for cross-row invariants it does not cover.

## Pattern 5: pessimistic locking

**Problem/naive failure.** A workflow reads shared state, makes several dependent updates, and discovers conflicts too late. Locking only in application memory fails across API replicas.

**Mechanism/example.** Acquire the appropriate database row locks within a transaction, validate current state, update, and commit promptly. A transfer can lock involved accounts in stable ID order before applying debits/credits. Locks must cover the invariant, including predicate/absence issues through constraints or stronger coordination where needed.

**Failures/trade-offs.** Deadlocks, long waits, lock escalation in some engines, and abandoned long transactions reduce throughput. Never hold locks while waiting for human input or an unrelated network call. Use pessimistic locking for short contested critical sections where waiting is preferable to repeated conflicts. Avoid it as a broad default around every read, especially when MVCC and atomic SQL already suffice.

## Pattern 6: feature flags

**Problem/naive failure.** A risky feature can only be disabled by redeploying. Adding a global boolean helps until it becomes an undocumented permanent dependency with unsafe defaults.

**Mechanism/example.** A flag has an owner, default, targeting rule, rollout/kill-switch purpose, audit trail, and removal date/condition. Relay enables a new search projection for a stable cohort, compares errors/latency, then expands. Evaluate entitlements authoritatively; a client-visible flag only controls presentation.

**Failures/trade-offs.** Flag-service outage, inconsistent evaluations, stale cached rules, and interacting flags create unexpected states. Choose safe defaults and bounded caching, and ensure the kill switch can operate during the failure it is meant to mitigate. Use flags for gradual exposure and operational control; avoid permanent branching when a simpler configuration or product model expresses the stable distinction.

## Exercises

1. **Design:** Trace tenant identity through SQL, Redis, object storage, search, and a queue event.
2. **Predict:** A soft-deleted username is reused, then the old account is restored. Which invariant decides the outcome?
3. **Implementation:** Test optimistic conflict handling and a pessimistic two-row transfer under concurrent requests.
4. **Debug:** An audit record says an administrator changed a task, but `actorId` came from the request body. Repair identity provenance.
5. **Interview:** Compare undo, audit, event sourcing, and backups as distinct data-history requirements.

<details><summary>Review criteria</summary>

Each pattern includes lifecycle cleanup and failure behavior. Tenant context derives from verified membership. Conflict handling preserves user intent. Audit fields are trustworthy and minimized. Flags have a safe failure policy and an end to their lifecycle.

</details>

## Further reading and connections

[PostgreSQL row security](https://www.postgresql.org/docs/current/ddl-rowsecurity.html), [OWASP logging](https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html), [PostgreSQL explicit locks](https://www.postgresql.org/docs/current/explicit-locking.html), and [OpenFeature concepts](https://openfeature.dev/docs/reference/intro/). Connect to [transactions](../06-databases/transactions-and-mvcc.md), [security](../08-security/trust-and-authorization.md), [CQRS](cqrs-and-event-sourcing.md), and [delivery](../18-ci-cd/safe-delivery.md).
