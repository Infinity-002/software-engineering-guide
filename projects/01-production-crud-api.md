# Project 1 — Production CRUD API

Build Relay's workspace/task API with PostgreSQL, validation, authentication, tests, structured errors, and Docker. The goal is one correct vertical slice whose behavior you can explain from HTTP through transaction commit.

## Contract and schema

Support registration/login/logout, workspace membership, task creation/listing/detail/edit/delete, and a health endpoint. Choose opaque cookie sessions for the first browser-facing version. Hash passwords with a maintained library, scope sessions, and enforce current workspace permissions on every resource operation.

Model users, workspaces, memberships, tasks, and sessions. Use primary/foreign/unique/check constraints; task edits carry an expected version. Membership uniqueness must survive concurrent requests. Decide soft versus hard deletion explicitly. Seed at least two workspaces and users with different permissions so isolation tests are meaningful.

Define an OpenAPI contract with bounded input, pagination/filter/sort rules, safe error codes, and retry semantics. Return an authoritative task/version after a successful mutation. Do not serialize database records indiscriminately.

## Milestones and why they exist

1. Implement one create/read path with migrations and parameterized SQL. Trace request parsing, validation, transaction, and response.
2. Add sessions and resource authorization. Demonstrate that changing an ID cannot cross a workspace boundary.
3. Add conditional edits and cursor pagination. These protect intent and stable traversal under concurrent activity.
4. Add bounded connection pooling, startup configuration validation, request IDs, and graceful shutdown. These make resource ownership visible.
5. Package API and PostgreSQL with Docker Compose, a persistent local volume, readiness handling, and documented startup/reset commands. Clearly distinguish a normal stop from destructive data reset.

Keep controller/service/persistence boundaries proportional. A few explicit modules are preferable to a generic framework abstraction that hides transactions.

## Required failure experiments

Run two edits against the same task version and prove exactly one succeeds. Send malformed and oversized input. Attempt cross-tenant reads/edits. Expire a session. Stop PostgreSQL while requests arrive and observe bounded failure rather than indefinite hangs. Send `SIGTERM` during a slow request and inspect draining behavior.

Reproduce a commit followed by a lost response using a controlled test hook or proxy. For an idempotent create endpoint, retry with the same key and verify one logical resource; otherwise document the ambiguous-create limitation and then implement the key as an extension. Avoid test hooks in production builds.

## Acceptance criteria

- [ ] One documented local command starts the stack from a clean checkout with non-secret sample configuration.
- [ ] Schema constraints and authorization reject invalid/cross-tenant operations under concurrency.
- [ ] Tests use a real disposable PostgreSQL instance for transaction/constraint behavior.
- [ ] Version conflicts are explicit; failed operations do not leak pool connections.
- [ ] Pagination includes a stable tie-breaker and has documented mutation limitations.
- [ ] Errors expose safe messages and request IDs; logs omit passwords/session tokens.
- [ ] Container replacement preserves intended data, and a backup can be restored locally.

## Exercises and review

Explain why each invariant lives in the database, service, or transport layer. Show an execution plan for the list endpoint with realistic data. Report pool wait separately from SQL duration. Add a short “why not microservices yet?” decision based on your workload and team assumptions.

<details><summary>Hints after implementation</summary>

Use the same checked-out database client for all statements in a transaction. Scope idempotency keys by caller/operation and compare meaningful payload fingerprints. Prefer a unique constraint over a pre-insert existence check for races. Keep transaction duration independent of external network waits.

</details>

## Further reading and connections

[Backend architecture](../05-backend/server-architecture.md), [API design](../05-backend/api-design.md), [transactions](../06-databases/transactions-and-mvcc.md), [security](../08-security/trust-and-authorization.md), and [Docker](../15-containers/containers-and-docker.md). Use [node-postgres documentation](https://node-postgres.com/) for driver-specific behavior.
