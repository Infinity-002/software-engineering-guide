# Distributed systems

**Prerequisites:** [Networking](../03-networking/README.md), [Databases](../06-databases/README.md), [Messaging and streaming](../09-messaging-streaming/README.md). **Roadmap level:** 4.

Read in this order; the checkpoint asks you to combine the ideas rather than repeat definitions.

Chapter | Priority | Concepts
--- | --- | ---
[Partial failure, CAP, and consistency](partial-failure-and-consistency.md) | P1 | network failures, process failures, partial failure, latency, timeouts, duplicate requests, message reordering, network partitions, CAP, strong consistency, eventual consistency, read-your-writes, monotonic reads, causal consistency, linearizability
[Replication, quorums, and failover](replication-and-quorums.md) | P2 | leader/follower, multi-leader, leaderless replication, failover, N W R quorums, stale reads, split brain
[Leases, distributed locks, and fencing tokens](leases-and-fencing.md) | P2 | leases, lease holder, lease authority, lease TTL, lease acquisition, lease renewal, lease expiration, stale holders, fencing tokens, distributed locks, lock ownership, lease clock assumptions
[Logical time and causality](logical-time.md) | P2 | clock problems, Lamport clocks, vector clocks, happens-before, hybrid logical clocks
[Consensus and leader election](consensus-and-leadership.md) | P2 | consensus, majority, terms, epochs, replicated logs, leader election, Raft, Paxos, failure detection

## Checkpoint

Complete the [section checkpoint](CHECKPOINT.md) without opening the chapters, then revisit weak explanations.

[Roadmap](../ROADMAP.md) · [Progress](../PROGRESS.md) · [Exercises](../EXERCISES.md)
