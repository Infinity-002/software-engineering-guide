# Inverted indexes and search mechanics

Relay has millions of task descriptions. Searching every row for “database timeout” repeatedly reads huge amounts of irrelevant text. An inverted index reverses the ordinary mapping: instead of document to words, it stores term to matching documents.

## From documents to postings

Analyze each document into terms and record occurrences. A posting list can include document ID, term frequency, and positions:

```text
database -> [(doc2, positions 1,8), (doc7, position 4)]
timeout  -> [(doc2, position 2),   (doc9, position 6)]
```

An AND query intersects document sets; an OR query unions them. Sorted posting lists can be merged efficiently, often starting with rarer terms to reduce candidate work. Skip structures or block metadata help jump over regions that cannot contribute. Compression reduces memory and I/O while adding decode CPU, often a favorable trade for large indexes.

Phrase search needs positional relationships: `database` at position 1 and `timeout` at position 2 supports an adjacent phrase, while the same terms far apart do not. Field boundaries and analyzer position rules affect interpretation. Indexing only document membership cannot reconstruct phrase information later.

## Analysis defines meaning

Tokenization decides how text becomes terms. Case normalization, stemming, stop-word handling, synonyms, and language-specific rules change matches. A naive split-on-spaces pipeline handles source-code identifiers, Chinese text, punctuation, and names poorly. Index-time and query-time analysis must be intentionally compatible.

Changing an analyzer can require rebuilding an index because old postings embody the previous interpretation. Version the analysis policy and compare quality using a labeled query set. More recall can reduce precision; adding broad synonyms can produce irrelevant results. Search quality is an empirical product requirement, not only a data-structure benchmark.

## Ranking selects useful matches

Boolean matching identifies candidates, but a common word may match millions of documents. Ranking uses signals such as term rarity, frequency, document length, freshness, and product context. BM25 is a representative lexical ranking family balancing frequency saturation and length normalization. A term appearing twice is evidence, but repeating it a thousand times should not necessarily multiply relevance a thousandfold.

Top-k retrieval algorithms can avoid scoring every candidate when bounds show some regions cannot beat the current result threshold. Distributed search adds local shard candidates, score/statistics considerations, and coordinator merging. More shards increase parallelism but also fanout and tail-latency exposure.

## Updates create segments and cleanup work

Many search engines buffer changes and publish immutable segments, then merge them. A refresh makes recent changes searchable under the engine's contract; it is not necessarily the same operation as durable commit. Deletions may mark documents invisible before physical bytes are reclaimed. Segment merges compete with queries for CPU, memory, and disk bandwidth.

Source versioning prevents delayed events from overwriting newer indexed content. A deletion tombstone or version policy prevents an old update from resurrecting a document. Rebuild into a new generation, catch up with ongoing changes, validate, then switch through a controlled alias/pointer. The index should be reconstructible if it is a projection of authoritative business data.

## Security and failure scenarios

A query returns a private task's snippet before a later authorization check removes the full document. The leak has already occurred. Apply tenant/access filtering before exposing content, and define how current permission changes reach or override stale index state. Caches must include the relevant scope.

Bound query complexity, result size, regex/fuzzy expansion, and execution time. One short query can be computationally expensive. Raw query logs can contain private text and should not be treated as harmless telemetry. A timeout/partial-result policy must tell clients whether results are complete enough for the product's use.

Why not use an inverted index for every lookup? Exact ID access is simpler in a key-value or relational index. Why not make search the source of truth? It may fit some applications, but transaction constraints, refresh visibility, and relational invariants must match the requirement. For Relay, PostgreSQL authority plus a rebuildable search projection keeps those responsibilities clear.

## Exercises

1. **Implementation:** Build a positional inverted index for ten documents and support AND, OR, and adjacent phrase queries.
2. **Predict:** Remove positions from the index. Which queries become impossible to answer exactly without rereading documents?
3. **Design:** Change the tokenizer while live updates continue and define safe index-generation cutover.
4. **Debug:** A deleted task reappears after a delayed event. Add version-aware update/deletion handling.
5. **Interview:** Explain how postings, analysis, ranking, segments, and authorization cooperate in one search request.

<details><summary>Hints</summary>

Posting membership cannot prove adjacency. Analysis is part of the schema. A versioned delete must dominate older updates, and permission enforcement must precede exposure of snippets or stored fields.

</details>

## Further reading and connections

[Lucene documentation](https://lucene.apache.org/core/), [Elasticsearch analysis](https://www.elastic.co/guide/en/elasticsearch/reference/current/analysis.html), and [near real-time search](https://www.elastic.co/guide/en/elasticsearch/reference/current/near-real-time.html). Connect to [LSM trees](lsm-trees.md), [CQRS projections](../20-production-patterns/cqrs-and-event-sourcing.md), and [large-scale search](../19-system-design/advanced-designs.md).
