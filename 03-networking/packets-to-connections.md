# From packets to reliable connections

When Relay sends an attachment, the network does not carry a single indivisible “file.” It carries packets through independently operated networks. Packets can be lost, delayed, duplicated, or delivered out of order. Higher layers decide which of those failures to hide and which to expose.

## Local delivery and Internet routing

Ethernet carries frames on a local link. A frame includes link-layer addresses; switches learn where to forward frames within that link. IP supplies addresses used across networks. A router examines a destination IP address, chooses a next hop from its routing table, and forwards a packet inside a new link-layer frame. The end-to-end IP destination can stay the same while link-layer addresses change at every routed hop.

```text
browser socket -> local Ethernet/Wi-Fi -> home router/NAT
  -> ISP routers -> destination network -> server socket
```

IPv4 uses 32-bit addresses; IPv6 uses 128-bit addresses and has different protocol details, including neighbor discovery. The bigger IPv6 space reduces address scarcity but does not eliminate routing or firewall policy. IP provides best-effort delivery, not a guarantee that a particular packet arrives. A packet's hop limit prevents routing loops from circulating it forever.

Ports identify transport endpoints on a host. An established TCP connection is distinguished by source/destination addresses and ports together with the transport protocol. The server's port may be 443 while the client uses a temporary source port. A million clients do not require a million different server listening ports.

**NAT** rewrites address/port mappings, commonly allowing private IPv4 hosts to share a public address. A mapping has state and can expire. This is one reason a connection that appears idle and open at the application can fail when reused. NAT is not equivalent to an authorization policy. Firewalls separately permit or deny traffic by rules and often connection state.

## TCP: an ordered byte stream

TCP's handshake establishes connection state and initial sequence numbers:

```text
client                   server
  SYN -------------------->
      <---------------- SYN + ACK
  ACK -------------------->
  bytes with sequence numbers ...
```

TCP numbers bytes, acknowledges received data, retransmits missing data, and presents an ordered stream. It does not preserve application message boundaries. One HTTP header can span several packets; several small messages can arrive in one read. A custom protocol therefore needs framing, such as a length prefix or delimiter with escaping.

Reliability does not mean unlimited patience or durable application processing. A transport acknowledgement means bytes reached the receiving TCP stack under the protocol's semantics; it does not mean a payment committed to a database. A connection reset after a write leaves the application outcome potentially unknown.

**Flow control** protects the receiver: an advertised window bounds how much data it can accept without being overwhelmed. **Congestion control** protects the network: the sender adjusts its sending behavior based on loss, acknowledgement timing, and other signals. A receiver with a large buffer cannot make a congested path infinitely fast. Retransmission improves eventual delivery but increases tail latency when packets are lost.

## UDP and QUIC

UDP sends datagrams without TCP's ordered-stream machinery. Datagrams preserve message boundaries, but the protocol does not itself retransmit or order them. It is useful when the application prefers current data over delayed old data, or wants to implement a different transport behavior. Real-time media still needs congestion management; using UDP does not grant permission to flood the network.

QUIC implements reliable streams and congestion control over UDP, integrating a TLS handshake. Its independent streams avoid TCP's cross-stream delivery blocking when one stream's data is lost, although all streams still share network congestion and finite bandwidth. HTTP/3 uses QUIC; “UDP is unreliable” does not imply “HTTP/3 loses responses without recovery.”

## Failure scenarios and diagnosis

A laptop changes networks. A traditional TCP connection's endpoint tuple may no longer work; QUIC can support connection migration through connection IDs, subject to path validation and implementation policy. A large upload stalls only on one route: investigate path MTU and packet loss, not just backend CPU. A server has free RAM but cannot connect outward: ephemeral ports or NAT mapping capacity may be exhausted.

NAT traversal introduces a discovery problem: a peer behind NAT may have no directly reachable listening endpoint. STUN can help discover the mapped address, hole punching can work with compatible mappings, and TURN relays traffic when direct connectivity fails. This introductory model explains why peer-to-peer applications often still need servers and why traversal is not guaranteed.

Use packet capture only with authorization and care for sensitive data. Start with endpoint-level timing and socket state, then inspect a narrow capture to test a hypothesis. TLS usually protects content, but addresses and timing remain useful metadata.

## Exercises

1. **Check:** Why is a port insufficient to uniquely identify a connection?
2. **Predict:** One packet carrying bytes for TCP stream A is lost. What happens to later bytes in that stream? How does HTTP/2 multiplexing interact with this?
3. **Debug:** A service succeeds from its own host but fails from another machine. Separate listening-address, firewall, route, DNS, and application hypotheses.
4. **Implementation:** Write a length-prefixed local TCP echo protocol and deliberately split one message across writes.
5. **Interview:** Contrast flow control, congestion control, and application backpressure.

<details><summary>Hints</summary>

TCP cannot expose a gap in its ordered byte stream. HTTP/2 streams sharing that TCP connection can therefore all wait on missing bytes even when their application-level streams differ. Binding only to loopback permits local access but not remote access.

</details>

## Further reading and connections

[RFC 9293: TCP](https://www.rfc-editor.org/rfc/rfc9293), [RFC 8200: IPv6](https://www.rfc-editor.org/rfc/rfc8200), and [RFC 9000: QUIC](https://www.rfc-editor.org/rfc/rfc9000) specify the mechanisms. Continue to [HTTP](dns-tls-http.md) and [partial failure](../10-distributed-systems/partial-failure-and-consistency.md).
