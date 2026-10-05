# Real-time features and file uploads

Relay adds live comments and attachments. Both features extend a request beyond a small JSON exchange: connections last longer, payloads grow, and work can outlive the original page. Resource ownership and recovery become central.

## Real-time delivery needs a recovery protocol

Polling every few seconds is often enough for export status. Long polling reduces empty responses by waiting for an update. SSE suits server-to-browser updates; WebSockets suit bidirectional interaction. Choose using freshness, direction, fanout, client support, and operational constraints, as [network transports](../03-networking/edges-and-realtime.md) explains.

A durable chat flow can be:

```text
client message ID -> authenticated server -> membership check
  -> persist message with conversation sequence -> acknowledge
  -> publish/fanout -> connected clients
reconnect -> request messages after last durable cursor
```

The send acknowledgement should state whether the message is merely received or durably stored. A client retry uses the same message ID. A server-assigned per-conversation sequence supports ordered display and gap detection; timestamps alone are insufficient. Sequence allocation can become a hotspot in a huge room, so scope ordering to the actual requirement.

Presence is soft state refreshed by heartbeats or recent activity. A disconnected network does not always produce an immediate close event. Expire presence after a grace interval and communicate “recently active” semantics where appropriate. Do not use presence as proof that a user received or read a message.

Reconnect with exponential backoff and jitter. Bound server and client buffers; a slow client should resync from history rather than retain unlimited live events. A load balancer restart can trigger a fleet-wide reconnect storm, stressing authentication, history reads, and subscription registration together.

## Two upload paths

In an API-mediated multipart upload, the browser sends a multipart body to the backend, which parses parts and streams bytes to storage. Bound total size, per-part size, number of parts, duration, and concurrent uploads. Never buffer the entire payload by default. Honor backpressure and clean up partial writes after cancellation.

A presigned/direct upload moves bulk bytes from browser to object storage:

1. Browser requests an upload intent with size/type metadata.
2. API authenticates, checks workspace quota, and allocates an unpredictable object key.
3. API returns a short-lived, narrowly scoped upload capability under provider rules.
4. Browser uploads directly; API later verifies completion, actual object metadata, and ownership.
5. A worker scans/transforms the object in quarantine.
6. Only validated objects become visible through attachment metadata.

An object-store multipart upload splits a large object into independently uploaded parts and later completes them; it is different from HTTP `multipart/form-data`. Track abandoned multipart sessions and lifecycle cleanup to avoid hidden storage costs.

## A filename is not authority

Do not use user filenames as trusted filesystem paths or object ownership evidence. Store display names separately from generated storage keys. Validate actual content where necessary; claimed MIME type and extension can lie. Images can contain huge dimensions or decompression bombs; archives can contain traversal paths or excessive expansion. Scanners and processors need resource limits and isolated permissions.

Serve untrusted active content from an appropriately isolated origin or force safe download behavior with correct content types and disposition. A private object's unpredictable URL is not a complete access policy. Signed download URLs are bearer capabilities: scope their lifetime and avoid logging or sharing them broadly.

## Consistency between metadata and bytes

Object storage and PostgreSQL do not share an ordinary transaction. Model attachment states such as `pending`, `uploaded`, `quarantined`, `ready`, and `failed`. A completion callback can arrive twice or never arrive; reconciliation jobs compare stale intents with actual object state. Deleting metadata before deleting bytes creates orphans; deleting bytes first can leave broken references. Make cleanup retryable and observable.

Why not store every file in PostgreSQL? Small transactional blobs can be reasonable, but large media affects backup size, replication bandwidth, database I/O, and serving cost. Object storage specializes in durable bulk objects, while the database stores ownership, lifecycle, and searchable metadata. The extra boundary is justified only when those benefits matter.

## Exercises

1. **Predict:** A message is persisted but its live fanout is lost. How does reconnect recovery prevent permanent disappearance?
2. **Design:** Specify attachment states and reconciliation for an upload completed after the browser closes.
3. **Implementation:** Stream an upload with a byte limit and cancellation; prove partial objects are eventually cleaned up.
4. **Debug:** A reconnect storm overloads PostgreSQL. Identify admission, replay, and jitter controls.
5. **Interview:** Distinguish a presigned URL, authorization, content validation, and malware scanning.

<details><summary>Hints</summary>

Live delivery is a latency path; durable history is the recovery path. A capability authorizes a constrained operation but does not certify the resulting content. Completion must be verified against the server-created intent, not accepted from arbitrary client object keys.

</details>

## Further reading and connections

[OWASP file uploads](https://cheatsheetseries.owasp.org/cheatsheets/File_Upload_Cheat_Sheet.html), [S3 presigned uploads](https://docs.aws.amazon.com/AmazonS3/latest/userguide/PresignedUrlUploadObject.html), and [WebSocket specification](https://www.rfc-editor.org/rfc/rfc6455). Continue to [chat project](../projects/04-realtime-chat.md), [queues](../09-messaging-streaming/queues-and-workers.md), and [cloud storage](../16-cloud/cloud-primitives.md).
