# Checkpoint: Foundations

Attempt without notes. Explain mechanisms and draw histories before opening the rubric.

## Scenario

Relay accepts 2,000 concurrent uploads. Memory grows until the process is killed, while CPU is low. A developer proposes making the handler async and doubling the heap.

## Questions

1. Explain processes, threads, heap/native buffers, descriptors, and which resources each upload owns.
2. Distinguish overlap of I/O from parallel CPU execution. Why does async alone not bound memory?
3. Design streaming, concurrency limits, cancellation, and backpressure. State what happens at the limit.
4. Choose clocks for request duration and persisted event time, and explain why their representations differ.

## Evidence to produce

Draw a resource-lifetime diagram and run a bounded producer/consumer experiment with measured in-flight work and peak memory.

Score each answer: 0 = names only; 1 = correct happy path; 2 = failure mechanism and repair; 3 = assumptions, trade-offs, and validation. Pass when every question reaches 2 and the evidence is reproducible. Revisit weak chapters before advancing.

<details><summary>Review rubric after attempting</summary>

A strong answer follows bytes and ownership, separates scheduling from capacity, and bounds both buffers and concurrent operations. It treats wall time as an instant and monotonic time as a local duration source. More heap postpones an unbounded-growth failure.

</details>

[Section reading order](README.md) · [Progress](../PROGRESS.md) · [Project briefs](../projects/README.md)
