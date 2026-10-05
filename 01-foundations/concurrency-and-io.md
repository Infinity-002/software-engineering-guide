# Concurrency, synchronization, and I/O

Suppose Relay must fetch a profile and task list. Waiting for the profile before starting the task query wastes time if the operations are independent. Running both concurrently overlaps their lifetimes. They execute in **parallel** only when actual work occurs simultaneously, for example on separate cores or devices. Concurrency is about managing overlapping work; parallelism is about simultaneous execution.

## Four distinctions that prevent confusion

| Distinction | What it asks | Example |
|---|---|---|
| CPU-bound vs I/O-bound | What limits progress? | Image encoding vs waiting for a database |
| Blocking vs non-blocking | Can this operation park the calling thread? | Blocking read vs a readiness-based socket |
| Synchronous vs asynchronous | How is completion delivered to the caller? | Direct result vs future/callback |
| Concurrency vs parallelism | Does work overlap or execute simultaneously? | Many pending fetches vs worker threads |

An asynchronous API can internally use blocking worker threads. A non-blocking socket can be used by a badly designed busy loop. Naming a function `async` does not move its computation to another core. In JavaScript, an expensive loop before the first `await` runs on the current thread and delays other work there.

## Shared state turns timing into correctness

Two workers increment a counter whose value is 10:

```text
A reads 10
B reads 10
A writes 11
B writes 11   // one increment disappeared
```

Each worker's local arithmetic is correct; the compound operation is not atomic. A **race condition** occurs when correctness depends on uncontrolled timing. A data race has a more specific memory-model meaning involving conflicting unsynchronized accesses; race conditions can also happen across HTTP requests without shared memory.

A **mutex** protects a critical section so participating threads enter one at a time. A **semaphore** tracks a count of permits, making it useful for limiting ten simultaneous jobs rather than claiming one exclusive owner. An atomic increment can solve a single-counter update; it does not automatically protect an invariant spanning several fields.

Imagine transferring stock between bins: `total = left + right` must stay fixed. Protecting each field separately may still expose an impossible intermediate state. Choose synchronization around the invariant, not around whichever line appears suspicious.

## Deadlock and cancellation

Worker A holds resource X and waits for Y. Worker B holds Y and waits for X. Neither can proceed. Consistent lock ordering breaks this cycle: acquire X before Y everywhere. Holding locks across slow network calls increases both contention and the number of things that can go wrong. Timeouts bound waiting but do not prove that an operation did not happen.

Cancellation is a request to stop work. A caller timing out does not automatically cancel a SQL query or refund a completed payment. Propagate deadlines where supported, release resources in `finally`, and distinguish cancellation from confirmed rollback. See [reliability](../13-reliability/resilience-and-recovery.md).

## Event-driven execution

An event loop runs ready callbacks. While a network request waits, the kernel or network subsystem can make progress independently of JavaScript execution. When data becomes available, a callback or promise continuation becomes runnable. This explains how one JavaScript thread can manage many connections while still being vulnerable to one long computation.

```text
accept/read events -> small handlers -> asynchronous work
       ^                                  |
       +--------- completion events ------+
```

This architecture exchanges many blocked stacks for explicit state machines. It does not create infinite throughput. Callbacks consume CPU, connections consume descriptors, and queued payloads consume memory. CPU-heavy work may need worker threads, separate processes, or a job service. Creating one worker per request is usually another unbounded-resource bug.

## Backpressure: make overload visible upstream

Suppose jobs arrive at 500/s and workers finish 300/s. The queue grows by 200 jobs each second. A queue changes when work happens; it does not make insufficient capacity disappear. In a stable system, Little's law relates average in-flight work `L`, throughput `λ`, and average time in the system `W`: `L = λW`. At 200 requests/s and 0.5 seconds average duration, expect about 100 requests in flight. This assumes compatible measurement boundaries and stable averages.

Backpressure tells a producer to slow down when the consumer cannot keep up. A Node stream's `write()` returning `false` asks the producer to wait for `drain`. A bounded queue may block submission or reject it. HTTP can express overload through a deliberate rejection. Decide what happens when the bound is reached; “just queue it” hides the decision until memory runs out.

Use concurrency to overlap independent waiting, with explicit limits. Avoid unlimited `Promise.all` over a million records. A batch of 20 preserves overlap while bounding database pressure, though the best limit depends on measured service capacity. Use a limiter around the actual scarce resource, not merely around request creation.

## Exercises

1. **Predict:** A Node handler computes a large hash synchronously while 1,000 sockets wait. Which activities can progress and which callbacks cannot?
2. **Debug:** Two async handlers both check available quota, `await`, then decrement it. Why can a single-threaded runtime still overspend?
3. **Design:** Give a bounded-queue policy for interactive requests and another for nightly exports. Explain their different latency promises.
4. **Implementation:** Build a producer/consumer with a queue limit of 100. Measure queue age, not only queue length, while doubling producer speed.
5. **Interview:** When is a semaphore more appropriate than a mutex?

<details><summary>Reasoning guide</summary>

Interleaving across `await` can invalidate an earlier check. Put the invariant in a transaction or atomic operation at the authority that owns it. For interactive work, early rejection may preserve useful latency; for durable batch work, delay may be acceptable if storage and maximum age are bounded.

</details>

## Further reading and connections

[Node.js: don't block the event loop](https://nodejs.org/en/learn/asynchronous-work/dont-block-the-event-loop) explains runtime consequences. [Node stream backpressure](https://nodejs.org/en/learn/modules/backpressuring-in-streams) connects to [queues](../09-messaging-streaming/queues-and-workers.md), [transactions](../06-databases/transactions-and-mvcc.md), and [load shedding](../13-reliability/resilience-and-recovery.md).
