# Consensus and leader election

Three coordinators must agree which worker owns Relay's scheduler partition. If each independently chooses a leader after a timeout, two leaders can emerge during a partition. Consensus exists to make one sequence of decisions survive machine failures and disagreement about who is alive.

## Agree on decisions, then replicate a state machine

Consensus asks participants to agree on a value under a specified failure model. Repeated consensus can establish an ordered log. If replicas start from compatible state and deterministically apply the same committed commands in the same order, they maintain a replicated state machine.

The challenge is not broadcasting a value when everything works. It is ensuring that a later leader cannot contradict a decision already committed before an earlier leader disappeared. Persistent metadata, quorum intersection, and rules about which histories can be extended provide that safety.

## Leader election is a means, not the entire guarantee

A leader simplifies sequencing. Followers suspect failure after missing expected progress, but timeouts cannot distinguish crash from delay. A candidate can win votes while an isolated old leader still believes it is leader. Correctness comes from limiting what either can commit and from rejecting stale terms/epochs, not from ensuring no two processes ever hold the belief.

In a five-voter cluster, a majority is three. Two disjoint majorities cannot exist in the same fixed membership. A partition of three and two can allow the majority side to make progress while the minority cannot commit new decisions. Losing three voters blocks progress, even if the remaining two are healthy.

## Raft's conceptual pieces

Raft organizes time into terms. Candidates request votes; a voter does not cast conflicting votes in one term, and log freshness influences eligibility. The leader appends commands and replicates them. Commitment follows quorum and term rules; followers apply committed entries. Conflicting uncommitted suffixes can be replaced when logs are reconciled, while committed history must remain preserved.

This is a conceptual model, not an implementation recipe. Correct handling of persistence, current-term commitment rules, membership changes, snapshots, and read paths is essential. A leader's local read is not automatically linearizable after it has been isolated; it must establish current authority through a suitable quorum/read protocol or a correctly justified lease. The [Raft paper](https://raft.github.io/raft.pdf) supplies the full algorithm.

```text
client -> leader proposes log entry
             -> follower A persists
             -> follower B persists
         quorum/term rules establish commit
         replicas apply deterministic command
client <- result under the chosen response contract
```

## Paxos intuition

Paxos separates proposing values from accepting them. Numbered proposals and a prepare/promise phase constrain later proposers: once a value might have been chosen, subsequent successful proposals must preserve the appropriate accepted value. Quorum intersection carries knowledge of prior decisions into later rounds. Multi-Paxos amortizes repeated agreement when a stable leader handles a sequence of slots.

The important insight is continuity of chosen values across leadership changes. “A majority liked my proposal” is incomplete if the proposer ignored a prior accepted history. Learners should understand the purpose and assumptions before attempting algorithm pseudocode from memory.

## Safety can survive when progress cannot

In a fully asynchronous model with crash faults, deterministic consensus cannot guarantee termination in every admissible execution. Practical systems use timeouts, randomized elections, and periods of sufficiently stable communication to make progress. This does not mean consensus is useless; it means liveness depends on conditions and must be separated from safety.

Consensus is also not Byzantine agreement. A replica that lies or violates protocol assumptions can require a different model and quorum design. Disk corruption, lost durable state, and operators cloning identities can invalidate assumptions even without malicious intent.

## Production use and trade-offs

Coordination stores, metadata services, and replicated databases use consensus to establish authority and ordered state. Keep commands deterministic or record nondeterministic choices in the log. Snapshotting bounds retained history but requires correct installation and recovery. Slow voters, storage latency, large entries, and cross-region placement affect commit latency.

Why not use consensus for every cache read? It adds coordination latency and availability dependence that may not be required. Why not implement it yourself for Relay? A maintained database or coordination service usually provides a safer authority. The application still needs to understand its guarantees, failure behavior, and transaction scope.

## Exercises

1. **Predict:** A five-node cluster partitions 3/2. Which side can commit, and why might both sides temporarily believe they have a leader?
2. **Debug:** An isolated old leader serves local reads. What evidence is missing for linearizability?
3. **Design:** Decide which Relay state needs consensus-backed authority and which can be a rebuildable projection.
4. **Interview:** Explain how a new leader learns enough history to avoid contradicting a committed decision.

<details><summary>Hints</summary>

Belief is not authority. Voting/log rules and persistent state constrain successors. A linearizable read needs evidence that the serving node's view remains authoritative, not just that it once won an election.

</details>

## Further reading and connections

[Paxos Made Simple](https://lamport.azurewebsites.net/pubs/paxos-simple.pdf), [Raft visualization and paper](https://raft.github.io/), and [FLP impossibility paper](https://groups.csail.mit.edu/tds/papers/Lynch/jacm85.pdf). Connect to [quorums](replication-and-quorums.md), [leases](leases-and-fencing.md), and [Kubernetes control-plane state](../17-kubernetes/kubernetes-model.md).
