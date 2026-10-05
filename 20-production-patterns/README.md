# Production patterns

**Prerequisites:** [Backend and API engineering](../05-backend/README.md), [Databases](../06-databases/README.md), [Messaging and streaming](../09-messaging-streaming/README.md). **Roadmap level:** 3.

Read in this order; the checkpoint asks you to combine the ideas rather than repeat definitions.

Chapter | Priority | Concepts
--- | --- | ---
[Idempotency keys and deduplication](idempotency-and-deduplication.md) | P1 | idempotency keys, request fingerprints, deduplication, response replay, retry-safe effects
[Outbox, inbox, sagas, and distributed transactions](outbox-inbox-and-sagas.md) | P1 | transactional outbox, inbox pattern, saga, distributed transactions, two-phase commit, compensation
[CQRS and event sourcing](cqrs-and-event-sourcing.md) | P2 | CQRS, event sourcing, projection rebuilding, event evolution
[Gateways, BFFs, and service discovery](boundaries-and-routing.md) | P1 | API gateway, backend-for-frontend, service discovery, microservice boundaries, modular monolith
[Tenancy, audit, deletion, and concurrency](data-lifecycle-and-tenancy.md) | P1 | multi-tenancy, soft deletion, audit logs, optimistic locking, pessimistic locking, feature flag lifecycle

## Checkpoint

Complete the [section checkpoint](CHECKPOINT.md) without opening the chapters, then revisit weak explanations.

[Roadmap](../ROADMAP.md) · [Progress](../PROGRESS.md) · [Exercises](../EXERCISES.md)
