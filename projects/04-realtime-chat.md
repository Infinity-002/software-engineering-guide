# Project 4 — Real-time chat

Add workspace rooms with WebSockets, durable messages, approximate presence, reconnect recovery, and per-room ordering. The project is complete when losing a live connection does not lose acknowledged history or create duplicate user-visible messages.

## Product and protocol

Support joining an authorized room, sending text, paginated history, reconnect from a cursor, and visible send status. Distinguish pending, durably accepted, delivered-to-connection, and read-by-user if you implement receipts. Define edits/deletes or explicitly leave them out of the first version.

Each client send includes a stable message ID reused on retry. The server authenticates the connection, checks current membership, validates bounds, persists the message, assigns authoritative room order, and acknowledges according to the durability contract. Store a uniqueness constraint on the intended sender/message scope.

```text
React chat -> WebSocket gateway -> message transaction
                                    |
                               durable history
                                    |
                              outbox/fanout -> room subscribers
```

A gateway's in-memory subscription map is not the message authority. If it restarts, clients reconnect and request history after their last durable cursor. A pub/sub channel can accelerate delivery while history repairs missed events.

## Milestones and failure reasoning

Start with one gateway and one database. Demonstrate persistence/acknowledgement order. Add duplicate suppression, then reconnect/gap detection. Add a second gateway only when you can explain how room events reach subscribers on both and how stale membership is handled.

Presence uses heartbeats and expiry. Show “recently active” or a clearly approximate online state. A connection close event is useful but not guaranteed promptly under network loss. Do not equate presence with message delivery or reading.

Bound outgoing buffers. A slow client can fall behind faster than it can receive; disconnect it with a resumable cursor rather than growing memory indefinitely. Jitter reconnection and limit history replay to prevent a deployment from causing a database read storm.

## Required experiments

Lose the sender acknowledgement after persistence and resend the same ID. Drop fanout after commit and recover through history. Kill a gateway with active users. Delay one client's network until its buffer limit triggers. Revoke membership while a connection remains open. Send out-of-order duplicate client commands. Restart while a room is busy and inspect ordering and reconnect load.

Use real browser E2E tests for connection/auth behavior and deterministic integration tests for persistence/concurrency. A fake socket alone cannot establish proxy timeout or browser-origin behavior.

## Acceptance criteria

- [ ] Acknowledged messages survive gateway restart under the configured database durability model.
- [ ] Retried sends create one durable message and one logical UI item.
- [ ] Reconnect recovers missed history with stable cursor semantics and bounded replay.
- [ ] Ordering is defined per room; timestamps are not the sole ordering authority.
- [ ] Slow clients cannot cause unbounded server memory growth.
- [ ] Membership is enforced on join/send/history and revocation has an explicit active-connection policy.
- [ ] Presence expires and is not misrepresented as exact knowledge.
- [ ] Telemetry covers send latency, fanout delay, reconnects, gaps, and buffer pressure.

## Exercises and review

Compare WebSockets with SSE plus HTTP sends for the same product. Increase one room to 100,000 members and identify which assumptions break. Design a migration of an active room to another owner without losing durable history or letting stale ownership violate ordering.

<details><summary>Hints after implementation</summary>

Use the durable cursor as recovery authority. Live delivery can be duplicated or missed without corrupting the final history if identities and versions are correct. Recheck authorization for long-lived sessions and avoid treating a successful initial handshake as permanent permission.

</details>

## Further reading and connections

[Real-time flows](../12-fullstack/realtime-and-uploads.md), [chat design](../19-system-design/intermediate-designs.md), [leases](../10-distributed-systems/leases-and-fencing.md), and [frontend state](../04-frontend/state-and-data-fetching.md). Review [RFC 6455](https://www.rfc-editor.org/rfc/rfc6455) for the transport's actual guarantees.
