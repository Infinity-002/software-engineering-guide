# Request lifecycle and backend boundaries

A backend translates untrusted requests into authorized changes to shared state. Its architecture should make invariants and resource ownership visible. Folder names such as `controllers/` and `services/` are useful only when they correspond to real responsibilities.

## Follow one mutation

```text
socket -> HTTP parser -> request limits -> route -> authentication
  -> input validation -> authorization -> business operation
  -> transaction/repository -> response mapping -> serialization
```

The ordering is contextual. A cheap size limit should precede expensive parsing. Authentication may precede detailed validation to avoid unnecessary work or information disclosure. Authorization often requires loading a resource and checking workspace membership. Never infer authorization merely from a valid ID supplied by the client.

Routing identifies the operation. Middleware implements cross-cutting request behavior such as tracing, authentication, and limits. A controller adapts transport details to the application operation. A service enforces business rules. A repository encapsulates persistence where doing so makes queries and transaction ownership clearer. These boundaries can be functions in one module; they need not become an abstract class hierarchy.

## Put invariants at the authoritative boundary

Relay allows only workspace members to edit tasks. A controller can reject malformed IDs, but a service must enforce the actual membership rule. A database constraint protects invariants such as uniqueness even when two requests race. Duplicating every SQL operation behind a generic CRUD repository can hide the query shape and make transactions harder to compose.

Dependency injection means supplying a dependency rather than constructing it invisibly inside the operation. It can be as simple as `createTask({db, clock, notifier}, input)`. This makes configuration and ownership explicit. Do not inject dozens of tiny abstractions solely to make mocks easy; test real boundaries and keep the interface proportional to the problem.

## Validation, errors, and serialization

Validate syntax, shape, size, and domain constraints. Parsing a date is not the same as accepting a valid appointment date. Reject unknown or forbidden mutation fields where mass assignment would be dangerous. The authenticated user ID should come from verified identity, not from a writable `ownerId` field.

Separate expected outcomes from faults. A missing task, a version conflict, invalid input, and a database outage require different responses. Use stable machine-readable error codes and safe messages; keep stack traces and internal details in restricted telemetry. A request/correlation ID helps support connect the safe external error to internal evidence.

Serialization is an explicit boundary. Convert large integer IDs safely, define time units, and return only intended fields. Serializing an ORM entity directly can expose password hashes or internal authorization state. Logging the whole request body creates similar risks.

## Configuration and connection pools

Read and validate configuration at startup. Missing database settings should fail clearly rather than create a request-time surprise. Environment variables are a common delivery mechanism, not an excuse to scatter string parsing throughout the code. Distinguish public frontend configuration from secrets; anything bundled into client JavaScript is visible.

A database pool reuses connections and bounds concurrency toward the database. Acquisition itself can queue. Set an acquisition timeout, release clients in `finally`, and keep transactions short. Never hold a transaction open while waiting for a user or an unrelated external API. Pool size is a fleet-level budget: replicas multiplied by connections per replica must fit database capacity and leave room for operations.

```typescript
const client = await pool.connect(); // application-configured pg pool
try {
  await client.query("BEGIN");
  // All statements in this transaction use this same client.
  await performDatabaseChanges(client);
  await client.query("COMMIT");
} catch (error) {
  await client.query("ROLLBACK");
  throw error;
} finally {
  client.release();
}
```

This teaching fragment omits production handling for connection failure during rollback; preserve the original failure and discard broken connections according to the driver contract. Using `pool.query` for individual statements inside this block can accidentally run them on other connections.

## Architecture choices and failure modes

A modular monolith keeps deployment and transactions simple while preserving domain boundaries. Microservices add independent deployment and ownership at the cost of network failure, compatibility, telemetry, and cross-service consistency. Split because there is a concrete need, not because the repository reached a certain line count.

Move slow noninteractive work to background jobs when the user can accept asynchronous completion. Return an operation identity and expose progress/failure rather than claiming completion before it exists. Streaming uploads avoids whole-body buffering, but requires bounds, cancellation, and cleanup. Both topics connect to [queues](../09-messaging-streaming/queues-and-workers.md) and [uploads](../12-fullstack/realtime-and-uploads.md).

## Exercises

1. **Debug:** Latency rises while SQL spans stay fast. How do pool wait, event-loop delay, and response serialization explain the gap?
2. **Design:** Place validation, authorization, and transaction boundaries for assigning a task to a workspace member.
3. **Implementation:** Add a failing operation and prove the connection returns to the pool on every path.
4. **Interview:** When does a repository abstraction help, and when does it hide useful database behavior?

<details><summary>Hints</summary>

Trace queueing separately from execution. The membership check and update need a race policy if membership can change concurrently. A transaction boundary must belong to the whole business operation, not arbitrarily to each repository method.

</details>

## Further reading and connections

[Node HTTP](https://nodejs.org/api/http.html), [node-postgres pooling](https://node-postgres.com/features/pooling), and [node-postgres transactions](https://node-postgres.com/features/transactions). Continue to [API design](api-design.md), [transactions](../06-databases/transactions-and-mvcc.md), and [trust](../08-security/trust-and-authorization.md).
