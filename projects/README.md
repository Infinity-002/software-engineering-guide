# Practical projects

Build one evolving application rather than five unrelated demos. These are complete project briefs: requirements, suggested boundaries, milestones, failure experiments, and acceptance criteria. They deliberately leave implementation to the learner. The repository's small runnable [mechanism labs](../labs/README.md) provide immediate experiments without requiring a cloud account.

Project | Priority | Prerequisites | Evidence of completion
--- | --- | --- | ---
[1. Production CRUD API](01-production-crud-api.md) | P0 | HTTP, SQL, sessions, transactions | Correct authenticated API, tests, Docker startup
[2. Full-stack Relay](02-full-stack-relay.md) | P1 | Project 1, React, browser, state/cache | Accessible UI, race handling, measured performance
[3. Background processing](03-background-processing.md) | P1 | Project 1, queues, idempotency, outbox | Crash-safe local effects, retries, DLQ, replay
[4. Real-time chat](04-realtime-chat.md) | P1 | Projects 2–3, persistent connections | Durable history, reconnect recovery, bounded buffers
[5. Scalable service](05-scalable-service.md) | P2 | Prior projects, replication, telemetry, reliability | Load/failure evidence, restore drill, safe rollout

Use TypeScript/Node, React, PostgreSQL, and Redis where each brief calls for them. Pin supported versions and record startup commands in your implementation README. Use disposable local data and provider fakes for irreversible external effects. The course does not require paid cloud services; containers, a local proxy, and controlled fault injection can demonstrate the mechanisms.

Each submission should contain a short design, schema/migrations, implementation, focused tests, an evidence report, and a decision log. The evidence report states workload, environment, commands, results, and limits. Checkboxes represent demonstrated behavior, not merely files that exist. Keep credentials out of source and include an example configuration with non-secret sample values.

When a milestone fails, record the history that violated the invariant and fix the owning boundary. Do not add a queue or cache merely to satisfy a diagram. [Relay's evolution](../21-case-studies/relay-evolution.md) explains the triggers for each added component.
