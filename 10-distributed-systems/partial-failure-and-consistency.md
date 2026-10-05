# Partial failure, CAP, and consistency

**A distributed system is a system where failures are partial.** Relay's API can be alive while its database is unreachable. The database can commit while the response disappears. One region can communicate internally while being cut off from another. There is no single reliable observation that tells every participant what happened everywhere.

## Start with an ambiguous history

```text
client                  payment service
  charge request --------->
                         commits charge
  <--- response lost ------
  timeout
```

The client cannot distinguish this history from one where the request never arrived. Retrying risks duplication; giving up risks leaving the user unaware of a successful charge. The solution is an explicit operation identity and a way to query/reconcile its outcome, not a longer timeout alone.

Processes can crash, pause for garbage collection, lose CPU scheduling, or become overloaded. Networks can drop, duplicate, delay, and reorder messages, depending on the layer and reconnections. TCP ordering within one surviving connection does not impose ordering across different connections or application retries. A timeout is evidence that a deadline passed, not proof that the remote process is dead.

## Safety and liveness ask different questions

Safety means something bad never happens, such as two owners committing conflicting writes under the same exclusive authority. Liveness means useful work eventually progresses under stated conditions. A system that refuses every write may preserve safety while being useless. A system that always accepts writes may remain responsive while violating an invariant.

State the failure model: crash-stop or crash-recovery, durable or volatile state, bounded or unbounded delays, trusted or Byzantine participants. Ordinary majority protocols for crash faults do not automatically tolerate malicious replicas. Clock and storage assumptions are part of the proof, not implementation trivia.

## Consistency is a contract about observations

Linearizability makes each operation appear to take effect at one point between its invocation and response, respecting real-time order. If a write completes before a later read begins, that read must reflect it or a later write under the register's semantics. “Strong consistency” is used loosely; specify the actual model.

Eventual consistency promises convergence when updates cease and required communication/repair assumptions hold. It does not by itself bound staleness or define conflict resolution. Read-your-writes ensures a session sees its own completed writes. Monotonic reads prevent that session from moving backward to an older observed version. Causal consistency preserves causally related order, such as not showing a reply without its preceding post, while allowing concurrent events to be observed differently.

Serializable transactions and linearizable single-object operations address different dimensions. A serializable transaction schedule can be equivalent to a serial order without that order necessarily matching external real-time expectations. When both transaction atomicity and real-time ordering matter, state the stronger contract explicitly.

## CAP is a partition-time conflict

Consider replicas A and B unable to communicate. A receives a write setting `x=1`; B receives a read. If A acknowledges the write and B must answer while unable to learn it, B may return stale `x=0`, violating linearizability. If B waits or rejects instead, it gives up the theorem's availability condition for that operation.

CAP's availability is a formal requirement that requests to non-failing nodes eventually receive a qualifying response; it is not the same as a monthly uptime percentage. The theorem says that under a partition, a system cannot guarantee both linearizable consistency and that availability requirement for all relevant operations. It does not mean choose any two properties permanently, and partition tolerance is not usually optional in a networked deployment. See [Gilbert and Lynch's proof](https://users.ece.cmu.edu/~adrian/731-sp04/readings/GL-cap.pdf).

Different operations can make different choices. Relay may reject edits requiring a unique global owner while continuing to serve stale public documentation. After a partition heals, accepted divergent writes still require conflict resolution. Labeling a database “AP” does not design that resolution for you.

## Latency and retries make the model operational

Even without a hard partition, remote coordination costs time. A cross-region quorum can protect an invariant but add round trips to every write. A local read can be fast but stale. Choose consistency per invariant and user workflow: a cached task count may lag; a unique payment debit cannot be casually duplicated.

Retries increase offered load precisely when a dependency may be slow. Bound attempts, propagate deadlines, use jitter, and centralize retry ownership. Cancellation does not erase a remote effect. Preserve an explicit “outcome unknown” state where the system cannot truthfully say success or failure.

Why not make every operation linearizable? Sometimes it is the simplest correct choice, especially with one database. Across distance and failures, coordination can reduce availability or increase latency. Why not make everything eventual? Some invariants cannot be repaired acceptably after conflicting actions. Engineering judgment starts with which wrong outcome the product can tolerate.

## Exercises

1. **Predict:** A write times out and a later read returns the old value. Does that prove the write failed? Draw another possible history.
2. **Design:** Choose consistency for workspace permissions, task counts, chat messages, and payment balances.
3. **Debug:** A user sees a new task, refreshes, and sees an older list. Which session guarantee is missing?
4. **Interview:** Explain CAP with one partitioned read/write history and without the phrase “pick two.”

<details><summary>Hints</summary>

The read may use a lagging replica while the write committed elsewhere. Monotonic reads concern not going backward; read-your-writes concerns observing one's own writes. State assumptions about which endpoint and consistency mode the read used.

</details>

## Further reading and connections

[Jepsen consistency models](https://jepsen.io/consistency), [Herlihy and Wing: linearizability](https://cs.brown.edu/~mph/HerlihyW90/p463-herlihy.pdf), and the CAP paper above. Continue to [quorums](replication-and-quorums.md), [leases](leases-and-fencing.md), and [idempotency](../20-production-patterns/idempotency-and-deduplication.md).
