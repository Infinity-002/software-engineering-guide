# HyperLogLog and approximate cardinality

Relay wants the number of distinct users active this month across billions of events. Counting events overcounts repeat visitors. An exact set of user IDs solves the problem but grows with the distinct population. HyperLogLog keeps a compact statistical summary when a small, quantified estimation error is acceptable.

## Rare hash patterns reveal population size

Hash each identity into a well-distributed bit string. A leading zero occurs about half the time, two leading zeros about one-quarter, and a run of twenty is rare. Seeing an unusually long run suggests many samples have been observed. A repeated identity produces the same hash pattern, so it does not create new evidence simply because it appears again.

Using only the single longest run is very noisy. HLL divides items among `m` registers using part of the hash. Each register records the largest rank observed from the remaining bits, commonly leading-zero count plus one. This creates many smaller experiments whose results can be combined.

```text
hash(userId) -> register index | remaining random-looking bits
register[index] = max(register[index], rank(remaining bits))
```

The sketch does not retain the user ID or let you retrieve the set. A stored rank summarizes evidence, not a particular member's identity.

## Estimation and error intuition

The classical estimator combines registers through a harmonic-style calculation, with calibration and range corrections. A raw form is proportional to `m² / sum(2^(-register[i]))`; the calibration factor and small/large-range handling are essential to a practical estimator. Do not copy this fragment as a production implementation without the complete algorithm.

For classical HLL under its assumptions, relative standard error is approximately `1.04 / sqrt(m)`. More independent registers reduce noise by a square-root relationship. Quadrupling memory roughly halves standard error. At 16,384 registers, it is about 0.81%. This is not a hard guarantee that every estimate differs by less than 0.81%.

Small cardinalities need special handling because many registers remain empty. Hash width limits the usable range; biased or adversarial hashes violate the statistical model. Modern variants improve bias correction and sparse representations. When evaluating a product, distinguish the mathematical family from the implementation's exact precision and memory behavior.

## Merge sketches, not final estimates

Compatible sketches use the same hash definition, register indexing, and precision rules. Their union can be represented by register-wise maxima: each register retains the most extreme evidence from either input. This is useful for distributed aggregation without transferring all user IDs.

Adding two cardinality estimates is wrong when users overlap. Taking register maxima preserves duplicate insensitivity. Precision conversion between sketches is implementation-specific and must be supported deliberately. A sketch generated with a different hash seed cannot be merged meaningfully just because the byte arrays have the same length.

Ordinary HLL does not support arbitrary deletion or subtraction. To estimate rolling windows, maintain sketches per time bucket and merge the relevant buckets. This trades time resolution and stored sketches against query cost. Removing a day means excluding that bucket, not subtracting its estimated count from the monthly estimate, because users can appear on many days.

## Production use and limits

HLL fits dashboards, approximate unique visitors, query planning statistics, and capacity estimates. Redis offers an HLL data type, but the application still must choose identity normalization, time buckets, tenant scope, and acceptable error. If user identity changes, the sketch counts according to the supplied keys, not the product's intended person model.

Do not use HLL to decide whether a specific account exists, bill an exact number of unique customers, or enforce an exact quota. A Bloom filter answers approximate membership; HLL estimates distinct count. An exact set remains the right choice when cardinality is small, exactness matters, or deletions/individual inspection are required.

Approximation does not automatically remove privacy obligations. Inputs and surrounding metadata may be sensitive, and small-population statistics can reveal information. Scope access and avoid claiming a probabilistic sketch is a general anonymization mechanism.

## Exercises

1. **Calculate:** Compare approximate standard error for 1,024, 4,096, and 16,384 registers.
2. **Predict:** Two regions each estimate 100,000 users with 50,000 overlapping users. Why is summing estimates invalid?
3. **Implementation:** Use a maintained HLL implementation on synthetic sets with known overlap; measure estimation distribution across independent datasets.
4. **Design:** Build a rolling 30-day unique-user dashboard using daily sketches and explain the partial-day boundary.
5. **Interview:** Compare exact sets, HLL, and Bloom filters by supported query, error, deletion, and merge behavior.

<details><summary>Hints</summary>

The approximate errors are 3.25%, 1.625%, and 0.8125%. Merge compatible internal state for unions. An exact rolling timestamp window may need finer buckets or a different structure; a daily-bucket design has boundary approximation beyond HLL's statistical error.

</details>

## Further reading and connections

[Original HyperLogLog analysis](https://algo.inria.fr/flajolet/Publications/FlFuGaMe07.pdf), [Redis HyperLogLog](https://redis.io/docs/latest/develop/data-types/probabilistic/hyperloglogs/), and [HyperLogLog in Practice](https://research.google/pubs/hyperloglog-in-practice-algorithmic-engineering-of-a-state-of-the-art-cardinality-estimation-algorithm/). Connect to [Bloom filters](bloom-filters.md), [hashing](../01-foundations/data-and-time.md), and [analytics pipelines](../19-system-design/intermediate-designs.md).
