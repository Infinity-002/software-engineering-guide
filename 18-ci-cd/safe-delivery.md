# CI/CD, migrations, and safe releases

A change is not complete when it compiles. It must become a traceable artifact, run with compatible data and configuration, survive mixed versions, and be reversible or recoverable when assumptions fail. Delivery engineering controls how uncertainty reaches users.

## Build one artifact and promote it

```text
reviewed source -> dependency resolution -> lint/type checks/tests
  -> build -> package/container -> immutable artifact + provenance
  -> staging verification -> controlled production rollout
  -> user-outcome checks -> expand or roll back
```

Use small reviewed changes and a source-control workflow that keeps integration frequent. Long-lived branches accumulate conflicts and delay feedback. CI should run required checks reproducibly from clean inputs, with locked dependencies where appropriate. Cache dependencies/build outputs safely without allowing untrusted branches to poison privileged release artifacts.

Promote the same tested artifact digest through environments and inject environment-specific configuration separately. Rebuilding for production can introduce different dependencies or build-time settings. Record commit, build identity, dependency inventory, and artifact digest so an incident can identify exactly what runs.

## Tests and supply-chain boundaries

Lint/type checks catch local errors; unit and integration tests protect behavior; contract checks detect compatibility regressions; critical E2E tests validate deployment wiring. Security scanning and dependency review add evidence but do not prove absence of vulnerabilities. A signed artifact proves something about provenance under a key policy, not that the code is safe.

CI often has powerful credentials. Restrict untrusted pull-request execution from secrets and release permissions. Prefer short-lived federated deployment identity, least privilege, and separated build/deploy roles. Pin and review third-party automation dependencies according to risk. Logs and test artifacts can leak secrets just as application logs can.

## Schema migrations require mixed-version design

Suppose `tasks.title` becomes `tasks.summary`. Renaming immediately breaks old API replicas still serving requests. Expand first: add the new representation compatibly, deploy code supporting both, backfill in bounded batches, verify consistency, switch readers/writers, then remove the old field after all consumers are gone.

Backfills should checkpoint progress, limit load, and tolerate retries. Concurrent writes during a backfill need a version/dual-write/derivation policy so old data does not overwrite newer values. Large indexes and constraints can lock or scan heavily; use engine-supported online/concurrent mechanisms where appropriate and understand their failure cleanup.

Application rollback cannot undo lost data from a destructive migration. Prefer forward-compatible schema changes and a tested roll-forward repair path. Take backups where needed, but restoring an entire database can discard unrelated newer writes; it is not a casual rollback button.

## Deployment strategies change exposure

Rolling deployment gradually replaces instances and temporarily mixes versions. Blue-green maintains two environments and switches traffic, giving a clear application rollback point but requiring extra capacity and shared-data compatibility. Canary exposes a small traffic population first and expands based on meaningful signals; choose representative cohorts so the canary does not miss the risky workload.

Compare error rate, latency, saturation, and business outcomes against a baseline. Low traffic can make percentages noisy. A canary must have a stop/rollback criterion and sufficient observation time for delayed effects such as queue processing or cache expiry. “Pods are ready” is necessary but not sufficient.

## Feature flags separate deployment from exposure

A flag can keep code deployed but inactive, enable a cohort, or disable optional behavior quickly. Define owner, default, targeting, audit, and expiry/removal plan. Evaluate sensitive entitlement server-side; a client flag is not authorization. Flag-service failure needs a safe cached/default policy.

Flags create combinations. Two individually tested flags may interact badly. Limit long-lived complexity, test relevant combinations, and remove flags once the decision is permanent. A kill switch should avoid requiring the broken subsystem to function before it can be turned off.

## Release recovery and graceful shutdown

Old instances must stop receiving fresh work and drain safely. Jobs and WebSockets can outlive ordinary request windows, so define reconnection/redelivery behavior. Reverting a container image may still leave new events, schema, or data that the old code cannot understand. Verify backward readability before calling rollback safe.

After rollback, check user outcomes and backlog recovery, not only deployment status. Preserve evidence of the failed version and migration state. A deployment runbook should say who owns the decision, how to stop expansion, what data changes occurred, and how success is verified.

## Exercises

1. **Design:** Plan the `title` to `summary` migration with mixed API versions and concurrent edits.
2. **Predict:** A canary passes for five minutes but fails after an hour. Name cache, queue, and traffic-pattern causes.
3. **Implementation:** Build a pipeline that records an immutable artifact digest and runs a smoke journey before expanding traffic.
4. **Debug:** Rollback restores code but errors continue because new events use an unsupported enum. Propose compatibility and recovery changes.
5. **Interview:** Explain why deployment, release, migration, and rollback are related but distinct operations.

<details><summary>Hints</summary>

Every old/new combination that can coexist needs a compatibility story. Delayed consumers and cached representations extend the coexistence window. A feature flag needs operational ownership and a removal condition, not just an SDK call.

</details>

## Further reading and connections

[Google SRE release engineering](https://sre.google/sre-book/release-engineering/), [SLSA supply-chain framework](https://slsa.dev/), and [PostgreSQL concurrent index creation](https://www.postgresql.org/docs/current/sql-createindex.html). Connect to [testing contracts](../05-backend/testing-and-evolution.md), [SLOs](../14-observability/slos-and-alerting.md), and [feature flags](../20-production-patterns/data-lifecycle-and-tenancy.md).
