# References and source policy

The local chapters contain the teaching material; these sources let you inspect specifications, implementation guarantees, and deeper arguments. Prefer the exact documentation for the deployed version. A specification describes a contract, a product manual describes an implementation, and a paper often assumes a particular failure model. None should be treated as interchangeable evidence.

The curriculum was authored and reviewed on 2026-10-04–05. Version-sensitive claims about React/Next.js, PostgreSQL isolation/indexes, Kafka delivery scope, Redis locks, Kubernetes resources, Web Vitals, and OAuth security were checked against primary sources. General explanations and worked scenarios are original teaching material. Architecture case studies and capacity figures are hypothetical. External availability checks are reported separately in [VALIDATION.md](VALIDATION.md); a successful HTTP fetch is not a technical review of an entire source.

## Foundations and operating systems

- [Operating Systems: Three Easy Pieces](https://pages.cs.wisc.edu/~remzi/OSTEP/) — freely available textbook on virtualization, concurrency, and persistence.
- [Linux man-pages](https://man7.org/linux/man-pages/) — system calls, process resources, sockets, and signals.
- [Node.js event-loop guidance](https://nodejs.org/en/learn/asynchronous-work/dont-block-the-event-loop) — runtime limits and blocking work.
- [ECMAScript specification](https://tc39.es/ecma262/) and [HTML event loops](https://html.spec.whatwg.org/multipage/webappapis.html#event-loops) — language and browser host scheduling contracts.
- [RFC 8259](https://www.rfc-editor.org/rfc/rfc8259) and [Unicode FAQ](https://www.unicode.org/faq/) — JSON and text representation.

## Networking and protocols

- [RFC 9293: TCP](https://www.rfc-editor.org/rfc/rfc9293), [RFC 8200: IPv6](https://www.rfc-editor.org/rfc/rfc8200), and [RFC 9000: QUIC](https://www.rfc-editor.org/rfc/rfc9000).
- [RFC 1034: DNS concepts](https://www.rfc-editor.org/rfc/rfc1034) and [RFC 8446: TLS 1.3](https://www.rfc-editor.org/rfc/rfc8446).
- [RFC 9110: HTTP semantics](https://www.rfc-editor.org/rfc/rfc9110), [RFC 9111: HTTP caching](https://www.rfc-editor.org/rfc/rfc9111), [RFC 9113: HTTP/2](https://www.rfc-editor.org/rfc/rfc9113), and [RFC 9114: HTTP/3](https://www.rfc-editor.org/rfc/rfc9114).
- [RFC 6455: WebSocket](https://www.rfc-editor.org/rfc/rfc6455), [Fetch standard](https://fetch.spec.whatwg.org/), and [gRPC concepts](https://grpc.io/docs/what-is-grpc/core-concepts/).
- [RFC 9457: problem details](https://www.rfc-editor.org/rfc/rfc9457), [OpenAPI](https://spec.openapis.org/oas/latest.html), and [GraphQL specification](https://spec.graphql.org/).

## Frontend engineering

- [HTML Living Standard](https://html.spec.whatwg.org/) and [WAI tutorials](https://www.w3.org/WAI/tutorials/) — semantics, forms, and accessibility.
- [MDN web development](https://developer.mozilla.org/en-US/docs/Learn_web_development) — browser APIs and web foundations; use specifications for disputed normative behavior.
- [TypeScript handbook](https://www.typescriptlang.org/docs/handbook/intro.html) — narrowing, generics, type manipulation, and compiler semantics.
- [React learning material](https://react.dev/learn), [state as a snapshot](https://react.dev/learn/state-as-a-snapshot), [state identity](https://react.dev/learn/preserving-and-resetting-state), and [effects](https://react.dev/learn/synchronizing-with-effects).
- [React Server Components](https://react.dev/reference/rsc/server-components), [hydrateRoot](https://react.dev/reference/react-dom/client/hydrateRoot), and [Next.js server/client boundaries](https://nextjs.org/docs/app/getting-started/server-and-client-components).
- [Next.js caching](https://nextjs.org/docs/app/guides/caching) — inspect version-specific defaults instead of memorizing a permanent default.
- [TanStack Query](https://tanstack.com/query/latest/docs/framework/react/overview), [Redux essentials](https://redux.js.org/tutorials/essentials/part-1-overview-concepts), and [Zustand](https://zustand.docs.pmnd.rs/learn/getting-started/introduction) — different state-management contracts.
- [Web Vitals](https://web.dev/articles/vitals), [Chrome DevTools performance](https://developer.chrome.com/docs/devtools/performance), [Testing Library principles](https://testing-library.com/docs/guiding-principles/), and [Playwright best practices](https://playwright.dev/docs/best-practices).

## Databases and storage

- [PostgreSQL documentation](https://www.postgresql.org/docs/current/) — authoritative starting point for the version linked by `current`.
- [Transaction isolation](https://www.postgresql.org/docs/current/transaction-iso.html), [explicit locks](https://www.postgresql.org/docs/current/explicit-locking.html), and [MVCC](https://www.postgresql.org/docs/current/mvcc-intro.html).
- [Multicolumn indexes](https://www.postgresql.org/docs/current/indexes-multicolumn.html), [index-only scans](https://www.postgresql.org/docs/current/indexes-index-only-scans.html), [EXPLAIN](https://www.postgresql.org/docs/current/using-explain.html), and [planner statistics](https://www.postgresql.org/docs/current/planner-stats.html).
- [WAL](https://www.postgresql.org/docs/current/wal-intro.html), [continuous archiving](https://www.postgresql.org/docs/current/continuous-archiving.html), and [vacuum](https://www.postgresql.org/docs/current/routine-vacuuming.html).
- [RocksDB overview](https://github.com/facebook/rocksdb/wiki/RocksDB-Overview), [compaction](https://github.com/facebook/rocksdb/wiki/Compaction), [Bloom filters](https://github.com/facebook/rocksdb/wiki/RocksDB-Bloom-Filter), and [LevelDB implementation](https://github.com/google/leveldb/blob/main/doc/impl.md).
- [Lucene](https://lucene.apache.org/core/) and [Elasticsearch analysis](https://www.elastic.co/guide/en/elasticsearch/reference/current/analysis.html) — search indexing and query analysis.
- [node-postgres transactions](https://node-postgres.com/features/transactions) — connection ownership in the example stack.

## Security

- [OWASP Cheat Sheet Series](https://cheatsheetseries.owasp.org/) — practical security controls organized by boundary.
- [Authorization](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html), [password storage](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html), [session management](https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html), and [secrets management](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html).
- [CSRF](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html), [XSS](https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html), [SSRF](https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html), and [file uploads](https://cheatsheetseries.owasp.org/cheatsheets/File_Upload_Cheat_Sheet.html).
- [RFC 9700: OAuth security best current practice](https://www.rfc-editor.org/rfc/rfc9700), [RFC 8725: JWT best practices](https://www.rfc-editor.org/rfc/rfc8725), and [OpenID Connect Core](https://openid.net/specs/openid-connect-core-1_0.html).

## Distributed systems and data-structure papers

- [Lamport: Time, Clocks, and the Ordering of Events](https://lamport.azurewebsites.net/pubs/time-clocks.pdf) — causal ordering and logical time.
- [Herlihy and Wing: Linearizability](https://cs.brown.edu/~mph/HerlihyW90/p463-herlihy.pdf) — the concurrent-object correctness condition.
- [Gilbert and Lynch: CAP proof](https://users.ece.cmu.edu/~adrian/731-sp04/readings/GL-cap.pdf) — partition, consistency, and availability assumptions.
- [Raft paper](https://raft.github.io/raft.pdf) and [Paxos Made Simple](https://lamport.azurewebsites.net/pubs/paxos-simple.pdf) — consensus safety and leadership.
- [FLP impossibility paper](https://groups.csail.mit.edu/tds/papers/Lynch/jacm85.pdf) — termination limits in the asynchronous crash-fault model.
- [Dynamo](https://www.allthingsdistributed.com/files/amazon-dynamo-sosp2007.pdf) — placement, replication, versioning, and anti-entropy in a specific design.
- [Spanner](https://research.google/pubs/spanner-googles-globally-distributed-database/) and [Chubby](https://research.google/pubs/the-chubby-lock-service-for-loosely-coupled-distributed-systems/) — concrete coordination/time assumptions.
- [Pugh: Skip Lists](https://www.cs.umd.edu/~pugh/skipLists/skipLists.pdf), [Bloom's paper](https://dl.acm.org/doi/10.1145/362686.362692), and [Bloom-filter sizing analysis](https://pages.cs.wisc.edu/~cao/papers/summary-cache/node8.html).
- [HyperLogLog](https://algo.inria.fr/flajolet/Publications/FlFuGaMe07.pdf) and [HyperLogLog in Practice](https://research.google/pubs/hyperloglog-in-practice-algorithmic-engineering-of-a-state-of-the-art-cardinality-estimation-algorithm/).
- [RFC 9162: Certificate Transparency](https://www.rfc-editor.org/rfc/rfc9162) — a concrete Merkle-tree/proof protocol.
- [Jepsen consistency models](https://jepsen.io/consistency) — a useful operational map of consistency guarantees.

## Messaging and production patterns

- [RabbitMQ acknowledgements](https://www.rabbitmq.com/docs/confirms) and [queues](https://www.rabbitmq.com/docs/queues).
- [Kafka design](https://kafka.apache.org/41/design/design/) — the cited 4.1 documentation's replication and delivery model.
- [Redis distributed locks](https://redis.io/docs/latest/develop/clients/patterns/distributed-locks/) and [Kleppmann's locking analysis](https://martin.kleppmann.com/2016/02/08/how-to-do-distributed-locking.html) — read assumptions and arguments together.
- [Debezium outbox router](https://debezium.io/documentation/reference/stable/transformations/outbox-event-router.html), [PostgreSQL two-phase transactions](https://www.postgresql.org/docs/current/two-phase.html), and [Azure saga pattern](https://learn.microsoft.com/en-us/azure/architecture/patterns/saga).
- [Stripe idempotency](https://docs.stripe.com/api/idempotent_requests) and [AWS safe retries](https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/) — concrete request-identity contracts.
- [Azure CQRS](https://learn.microsoft.com/en-us/azure/architecture/patterns/cqrs) and [event sourcing](https://learn.microsoft.com/en-us/azure/architecture/patterns/event-sourcing) — pattern scope and trade-offs.
- [Automerge](https://automerge.org/docs/) — a maintained CRDT implementation and its specific document model.

## Reliability, observability, infrastructure, and delivery

- [Google SRE book](https://sre.google/sre-book/table-of-contents/) and [workbook](https://sre.google/workbook/table-of-contents/) — freely available primary operational teaching.
- [AWS retries/backoff/jitter](https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/) and [caching challenges](https://aws.amazon.com/builders-library/caching-challenges-and-strategies/).
- [OpenTelemetry concepts](https://opentelemetry.io/docs/concepts/), [Prometheus metric types](https://prometheus.io/docs/concepts/metric_types/), and [W3C Trace Context](https://www.w3.org/TR/trace-context/).
- [Brendan Gregg's USE method](https://www.brendangregg.com/usemethod.html) — resource-oriented performance diagnosis.
- [Docker concepts](https://docs.docker.com/get-started/docker-concepts/the-basics/what-is-a-container/), [Dockerfile reference](https://docs.docker.com/reference/dockerfile/), and [Compose](https://docs.docker.com/compose/).
- [AWS Well-Architected](https://docs.aws.amazon.com/wellarchitected/latest/framework/welcome.html), [shared responsibility](https://aws.amazon.com/compliance/shared-responsibility-model/), and [VPC](https://docs.aws.amazon.com/vpc/latest/userguide/what-is-amazon-vpc.html).
- [Kubernetes architecture](https://kubernetes.io/docs/concepts/architecture/), [workloads](https://kubernetes.io/docs/concepts/workloads/), [resource management](https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/), and [probes](https://kubernetes.io/docs/concepts/configuration/liveness-readiness-startup-probes/).
- [SLSA](https://slsa.dev/) and [OpenFeature](https://openfeature.dev/docs/reference/intro/) — supply-chain provenance and feature-flag interfaces.

## Books for deeper study

- [Designing Data-Intensive Applications](https://dataintensive.net/) — storage, replication, distributed data, and trade-offs. The course does not require purchasing it.
- [Operating Systems: Three Easy Pieces](https://pages.cs.wisc.edu/~remzi/OSTEP/) — free foundations with exercises.
- [Site Reliability Engineering](https://sre.google/books/) — free online books connecting operational practice to service objectives.

Use references to answer a specific uncertainty: “Does this acknowledgement mean persisted or applied?” is a better reading goal than collecting more links. If a product's behavior differs from a conceptual example, preserve the concept and update the implementation-specific claim with a versioned source.
