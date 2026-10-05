# Logical time and causality

Relay displays a reply before the comment it answers because two servers' timestamps disagree. Sorting by wall time feels natural, but wall clocks are imperfect measurements, not a causal ordering service. Distributed systems often need to represent “this depended on that” rather than merely “this machine said 10:02.”

## Happens-before is a partial order

Within one process, an earlier relevant event precedes a later event. Sending a message precedes receiving that message. Taking the transitive closure of those relations gives **happens-before**. If neither event precedes the other, they are concurrent in this model; that does not mean they happened at exactly the same physical instant.

```text
process A: create comment ---- send -------- later edit
                                \
process B:                       receive ---- reply
```

The reply depends on receiving the comment. A separate update on process C may be concurrent with both, even if its wall timestamp falls between them. Causal metadata helps avoid presenting effects without their causes and helps identify conflicting versions.

## Lamport clocks preserve one implication

Each process maintains a counter. Increment it for local events; attach it to sent messages. On receiving a timestamp `t`, update the local counter to `max(local, t) + 1` before assigning the receive event's time. If event A happens before B, then `L(A) < L(B)`.

The converse is false: `L(A) < L(B)` does not prove A caused or preceded B. Independent processes can have different counter values. Pairing a Lamport counter with a process ID gives a deterministic total order for tie-breaking, but that imposed order is not discovered physical truth.

Example: A sends at counter 4. B is at 9 and receives it, advancing to 10. B's reply gets 11. This preserves A-before-reply even though B had already counted more local work. The counter measures ordering constraints, not elapsed seconds.

## Vector clocks can distinguish concurrency

A vector keeps one logical counter per participant or tracked actor. A process increments its own component and sends the vector; receivers merge component-wise maxima and record their own event according to the algorithm. Vector `v` precedes `w` when every component of `v` is at most the corresponding component of `w` and at least one is smaller.

`[2,0]` and `[1,1]` are incomparable: each contains progress absent from the other, so the represented versions are concurrent. `[2,1]` dominates both. This supports conflict detection, but vector size and membership management grow with tracked actors. Real systems use compacted or specialized variants depending on their workload and retention needs.

Detecting concurrency does not resolve it. Two edits to a title may need user choice or a domain merge. A counter increment can be modeled with merge-friendly state. A permission grant and revocation need carefully chosen semantics, not automatic “merge both.”

## Physical, monotonic, and hybrid time

Use wall time for human timestamps and cross-system observability with known uncertainty. Use a local monotonic clock for durations/deadlines where supported. Do not compare unrelated monotonic origins across machines. Time synchronization reduces skew but does not make every clock identical or prevent pauses.

Hybrid logical clocks combine a physical-time component with logical increments to preserve useful ordering while staying near wall time under assumptions. They can make versions more interpretable and compact than full vectors, but do not by themselves detect every concurrent pair or establish a global transaction order. Systems using bounded clock uncertainty for stronger guarantees must explicitly account for that uncertainty and waiting behavior.

## Failure scenarios and judgment

A last-write-wins store accepts a future-dated write from a skewed clock and rejects later legitimate values as “older.” An audit log sorted only by timestamp appears to show impossible cause/effect order. A scheduler computes elapsed duration with wall time and runs too early after a clock jump. The repairs differ: version protocols, causal/trace identifiers, and monotonic duration measurement respectively.

Why not attach a vector clock to every web request? Most CRUD applications can use a database's transaction order and entity versions with far less metadata. Logical time is useful when concurrent independent histories must be compared. Start with the required relation: elapsed time, human date, causal order, or one agreed commit order.

## Exercises

1. **Predict:** Compare `[3,1,0]` with `[2,2,0]` and `[3,2,0]`. Which pairs are ordered?
2. **Implementation:** Simulate Lamport send/receive updates and verify the happens-before implication.
3. **Debug:** A record's future timestamp dominates updates for an hour. Explain why clock synchronization alone may not repair existing version state.
4. **Interview:** Why does a total order derived from `(counter, processId)` not prove causality?

<details><summary>Hints</summary>

The first two vectors are concurrent; the third dominates each. A total order can arbitrarily place concurrent events. Repairing a poisoned timestamp may require an explicit version correction protocol, not just fixing the host clock.

</details>

## Further reading and connections

[Lamport: Time, Clocks, and the Ordering of Events](https://lamport.azurewebsites.net/pubs/time-clocks.pdf), [Dynamo versioning](https://www.allthingsdistributed.com/files/amazon-dynamo-sosp2007.pdf), and [Spanner paper](https://research.google/pubs/spanner-googles-globally-distributed-database/). Connect to [leases](leases-and-fencing.md), [data representation](../01-foundations/data-and-time.md), and [tracing](../14-observability/logs-metrics-traces.md).
