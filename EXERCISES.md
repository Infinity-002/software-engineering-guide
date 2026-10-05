# Exercise guide

Every teaching chapter ends with exercises and a folded hint/rubric. Every major section has a checkpoint. This page organizes practice by the evidence it produces; the [coverage index](COVERAGE.md) locates individual concepts and [PROGRESS.md](PROGRESS.md) tracks demonstrated understanding.

## A study loop

1. **Check your understanding:** explain the mechanism from memory, including its assumptions.
2. **Predict what happens:** draw an execution history before running code.
3. **Debug this:** list competing hypotheses and choose a discriminating observation.
4. **Design exercise:** protect one explicit invariant under a stated workload/failure model.
5. **Implementation exercise:** build the smallest experiment that tests the mechanism.
6. **Interview question:** explain the result clearly, then answer a changed-condition follow-up.

Keep answers hidden until you have a prediction. A failed experiment is useful evidence when you explain why your model was wrong. Record environment, workload, observation, and limits so results are reproducible.

## Mechanism lab sequence

Lab | Priority | Starting material | Required evidence
--- | --- | --- | ---
Bounded producer/consumer | P0 | [Concurrency](01-foundations/concurrency-and-io.md) | Queue age and memory remain bounded under overload
Browser task/microtask ordering | P0 | [JavaScript](04-frontend/javascript-runtime.md) | Predicted ordering and explanation of starvation
Runtime input parser | P0 | [TypeScript](04-frontend/typescript-boundaries.md) | Invalid bytes rejected despite compile-time types
Out-of-order search | P0 | [Server state](04-frontend/state-and-data-fetching.md) | Old response cannot replace current results
Two-session lost update/write skew | P0 | [PostgreSQL lab](labs/postgres-concurrency.md) | Reproduction plus multiple justified repairs
Query plan before/after index | P0 | [Indexes](06-databases/indexes-and-query-plans.md) | Actual rows, estimates, buffers, and write cost
Cache stale-fill race | P1 | [Cache design](07-caching/cache-design.md) | Timeline and version/freshness repair
Worker crash before ack | P1 | [Queues](09-messaging-streaming/queues-and-workers.md) | Redelivery without repeated protected effect
Bloom membership/sizing | P1 | [Runnable models](labs/README.md) | No inserted misses and measured false positives
Token bucket | P1 | [Runnable models](labs/README.md) | Burst/refill/capacity and clock tests
Stale lease holder | P2 | [Runnable models](labs/README.md) | Rejection after newer fence plus documented pre-fence limitation
Merkle proof and replica difference | P2 | [Merkle trees](11-system-data-structures/merkle-trees.md) | Trusted-root proof and version-aware repair
Slow-request trace | P1 | [Observability](14-observability/logs-metrics-traces.md) | Critical path, pool wait, and browser/server boundary
Restore drill | P1 | [Recovery](13-reliability/resilience-and-recovery.md) | Verified data plus measured full recovery time
Mixed-version migration | P1 | [CI/CD](18-ci-cd/safe-delivery.md) | Old/new compatibility and safe recovery

The runnable models need only Python 3.11+. Application labs use a disposable Node/React/PostgreSQL/Redis environment built during the projects. Do not run destructive or high-load experiments against real services. That constraint follows the exercise's need for controlled evidence and reproducibility.

## Project progression

Complete [Production CRUD API](projects/01-production-crud-api.md) **P0**, [Full-stack Relay](projects/02-full-stack-relay.md) **P1**, [Background processing](projects/03-background-processing.md) **P1**, [Real-time chat](projects/04-realtime-chat.md) **P1**, and [Scalable service](projects/05-scalable-service.md) **P2**. Each includes prerequisites, milestones, failure experiments, and acceptance criteria.

## Design and interview practice

Work through four [beginner designs](19-system-design/beginner-designs.md) **P0**, six [intermediate designs](19-system-design/intermediate-designs.md) **P1**, and eight [advanced designs](19-system-design/advanced-designs.md) **P2**. Each design has a specific adversarial exercise. Use the [question bank](22-interview-preparation/reasoning-interviews.md) and [four timed mocks](22-interview-preparation/mock-interviews.md) **P1** after you have implementation evidence.

## Assessment rubric

Score 0 for names without mechanism, 1 for a correct happy path, 2 for a concrete failure and justified repair, and 3 for assumptions, trade-offs, and validation. Pass a checkpoint only when each question reaches 2 and its evidence exists. P2/P3 material is advanced, not optional in roles whose responsibilities depend on those guarantees.

<details><summary>How to use hints without memorizing them</summary>

Compare your history with the rubric's invariant and boundary. If you missed one, construct a new example with different timing or data rather than copying the answer. A useful correction states: “I assumed X; this observation shows Y; the guarantee actually requires Z.” Revisit the concept after a delay and explain it again without the rubric.

</details>
