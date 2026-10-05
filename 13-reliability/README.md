# Reliability engineering

**Prerequisites:** [Backend and API engineering](../05-backend/README.md), [Messaging and streaming](../09-messaging-streaming/README.md), [Distributed systems](../10-distributed-systems/README.md). **Roadmap level:** 5.

Read in this order; the checkpoint asks you to combine the ideas rather than repeat definitions.

Chapter | Priority | Concepts
--- | --- | ---
[Bounding failure and recovering service](resilience-and-recovery.md) | P1 | timeouts, retry storms, exponential backoff, jitter, circuit breakers, bulkheads, load shedding, graceful degradation, health checks, readiness vs liveness, redundancy, disaster recovery, backups, RPO, RTO
[Rate limiting, fairness, and admission control](rate-limiting.md) | P1 | fixed window, sliding window log, sliding window counter, token bucket, leaky bucket, distributed rate limiting, Redis rate limiting, fairness, burst handling

## Checkpoint

Complete the [section checkpoint](CHECKPOINT.md) without opening the chapters, then revisit weak explanations.

[Roadmap](../ROADMAP.md) · [Progress](../PROGRESS.md) · [Exercises](../EXERCISES.md)
