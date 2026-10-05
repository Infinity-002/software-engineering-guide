# Proxies, load balancing, and persistent connections

Relay's single API process reaches capacity. A second process adds compute, but clients now need a stable entry point and a way to reach healthy capacity. A load balancer solves routing; it does not automatically make application state shareable.

## Intermediaries have different jobs

A forward proxy acts on behalf of clients, such as an organization's outbound proxy. A reverse proxy fronts servers. It can terminate TLS, route paths, buffer traffic, enforce size limits, and attach telemetry. A load balancer selects a destination among candidates. Products such as Nginx and Envoy can combine several roles, but the roles remain useful for reasoning.

An L4 balancer primarily makes transport-level decisions using connection information. An L7 balancer understands an application protocol such as HTTP and can route by host/path or inspect headers. L7 adds flexibility and CPU cost, and creates another parser/trust boundary. An HTTP-aware balancer may distribute requests while an L4 balancer distributes connections; a few long-lived connections can therefore skew load.

Round-robin is simple when requests have similar cost. Least-connections or other adaptive policies can respond to uneven work, but measured connection count is only a proxy for load. Health checks need to reflect whether a replica should receive new work. A cached discovery record or an in-flight request can still reach a failing replica after a health check changes.

```text
browser -> CDN -> reverse proxy/load balancer -> API replicas
                 separate connections          |
                                           shared data authority
```

Trust forwarded headers only from configured trusted proxies. Otherwise a client can forge `X-Forwarded-For` and bypass an IP-based policy. Likewise, the proxy and backend must agree on HTTP framing; inconsistent parsing can enable request smuggling. Prefer maintained protocol implementations and consistent limits.

## CDNs move representations toward users

A CDN places serving/cache infrastructure near users and can absorb large volumes of repeated content requests. It improves network distance and origin load for cacheable representations. It does not make an uncached database transaction local. A content-hashed JavaScript asset is an excellent cache candidate; a personalized account response requires much more careful policy.

Cache key design must account for host, path, query parameters, negotiated variants, and any authorized personalization. Purges are operational actions with propagation behavior, not instantaneous distributed transactions. Versioned immutable asset names avoid many invalidation races. See [cache failures](../07-caching/cache-failures.md).

## Choosing a real-time transport

| Approach | Mechanism | Best fit | Main cost |
|---|---|---|---|
| Polling | Repeated short requests | Infrequent updates, simple clients | Empty requests and freshness delay |
| Long polling | Hold a request until data or timeout | Compatibility with request/response infrastructure | Reconnect churn and held request state |
| SSE | Streaming HTTP response of events | Server-to-browser updates | One-way channel; buffering and reconnect semantics |
| WebSocket | Persistent bidirectional framed channel | Interactive chat, collaborative messages | Connection lifecycle, backpressure, recovery |

SSE supports event IDs and reconnection behavior in the browser API, but the server must retain/reconstruct events for meaningful resume. WebSockets provide a message channel, not durable message delivery. After reconnect, an application needs a cursor or acknowledgement protocol to recover missed events. A heartbeat detects lack of recent progress; it cannot prove the peer is dead.

Long-lived connections consume file descriptors, memory, and load-balancer capacity. Bound outgoing buffers for slow clients. Disconnecting a client that cannot keep up may be safer than retaining an unbounded backlog, provided the client can resynchronize. Presence is approximate: “connected recently” is defensible; “definitely online now” usually is not.

## gRPC on the network

gRPC commonly uses HTTP/2 with typed service contracts and supports unary and streaming calls. Multiplexing reduces the need for one connection per RPC, while deadlines and status codes help structure failure handling. Proxies must support the required protocol, streaming, and trailers. Browser use commonly needs gRPC-Web or a compatible gateway because browser networking APIs differ from native HTTP/2 clients.

A long-lived client connection can pin traffic to one backend behind an L4 balancer. Adding pods may not redistribute existing connections immediately. Client-side balancing, connection rotation, or appropriate L7 routing can help, each with operational trade-offs. Do not diagnose this as “autoscaling failed” before inspecting routing granularity.

## Exercises

1. **Predict:** Ten thousand chat users reconnect simultaneously after a deploy. What becomes hot besides the WebSocket listener?
2. **Debug:** SSE messages arrive in batches every minute. Which intermediary buffering and timeout settings would you inspect?
3. **Design:** Choose a transport for stock quotes, document collaboration, and daily export completion. State freshness and recovery requirements first.
4. **Interview:** Why can sticky sessions hide a state-design problem? When can affinity still be useful?

<details><summary>Hints</summary>

Authentication, presence writes, history replay, and subscription setup can all surge during reconnect. Jitter reconnects and bound replay. Affinity can improve locality but should not be the only thing preventing data loss when a replica disappears.

</details>

## Further reading and connections

[MDN: server-sent events](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events), [RFC 6455: WebSocket](https://www.rfc-editor.org/rfc/rfc6455), and [gRPC core concepts](https://grpc.io/docs/what-is-grpc/core-concepts/) describe protocol behavior. Continue to [real-time application flows](../12-fullstack/realtime-and-uploads.md) and [service discovery](../20-production-patterns/boundaries-and-routing.md).
