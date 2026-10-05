# Designing durable APIs

An API is a contract between independently changing programs. A good contract exposes useful domain operations, defines failure behavior, and remains understandable after retries, pagination, and version changes. Attractive URL spelling is a small part of that work.

## Resources, methods, and representations

REST emphasizes resources and uniform HTTP semantics. `/workspaces/{id}/tasks` identifies a collection; `GET` retrieves a representation, `POST` can create or invoke processing, `PUT` replaces the target representation under the contract, `PATCH` applies a defined modification, and `DELETE` removes the resource association. RPC exposes named operations, which can be clearer for actions such as `approveExpense`. Do not force every domain command into awkward CRUD merely to appear RESTful.

A **safe** method requests no state-changing semantics from the client perspective, although logging and accounting may occur. An **idempotent** method has the same intended effect after multiple identical requests as after one. `PUT` is normally idempotent because repeatedly replacing a resource with the same representation leaves the same intended state. `DELETE` can be idempotent even if later responses differ. `POST` does not inherently promise idempotence: two create requests may create two resources. An [idempotency key](../20-production-patterns/idempotency-and-deduplication.md) can add an application guarantee.

Do not mutate business state through `GET`; browsers, crawlers, and intermediaries may fetch or prefetch it. HTTP semantics and method guarantees are specified in [RFC 9110](https://www.rfc-editor.org/rfc/rfc9110).

## Responses are part of the design

Use `201` with a resource location for a completed creation where appropriate, `202` for accepted asynchronous work, and `204` for success without content. Distinguish malformed/invalid requests, unauthenticated callers (`401` with applicable challenge behavior), unauthorized access (`403`), absent resources (`404`), conflicts (`409`), throttling (`429`), and server faults (`5xx`). Do not encode every outcome as `200` with an arbitrary error string.

`Content-Type` describes the supplied representation; `Accept` expresses client preferences. Headers can carry validators, caching policy, trace context, and retry guidance. Decide an error envelope with a stable code, safe message, field details where useful, and a request ID. Avoid leaking whether a private resource exists when that fact itself is sensitive.

## Pagination is a consistency contract

Offset pagination is simple: `ORDER BY created_at DESC, id DESC LIMIT 20 OFFSET 20`. But if new rows arrive before the next request, positions shift and the client may see duplicates or omissions. Deep offsets also require the database to skip preceding work.

Cursor pagination uses a stable ordered position:

```sql
SELECT id, title, created_at
FROM tasks
WHERE workspace_id = $1
  AND (created_at, id) < ($2::timestamptz, $3::bigint)
ORDER BY created_at DESC, id DESC
LIMIT $4;
```

The unique tie-breaker avoids ambiguity when timestamps match. The index should match filtering and ordering. A cursor should carry or bind the relevant filter/sort context and be validated; opacity is not authorization. Keyset pagination avoids shifting offsets for inserts before the boundary, but it does not provide a stable snapshot if sort keys change or records are deleted. A snapshot export needs a stronger contract.

Bound page size, whitelist filter/sort fields, and define null ordering. Avoid exposing arbitrary SQL fragments through “flexible” query parameters. Consider the cost of total counts separately from page retrieval.

## Protocol choices and compatibility

GraphQL lets clients select fields through a typed schema and can reduce overfetching, but resolvers can create N+1 queries and expensive nested work. Enforce authorization per resource, query cost/depth controls where appropriate, and batching. gRPC uses typed service definitions and is strong for internal RPC/streaming, but browser integration and public debugging can be less straightforward. OpenAPI describes HTTP contracts and supports documentation, generation, and validation; it does not prove implementation correctness.

Additive changes are often safer than breaking changes, but a new enum member can break exhaustive clients. Changing units, nullability, ordering, or error semantics can break clients without changing a field name. Version only when needed, keep compatibility windows explicit, and observe old-client usage before removal.

## Webhooks and API keys

A webhook delivers an event to a caller-controlled endpoint. Sign the prescribed raw payload, include an event identity and timestamp/replay policy, retry with bounds, and expect duplicates. The receiver should durably accept work quickly and process asynchronously where appropriate. Outbound webhook delivery also creates an SSRF boundary.

API keys identify an integration and its granted scope; they are bearer secrets, not proof of a human's identity. Support rotation, revocation, restricted permissions, and redacted logs. Rate limits protect capacity and fairness, but [admission control](../13-reliability/rate-limiting.md) still needs a clear identity and failure policy.

## Exercises

1. **Design:** Specify task creation, listing, conditional editing, and asynchronous export endpoints, including errors and retry semantics.
2. **Predict:** Insert three new rows between offset pages. Draw the duplicate/skip behavior and compare a cursor.
3. **Debug:** A client retries `POST /payments` after timeout. Explain why HTTP status alone cannot prevent duplication.
4. **Interview:** When would you choose RPC or GraphQL over a resource-oriented HTTP API?

<details><summary>Hints</summary>

State the invariant and caller needs before choosing protocol. A conditional edit can use an entity version or validator. A safe payment retry requires durable request identity tied atomically to the business result, with downstream handling for unknown outcomes.

</details>

## Further reading

[OpenAPI specification](https://spec.openapis.org/oas/latest.html), [GraphQL specification](https://spec.graphql.org/), and [RFC 9457: problem details](https://www.rfc-editor.org/rfc/rfc9457). Connect to [indexes](../06-databases/indexes-and-query-plans.md) and [contract evolution](testing-and-evolution.md).
