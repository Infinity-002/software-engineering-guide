# Checkpoint: Networking

Attempt without notes. Explain mechanisms and draw histories before opening the rubric.

## Scenario

A browser request is slow only on its first visit, while a WebSocket disconnects after long idle periods and an HTTP/2 connection stalls during packet loss.

## Questions

1. Trace DNS delegation/caches, connection establishment, TLS verification, HTTP, intermediaries, and backend routing.
2. Separate flow control, congestion control, and application backpressure.
3. Explain connection reuse, NAT/proxy idle state, and heartbeat/reconnect behavior.
4. Compare TCP-level blocking with QUIC stream behavior without claiming HTTP/3 removes congestion.

## Evidence to produce

Capture a browser waterfall for cold and warm requests and annotate which stages were reused or skipped.

Score each answer: 0 = names only; 1 = correct happy path; 2 = failure mechanism and repair; 3 = assumptions, trade-offs, and validation. Pass when every question reaches 2 and the evidence is reproducible. Revisit weak chapters before advancing.

<details><summary>Review rubric after attempting</summary>

The explanation distinguishes packets, streams, requests, and application commits. DNS TTL does not expire established connections. TLS authenticates a channel endpoint; proxies create additional connections and trust boundaries.

</details>

[Section reading order](README.md) · [Progress](../PROGRESS.md) · [Project briefs](../projects/README.md)
