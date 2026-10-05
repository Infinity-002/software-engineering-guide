# LSM trees and compaction

A write-heavy store can spend much of its time modifying scattered tree pages. A log-structured merge design first collects writes in memory and emits sorted immutable files, converting many small random updates into larger sequential writes. The cost reappears later as merging work.

## The write path

Append the change to a write-ahead log under the required durability policy, then update an ordered in-memory structure called a memtable. When it reaches a size threshold, freeze it and flush it as an immutable sorted string table (SSTable). A new memtable accepts writes while the old one flushes, subject to bounded buffering.

```text
write -> WAL -> active memtable
                  |
                freeze -> immutable memtable -> SSTable
                                                   |
                                                compaction
```

A skip list is one possible memtable implementation; the abstract requirement is efficient ordered updates and iteration. The WAL supports recovery of writes not yet safely represented in flushed files. A crash-recovery protocol must also track which files and log segments belong to the durable database state.

## Reads combine several histories

A lookup checks recent memory state and candidate SSTables, selecting the newest visible version according to sequence/version rules. A key may have versions in several files. Per-file indexes narrow the region to read; Bloom filters can skip files that definitely lack the key. Range scans merge sorted iterators and resolve duplicate versions.

An immutable file cannot be edited to erase an older value in place. A deletion writes a tombstone that suppresses earlier versions. Compaction may eventually discard the tombstone and older values only when retention, snapshots, and lower-level/replica visibility rules make resurrection impossible.

## Compaction pays accumulated debt

Compaction merges sorted files, discards obsolete versions when safe, and reorganizes data. Leveled strategies limit overlap at many levels, often improving read and space amplification at the cost of rewriting data through levels. Tiered/universal-style strategies can reduce some write amplification while retaining more overlapping runs and temporary space. Actual implementations have hybrids and tuning knobs.

Three amplifications describe the trade-off:

- **Write amplification:** physical bytes written relative to logical user bytes, including flushes and compaction.
- **Read amplification:** extra structures/pages consulted to answer a logical read.
- **Space amplification:** stored bytes relative to the live logical dataset, including old versions and temporary merge output.

Reducing one can increase another. A fast ingest benchmark that ends before compaction catches up may hide unsustainable throughput. If incoming writes outrun compaction, immutable buffers/files accumulate until the engine slows or stalls writes to protect bounded resources.

## Production failure reasoning

Relay's event projection is fast initially, then periodically stalls. Inspect compaction backlog, storage bandwidth, write stalls, file counts, cache hit rate, and long-lived snapshots. More memory can absorb bursts but cannot fix a permanent compaction-capacity deficit. Disk space must allow temporary compaction output; operating near full capacity can prevent the cleanup needed to recover space.

Bloom filters help negative lookups but do not remove the need to inspect all relevant versions for ranges. Caching hot blocks can improve reads while competing with memtable memory. Large values may make repeated compaction expensive, motivating separation of values from sorted keys in some designs, with additional garbage-collection complexity.

## When to choose this shape

LSM designs are attractive for sustained writes, ordered key-value access, and storage environments where batched sequential work helps. B+ trees can be attractive for predictable point/range reads and update patterns fitting page caching. Neither family is universally faster. Workload distribution, durability, compression, hardware, and engine implementation matter.

Why not simply append forever? Reads would consult ever more history, deleted values would occupy space, and recovery would grow. Compaction is the mechanism that keeps the append-friendly write path from turning into unbounded read and storage debt.

## Exercises

1. **Predict:** A tombstone is removed while an older value remains in another file. What can happen?
2. **Implementation:** Build a toy memtable plus sorted-file store with version numbers, point lookup, and two-file merge. State that it is not crash-safe until recovery is designed.
3. **Debug:** Write throughput collapses after an hour, not immediately. What evidence distinguishes compaction debt from an API bottleneck?
4. **Interview:** Explain why “LSM is write optimized” does not mean low total bytes written.

<details><summary>Hints</summary>

The old value can reappear if deletion evidence is discarded prematurely. Initial buffering can disguise a lower long-term maintenance rate. Measure physical write traffic and backlog over a long enough steady-state interval.

</details>

## Further reading and connections

[RocksDB overview](https://github.com/facebook/rocksdb/wiki/RocksDB-Overview), [RocksDB compaction](https://github.com/facebook/rocksdb/wiki/Compaction), and [LevelDB implementation notes](https://github.com/google/leveldb/blob/main/doc/impl.md). Connect to [Bloom filters](bloom-filters.md), [skip lists](skip-lists.md), and [WAL](../06-databases/storage-and-recovery.md).
