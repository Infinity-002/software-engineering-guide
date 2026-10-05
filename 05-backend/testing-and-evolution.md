# Testing services and changing contracts

A backend can pass hundreds of mocked unit tests while losing updates in production. Tests need to exercise the boundary that owns the guarantee. If PostgreSQL enforces uniqueness, a fake repository returning `true` does not establish concurrent uniqueness.

## Build a risk-based portfolio

Pure unit tests are fast and useful for deterministic domain calculations. Integration tests use real dependencies where their semantics matter: transactions, constraints, serialization, and broker acknowledgement behavior. Contract tests verify what one component promises another. A few end-to-end tests connect deployed routing, identity, application logic, and persistence.

Choose test seams at meaningful boundaries. Inject a clock for expiration logic and a payment-provider interface for outcome simulation. Do not mock every internal function; doing so makes tests describe the current call graph rather than protect behavior through refactoring. Use isolated database schemas or disposable instances and stable fixtures, with explicit cleanup ownership.

## Test histories, not just inputs

For Relay task edits, two requests can both read version 4. A correct optimistic update lets at most one commit against that version. Write a test that deliberately synchronizes both reads before permitting updates. Merely starting two promises together does not guarantee the race was exercised.

```text
concurrency test (pseudocode)
  create task version 4
  client A and B both read version 4
  release both conditional updates
  assert exactly one succeeds
  assert final title belongs to the successful update
  assert loser receives an explicit conflict
```

Property tests generate many inputs to challenge an invariant, such as “pagination never returns an item twice under the documented immutable-order assumption.” Metamorphic tests check relationships: sorting twice should not change the result; replaying an idempotent operation should not add another effect. These tests are stronger than copying the implementation into the expected-value calculation.

## Schema and API evolution

A deployment is often a period when old and new versions coexist. Add a nullable field or compatible structure first, deploy code able to handle both, backfill in bounded batches, switch reads, and remove the old shape only after its users are gone. This expand-and-contract approach applies to databases, APIs, and events.

The producer's new event schema must coexist with old consumers. Optional additions may be safe, but changing semantics under the same field name is not. A schema registry can check structural compatibility within its configured rules; it cannot prove that “amount” kept the same unit. Contract tests should include older examples and unknown enum/field behavior.

Database migrations require realistic data-volume checks. Adding a constraint or rewriting a large table can block writes or exhaust storage. A rollback of application code does not reverse a destructive migration. Test both mixed-version operation and recovery, not just migration success on an empty database.

## Load tests are experiments

Define workload shape: endpoint mix, payloads, key distribution, think time, concurrency/arrival rate, cache warmth, and data volume. Uniform random keys can conceal hot-tenant problems. Closed-loop clients that wait for each response can reduce offered load when the server slows, hiding overload; understand the generator's model and coordinated-omission effects on latency measurement.

Measure throughput, latency distribution, error rate, queue/pool wait, CPU, memory, and dependency saturation. Increase load until a limit appears, then verify whether overload is bounded. A useful service degrades predictably rather than accepting infinite work until it crashes.

## Failure injection and judgment

Inject dependency delays, connection loss, duplicate delivery, process termination after commit, and expired credentials in a controlled environment. State the expected invariant before the experiment. A chaos experiment without a hypothesis and rollback path is just an outage.

Do not add tests that mirror trivial formatting or mechanically assert every method call. Spend effort on irreversible effects, concurrency, compatibility, and recovery. Keep test failures actionable: preserve the scenario seed, relevant logs, and version information without exposing secrets.

## Exercises

1. **Implementation:** Write a deterministic lost-update test and then protect the invariant with conditional SQL or locking.
2. **Design:** Plan a migration from one `name` field to separate fields while old clients remain active.
3. **Debug:** A load test reports good latency while production collapses during a burst. Compare arrival models and key distributions.
4. **Interview:** What does a passing contract test prove, and what semantic bugs can it miss?

<details><summary>Review criteria</summary>

Tests exercise the owning dependency, synchronize races deliberately, and specify mixed-version behavior. Compatibility includes meaning, not just JSON shape. A load test reports its traffic model and saturation point rather than one impressive request-rate number.

</details>

## Further reading and connections

[PostgreSQL testing documentation](https://www.postgresql.org/docs/current/regress.html), [Pact contract testing](https://docs.pact.io/), and [Grafana k6 concepts](https://grafana.com/docs/k6/latest/using-k6/). Connect to [safe delivery](../18-ci-cd/safe-delivery.md), [frontend tests](../04-frontend/testing.md), and [idempotency](../20-production-patterns/idempotency-and-deduplication.md).
