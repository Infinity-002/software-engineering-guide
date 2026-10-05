# Bloom filters and negative knowledge

A storage engine has many sorted files on disk. Most do not contain the requested key, but checking each file costs I/O. A Bloom filter spends a small amount of memory to answer a narrower question: “Can I safely skip this file?” It can say definitely absent or possibly present.

## Build intuition with shared marks

Allocate `m` bits, initially zero. Choose `k` well-distributed hash-derived positions for each key. To insert a key, set all its positions to one. To query a key, inspect those positions: any zero proves that this key was not inserted; all ones mean it may have been inserted.

```text
bits:       0 1 2 3 4 5 6 7 8 9 10 11
insert A:     1       1         1
insert B:         1   1             1
query C:          ^   ^             ^
```

If C's positions happen to be ones set by A and B, the filter returns a false positive. It has lost information about which key set each bit. For an ordinary insert-only filter with correct hashing and no corruption, false negatives do not occur: insertion set every queried position, and nothing clears them.

That guarantee has assumptions. Querying with a different encoding/hash seed, losing updates, using a stale filter missing recent inserts, or deleting bits can produce false negatives at the system level. A filter built for an immutable SSTable is easier to reason about than one asynchronously maintained for a live global dataset.

## Why the false-positive formula looks this way

Each hash placement leaves a particular bit untouched with probability about `1 - 1/m`. After `kn` placements from `n` inserted keys, its probability of remaining zero is approximately `(1 - 1/m)^(kn)`, close to `e^(-kn/m)` for large `m`. Thus the probability that a random queried position is one is roughly `1 - e^(-kn/m)`. If the `k` query positions behave approximately independently, the chance they are all one is:

```text
p ≈ (1 - e^(-kn/m))^k
```

Here `p` is the false-positive probability for a key not in the set, `m` the number of bits, `n` inserted distinct keys for sizing purposes, and `k` the number of hash positions. More bits reduce collisions. More inserted keys saturate the filter. Increasing `k` helps only until the extra set bits outweigh the benefit of extra checks.

The approximate optimum is `k ≈ (m/n) ln 2`, and a target `p` gives `m ≈ -n ln(p)/(ln 2)^2`. For one million keys and a 1% target, this is about 9.59 million bits, roughly 1.20 MB in decimal units, with about seven positions per key. Metadata, alignment, hash costs, and implementation details add overhead. This is a sizing model, not a promise for adversarial hash distributions. [The Summary Cache analysis](https://pages.cs.wisc.edu/~cao/papers/summary-cache/node8.html) derives the approximation.

## A storage-engine lookup

```text
get(key)
  -> memtable lookup
  -> for candidate SSTables:
       Bloom says absent? skip file
       Bloom says maybe?  consult file index/data
  -> resolve versions/tombstones
```

A false positive costs an unnecessary lookup, not a wrong returned value, because the authoritative structure confirms membership. The filter is an optimization before the truth. Do not use “maybe present” to grant access, charge money, or definitively suppress a new record.

When most queries are for existing keys, the filter may save less work. When disk reads are expensive and negative lookups common, it can be highly valuable. Allocate bits according to expected I/O benefit across files rather than assuming every filter deserves identical space.

## Deletion and variants

Clearing A's bits on deletion can clear bits B also needs, creating false negatives. Counting Bloom filters replace bits with counters so insertions increment and deletions decrement positions, but require correct membership/deletion discipline and handling for counter overflow. Deleting a key never inserted can corrupt the guarantee. Other probabilistic structures offer different deletion and space trade-offs; evaluate the workload before choosing a variant.

Filters can be combined by bitwise OR only when size and hash configuration agree, representing a union with a changed false-positive rate. As the set grows beyond its planned capacity, false positives rise toward one. Rebuild or use a growth strategy; a saturated filter becomes useless rather than automatically resizing itself.

## Exercises

1. **Predict:** Why does inserting the same key twice not change a normal bit filter after the first insertion? What changes for a counting filter?
2. **Implementation:** Build a small filter with stable hash functions. Insert known keys, prove no inserted key is missed, and measure false positives on disjoint keys.
3. **Design:** Size a filter for ten million keys at 0.1% false positives. Explain the memory/CPU trade-off before calculating.
4. **Debug:** A cache-penetration filter rejects a newly created account. Which freshness invariant failed?
5. **Interview:** Explain “definitely absent, probably present” without saying the filter stores every key.

<details><summary>Hints</summary>

For ten million keys and 0.1%, the approximation is about 143.8 million bits (18.0 MB decimal) and ten positions. A live-system filter must include every authoritative inserted key before its negative result can safely suppress that key's lookup.

</details>

## Further reading and connections

[RocksDB Bloom filters](https://github.com/facebook/rocksdb/wiki/RocksDB-Bloom-Filter), [Bloom's original paper](https://dl.acm.org/doi/10.1145/362686.362692), and the analysis above. Connect to [hashing](../01-foundations/data-and-time.md), [LSM trees](lsm-trees.md), [storage engines](../06-databases/storage-and-recovery.md), and [cache penetration](../07-caching/cache-failures.md).
