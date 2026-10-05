# Skip lists: ordered data without tree rotations

An LSM engine needs to accept writes into memory while supporting ordered scans for flushing. A hash table handles equality lookup well but does not naturally emit keys in order. A sorted linked list emits ordered keys but takes linear time to find a position. A skip list adds a probabilistic hierarchy of shortcuts.

## Build express lanes over a sorted list

The bottom level contains every key in order. Each higher level contains a subset of the level below. Search starts at the highest level, moves right while the next key is less than the target, and drops down when moving right would overshoot. At the bottom, it finds the target or its insertion predecessor.

```text
level 2: head ---------------- 30 ---------------- tail
level 1: head ------ 10 ------ 30 ------ 50 ------- tail
level 0: head -- 5 --10 --20 --30 --40 --50 --60 -- tail
```

To find 45, the top lane skips to 30. The next lane cannot move to 50, so search descends and moves to 40. It then discovers that 50 is the next larger key. The search has skipped several bottom-level links without requiring a balanced-tree rotation.

## Insertion and probability

During search, retain the predecessor at every level. Choose the new node's height by repeatedly promoting with probability `p`, commonly a value such as one-half. Link the node after the recorded predecessors at every level it occupies. Deletion reconnects those predecessors around the node.

Why does random promotion help? About half the nodes reach level one when `p=1/2`, a quarter reach level two, and so on. Each higher level spans larger gaps, leaving only a modest expected amount of horizontal work before each descent. Search, insert, and delete have expected logarithmic cost under the randomized model, not a strict worst-case guarantee for every possible layout.

Expected level participation is `1 + p + p² + ... = 1/(1-p)`. At `p=1/2`, a node has about two forward pointers on average, before metadata and allocation overhead. Increasing promotion changes memory, height, and traversal trade-offs. Real implementations cap height and select policies based on workload and memory layout.

## Concurrency changes the problem

A sequential skip list is relatively straightforward. A concurrent one must prevent readers from following partially installed or freed nodes. Locks, atomic compare-and-swap, logical deletion markers, and safe memory-reclamation schemes can address different parts of this problem. Publishing a new pointer before initializing the node's contents can expose invalid state under the memory model.

Garbage-collected languages reduce some reclamation hazards but do not make compound updates atomic. Native implementations may use epochs, hazard pointers, or specialized lifetime rules. An immutable/frozen memtable can simplify iteration during flush, but the active structure still needs correct concurrent access.

Do not infer “lock-free” from “uses atomics.” Progress guarantees require a complete algorithm and reclamation model. A fine-grained lock implementation may be simpler and fast enough; correctness and measured contention should guide the choice.

## Production use and trade-offs

Skip lists appear in ordered in-memory indexes, some LSM memtables, and sorted-set implementations. They support ordered iteration and incremental updates without tree rotations. The pointer-rich layout can cost memory and cache misses, while compact arrays are excellent for static data and binary search. Balanced trees offer different locality and worst-case properties.

For a memtable, the skip list is only one layer. The [LSM engine](lsm-trees.md) still needs WAL durability, snapshot/version rules, flush publication, and recovery. A correct in-memory ordered map does not establish a correct database.

Why not always use a skip list? If data is immutable, a sorted array may be smaller and more cache-friendly. If keys are only accessed by equality, a hash table may be simpler. If strict worst-case bounds or a particular cache layout matter, a deterministic tree may fit better. The advantage comes from the access pattern and implementation constraints, not from the expected-complexity label alone.

## Exercises

1. **Predict:** Trace searches for 5, 45, and 100 in the diagram. Which links are skipped?
2. **Implementation:** Build a sequential skip list with a seeded random generator, then compare search steps against a sorted list on 10,000 keys.
3. **Debug:** A concurrent reader follows a node that a deleter frees. Explain why changing pointers atomically is insufficient by itself.
4. **Design:** Choose a memtable structure for point reads plus ordered flushes and compare memory/locality costs.
5. **Interview:** Explain expected logarithmic behavior and why it is not a guarantee for every random layout.

<details><summary>Hints</summary>

The hierarchy is sparse geometrically, reducing expected traversal work. Pointer publication and object lifetime are separate correctness obligations. Use deterministic seeds for repeatable experiments, but do not confuse one good seed with a proof.

</details>

## Further reading and connections

[Pugh's Skip Lists paper](https://www.cs.umd.edu/~pugh/skipLists/skipLists.pdf), [LevelDB skip-list implementation](https://github.com/google/leveldb/blob/main/db/skiplist.h), and [RocksDB memtables](https://github.com/facebook/rocksdb/wiki/MemTable). Connect to [concurrency](../01-foundations/concurrency-and-io.md), [LSM trees](lsm-trees.md), and [B+ trees](b-plus-trees.md).
