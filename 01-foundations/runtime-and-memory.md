# Processes, memory, and runtime boundaries

Relay's API seems to be a function that takes a request and returns JSON. In production it is a long-lived process sharing finite CPU, memory, files, and network capacity with other processes. Many application failures become understandable only at this level.

## A program becomes a process

A program is executable instructions and data. A process is a running instance with an address space, security identity, open resources, and execution state. Starting two Node.js servers creates two processes: changing a JavaScript variable in one does not update the other. This is why a global `Map` cannot be a shared session store across replicas.

A thread is an execution path within a process. Threads normally share the process address space and open resources, but have their own execution registers and stacks. Sharing is cheap compared with sending messages between isolated processes, but a bad pointer or unsynchronized write can corrupt shared state. A process boundary improves isolation; it does not remove coordination costs.

The operating system schedules runnable threads onto CPU cores. A **context switch** saves one execution context and restores another. It has direct bookkeeping cost and can disturb CPU caches. Ten thousand waiting connections do not require ten thousand continuously running threads. A server can ask the kernel to notify it when a socket is ready and maintain connection state separately from active execution.

## Memory is several different resources

The stack holds call frames and local execution state. Nested calls grow it; unbounded recursion can overflow it. The heap holds dynamically allocated objects whose lifetimes need not match a function call. A returned closure can retain an object after its creating function has returned. Languages and optimizing runtimes may place or eliminate allocations differently; “local variable means stack allocation” is not a universal rule.

**Virtual memory** gives a process its own address space. Page tables translate virtual addresses to physical memory or identify mappings that must be brought into memory. This supports isolation, shared mappings, and demand loading. Virtual size is not the same as resident physical memory. A page fault may be inexpensive allocation bookkeeping or expensive storage I/O; a high fault count alone does not identify a problem.

```text
process virtual address space
  code / read-only data
  heap and mappings  ---- page tables ---- physical pages
  thread stacks                         ---- file-backed pages
```

Garbage collection frees unreachable managed objects. It does not free reachable objects you no longer need. An unbounded cache is a memory leak from the application's perspective even if the collector is correct. Native buffers, thread stacks, and runtime bookkeeping can also make resident memory exceed the reported managed heap. Under pressure the kernel may reclaim caches, swap where configured, or terminate a process. A container's memory limit changes when pressure becomes fatal, not the nature of memory.

## Crossing into the kernel

Ordinary application code cannot directly manipulate arbitrary hardware or another process's memory. It requests privileged operations through **system calls**: open a file, create a socket, read bytes, allocate mappings, or launch a process. A **file descriptor** is a small process-local handle identifying an open resource. Files, sockets, pipes, and several notification mechanisms use this interface on Unix-like systems.

Descriptors are finite. A request handler that opens a file but never closes it can eventually fail to open a database connection even with free RAM. A socket is an endpoint for communication, not an entire HTTP request. One connection may carry many requests, and one request can span many reads. A `read` call returning fewer bytes than requested is normal; application protocols define message boundaries.

## Failure-driven example

Relay initially stores sessions in an in-process map. A deployment restarts the process and everyone is logged out. Adding a second API process makes logins appear intermittent because requests reach different maps. The problem is state ownership, not random load-balancer behavior. Moving session authority to a durable/shared service changes the failure model: sessions survive API restarts, but login now depends on that service's latency and availability.

Next, an upload endpoint buffers each 100 MB attachment. Fifty concurrent uploads can require roughly 5 GB just for payload bytes. Increasing the heap postpones failure. Streaming with bounded buffers changes memory growth from “entire file times concurrency” to “buffer budget times active streams.” You still need concurrency limits and slow-client timeouts.

## Judgment and connections

Use multiple processes for isolation and CPU capacity when measurements justify it; use bounded asynchronous I/O to overlap waiting. Do not multiply processes without accounting for duplicated caches and database pools. Twenty processes with a pool of 30 connections potentially demand 600 database connections.

Connect this model to [concurrency](concurrency-and-io.md), [Linux diagnosis](../02-operating-systems-linux/linux-debugging.md), [browser processes](../04-frontend/browser-internals.md), and [containers](../15-containers/containers-and-docker.md). Containers package processes; they do not make these resource limits disappear.

## Exercises

1. **Check your understanding:** Why can two threads see the same object while two API processes normally cannot?
2. **Predict:** A server's managed heap is stable but resident memory grows during uploads. Give three hypotheses and a measurement for each.
3. **Debug:** A service reports “too many open files.” Why might restarting help briefly? What evidence should be collected first?
4. **Implementation:** Compare buffered and streamed copies of a large local file. Record peak memory and elapsed time; do not infer production capacity from one run.
5. **Interview:** Explain what happens between calling `listen()` and handling a request, including the kernel's role.

<details><summary>Hints after attempting</summary>

Inspect descriptors over time, native/buffer allocations, concurrency, and the size of retained objects. A restart discards process state and closes resources but does not fix the leak. Streaming bounds memory only if downstream pressure reaches the producer.

</details>

## Further reading

[Operating Systems: Three Easy Pieces](https://pages.cs.wisc.edu/~remzi/OSTEP/) develops virtualization and scheduling. [Linux open(2)](https://man7.org/linux/man-pages/man2/open.2.html) and [socket(2)](https://man7.org/linux/man-pages/man2/socket.2.html) specify descriptor behavior.
