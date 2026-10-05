# Reading a running Linux system

A production report says “the API is slow.” Restarting may restore service but erase the evidence that explains it. Start by separating four questions: Is work arriving? Is it waiting? Is it executing? Is a resource exhausted? Linux exposes clues about all four.

## Processes, ownership, and lifecycle

A process has a user/group identity. File permission bits and other access controls determine which operations that identity may perform. Giving the application root privileges to fix a permission error expands the damage an application bug can cause. Instead, identify the exact directory or socket it needs and assign the narrowest useful access.

The shell expands arguments and starts processes. Quoting matters: untrusted values interpolated into shell strings may become commands. Prefer argument arrays in application APIs. Environment variables are inherited configuration, not a secure database; avoid printing them indiscriminately because they may contain secrets. A process's working directory also affects relative file paths, which explains many “works locally” failures.

Signals request lifecycle actions. `SIGTERM` is a conventional request for graceful termination; `SIGKILL` prevents application cleanup. A shutdown sequence should stop accepting new work, stop acquiring new jobs, let in-flight work finish within a bound, close connections, and exit. If the bound expires, the platform may kill the process. Correctness must survive that final interruption.

## An evidence-oriented toolkit

These commands are Linux examples, usable in a Linux host, VM, or WSL. Some images omit utilities; `pidstat`/`iostat` usually come from `sysstat`, and `lsof`/`strace` may require installation. Inspecting another user's process can require privileges.

| Question | Tool | Interpretation |
|---|---|---|
| Which process is busy? | `ps`, `top`, `pidstat` | Per-process CPU, memory, scheduling activity |
| Is memory pressure growing? | `free`, `/proc/meminfo` | Available memory, cache, swap; “free” alone misleads |
| Are files/descriptors leaking? | `lsof -p PID`, `/proc/PID/fd` | Count and identify open resources |
| Is the server listening? | `ss -ltnp` | Address, port, and owning process |
| Are disks busy or full? | `df -h`, `df -i`, `iostat` | Bytes, inodes, latency, queue pressure |
| What is it waiting on? | `strace -p PID` | System-call activity, with tracing overhead |
| Can HTTP reach it? | `curl -v URL` | Resolution, connection, TLS, HTTP outcomes |

Never conclude “RAM leak” solely because Linux uses most memory: unused memory can be used for reclaimable file cache. Never conclude “disk is fine” solely from free space: latency, IOPS saturation, and exhausted inodes are different failures. CPU averages also hide a saturated single core on a multicore machine.

## Worked diagnosis: the slow API

Relay's latency rises from 80 ms to 2 seconds while CPU stays low. First compare request rate and in-flight count. If throughput is unchanged but duration rises, more work is waiting. Inspect connection-pool wait time before assuming SQL execution itself is slow. A leaked database client can strand callers even when the database is idle.

If the pool is healthy, inspect network connection state and database spans. If CPU is high on one core while other cores idle, sample the application profiler: a synchronous JSON transformation may block Node's event loop. If resident memory climbs, compare allocation profiles and descriptor counts across time. One snapshot rarely establishes a leak; a trend tied to repeated work is stronger evidence.

Use `strace` narrowly. Repeated reads returning no useful progress or a long wait on a descriptor can guide hypotheses, but encrypted protocol payloads and application invariants are not visible there. High-volume tracing can itself alter performance. Preserve timestamps and distinguish observation from inference.

## Graceful shutdown is a distributed protocol

Removing a replica from routing is not instantaneous. Discovery caches, load balancers, and existing keep-alive connections may keep traffic flowing briefly. Mark it unready, allow routing changes to propagate, stop accepting fresh work, and drain within the orchestrator's termination grace period. Queue workers should stop reserving messages and either complete current work or allow redelivery. A shutdown handler is not a substitute for [idempotency](../20-production-patterns/idempotency-and-deduplication.md).

Why not restart on every high latency signal? If the cause is a shared database, restarting all clients can create a reconnection storm and remove healthy capacity. Use [readiness and liveness](../13-reliability/resilience-and-recovery.md) for different purposes. Restart only when the evidence supports a process-local condition that a restart can improve.

## Exercises

1. **Check:** Explain why a full disk and exhausted inodes can produce similar symptoms.
2. **Predict:** What happens to a job if the worker receives `SIGKILL` after its database commit but before acknowledgement?
3. **Debug:** CPU is 15% on an eight-core host, yet one Node process is unresponsive. What measurement changes your interpretation?
4. **Implementation:** Run a small server locally. Send `SIGTERM` during a slow request and record whether it completes. Repeat with forced termination in a disposable environment.
5. **Interview:** Give a five-minute investigation plan for rising latency with stable request rate.

<details><summary>Reasoning guide</summary>

The job can be redelivered; the durable effect must tolerate it. One core near saturation can hide in host averages. Follow waiting time through admission, pool acquisition, dependency work, and response delivery before choosing a fix.

</details>

## Further reading and connections

[Linux proc(5)](https://man7.org/linux/man-pages/man5/proc.5.html) documents process evidence. [Linux signal(7)](https://man7.org/linux/man-pages/man7/signal.7.html) explains signal semantics. Connect these observations to [runtime resources](../01-foundations/runtime-and-memory.md), [observability](../14-observability/logs-metrics-traces.md), and [containers](../15-containers/containers-and-docker.md).
