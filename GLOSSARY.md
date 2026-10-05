# Software engineering glossary

Definitions establish the vocabulary used throughout the course; linked chapters supply mechanisms, examples, and failure reasoning. Similar words are kept distinct where confusing them changes a design.

## Relay's domain

**User:** A person recognized by Relay's identity system. A user can belong to several workspaces.

**Workspace:** A collaboration boundary owning tasks, comments, attachments, and membership policy. _Avoid:_ using “account” interchangeably for a user and a workspace.

**Membership:** A user's relationship to a workspace, including the permissions that relationship grants.

**Task:** A unit of work within one workspace, with a title, lifecycle state, and change history.

**Comment:** A contribution to a task's discussion, owned by an author and subject to workspace visibility.

**Attachment:** A file associated with workspace content and governed by an upload/validation/publication lifecycle.

**Notification:** A user-facing notice about a relevant event. Delivery attempts and the underlying business event are distinct.

**Export:** A generated representation of selected workspace data under a defined selection/time policy.

**Operation:** One logical intent such as creating an export. An operation may have several execution attempts.

**Attempt:** One execution try for an operation. _Avoid:_ using a new attempt identity as a new business-operation identity during a retry.

## Execution and representation

**Process:** A running program instance with an address space, identity, resources, and execution state. [Runtime](01-foundations/runtime-and-memory.md)

**Thread:** An execution path within a process, normally sharing its address space while retaining its own stack/register state. [Runtime](01-foundations/runtime-and-memory.md)

**Concurrency:** Overlapping lifetimes of work under coordination. **Parallelism:** simultaneous execution of work. [Concurrency](01-foundations/concurrency-and-io.md)

**Race condition:** A correctness failure dependent on uncontrolled timing or interleaving. [Concurrency](01-foundations/concurrency-and-io.md)

**Mutex:** A mutual-exclusion mechanism for a critical section. **Semaphore:** a counted-permit synchronization mechanism. [Concurrency](01-foundations/concurrency-and-io.md)

**Deadlock:** A state where participants cannot proceed because each waits for resources/progress held by others in a cycle. [Transactions](06-databases/transactions-and-mvcc.md)

**Virtual memory:** A process address-space abstraction mapped to physical memory and other backing resources. [Runtime](01-foundations/runtime-and-memory.md)

**File descriptor:** A process-local handle for an open operating-system resource. [Linux](02-operating-systems-linux/linux-debugging.md)

**Blocking:** An operation may suspend the calling thread while waiting. **Asynchronous:** completion is delivered separately from the initiating call's direct return. [I/O](01-foundations/concurrency-and-io.md)

**Backpressure:** Feedback or admission behavior that prevents producers from indefinitely outrunning consumers. [Concurrency](01-foundations/concurrency-and-io.md)

**Serialization:** A mapping from structured values to a transferable/storable representation. **Encoding:** a mapping between representations, such as text to UTF-8 bytes. [Data](01-foundations/data-and-time.md)

**Hash:** A fixed-size digest derived from input under a particular algorithm and purpose. It is not necessarily cryptographic or suitable for passwords. [Data](01-foundations/data-and-time.md)

**Wall clock:** A source of civil/absolute time subject to synchronization and adjustment. **Monotonic clock:** a local elapsed-time source that avoids wall-clock jumps under its platform contract. [Time](01-foundations/data-and-time.md)

## Networking and browser

**Packet:** A network-layer unit forwarded through a network. **Frame:** a link-layer unit used on a local link. [Packets](03-networking/packets-to-connections.md)

**Port:** A transport-layer endpoint identifier on a host. **Socket:** an operating-system communication endpoint. [Connections](03-networking/packets-to-connections.md)

**TCP:** A transport protocol providing an ordered reliable byte stream under its connection/failure semantics. **UDP:** a datagram transport without TCP's ordering/retransmission service. [Connections](03-networking/packets-to-connections.md)

**Flow control:** Protection against overwhelming a receiver. **Congestion control:** adaptation to shared network capacity. [Connections](03-networking/packets-to-connections.md)

**DNS:** A delegated naming system whose records help locate services and other domain information. [DNS](03-networking/dns-tls-http.md)

**TLS:** A protocol for authenticated protected communication under configured trust and key policies. [TLS](03-networking/dns-tls-http.md)

**Reverse proxy:** An intermediary acting in front of servers. **Load balancer:** a component selecting destinations among service instances. [Edges](03-networking/edges-and-realtime.md)

**CDN:** Distributed serving infrastructure that places content and related edge capabilities closer to users. [Edges](03-networking/edges-and-realtime.md)

**Origin:** A browser security identity based on scheme, host, and port. **Site:** a distinct browser concept used in policies such as SameSite cookies. [Browser security](08-security/browser-and-input-security.md)

**DOM:** The document's object representation. **Layout:** computing geometry. **Paint:** producing drawing work. **Compositing:** combining rendered layers into a presentation. [Browser internals](04-frontend/browser-internals.md)

**Closure:** A function together with access to its lexical environment. [JavaScript](04-frontend/javascript-runtime.md)

**Microtask:** A scheduled job such as a promise reaction, processed at host-defined microtask checkpoints. [JavaScript](04-frontend/javascript-runtime.md)

**Structural typing:** Compatibility based primarily on shape/capabilities rather than declared nominal identity. [TypeScript](04-frontend/typescript-boundaries.md)

**Render:** React's calculation of a UI description. **Commit:** applying selected changes to the host UI. [React](04-frontend/react-mental-model.md)

**Hydration:** Connecting client behavior to a compatible server-rendered UI representation. [Rendering](04-frontend/rendering-architectures.md)

**Server state:** A client's local representation of remotely authoritative data. [State ownership](04-frontend/state-and-data-fetching.md)

**Optimistic update:** A client prediction of a mutation's result before authoritative confirmation. [State ownership](04-frontend/state-and-data-fetching.md)

## APIs and data

**Safe method:** An HTTP method whose requested semantics do not ask for a state-changing action. **Idempotent operation:** repetition has the same intended effect as one execution under its defined scope. [APIs](05-backend/api-design.md)

**Idempotency key:** A stable caller-supplied identity for one logical operation, scoped and enforced by the server. [Idempotency](20-production-patterns/idempotency-and-deduplication.md)

**Cursor:** A token identifying a continuation position and relevant query context. It is not inherently a stable snapshot or an authorization credential. [Pagination](05-backend/api-design.md)

**Connection pool:** A bounded manager of reusable connections and their acquisition/release lifecycle. [Backend](05-backend/server-architecture.md)

**Constraint:** A rule enforced by the data authority over acceptable stored state. [Relational model](06-databases/relational-model.md)

**Normalization:** Organization of facts to reduce redundancy and update anomalies. **Denormalization:** deliberate duplication/derivation for an access pattern with a maintenance policy. [Relational model](06-databases/relational-model.md)

**Index:** An auxiliary organization of keys and references used to accelerate particular access paths. [Indexes](06-databases/indexes-and-query-plans.md)

**Selectivity:** How strongly a predicate narrows a population. **Cardinality:** a count, commonly distinct values or estimated rows depending on context. [Query plans](06-databases/indexes-and-query-plans.md)

**Transaction:** A unit of database work with an atomic commit/abort boundary and a specified isolation/durability contract. [Transactions](06-databases/transactions-and-mvcc.md)

**MVCC:** Concurrency control using multiple versions and visibility rules for readers/writers. [Transactions](06-databases/transactions-and-mvcc.md)

**Write skew:** Concurrent transactions update different items after reading a shared condition and jointly violate an invariant. [Transactions](06-databases/transactions-and-mvcc.md)

**WAL:** Write-ahead logging, where required log records become durable before corresponding data-page persistence. [Recovery](06-databases/storage-and-recovery.md)

**Checkpoint:** A coordinated recovery/persistence boundary limiting required recovery work. It is not a backup. [Recovery](06-databases/storage-and-recovery.md)

**Replication lag:** Delay or progress difference between authoritative writes and a replica's received/persisted/applied state. [Scaling](06-databases/scaling-and-nosql.md)

**Partition:** Either a divided data/stream range or a network communication failure, depending on context. **Shard:** a data partition assigned to a storage node/group. [Scaling](06-databases/scaling-and-nosql.md)

**Cache invalidation:** Marking/removing derived representations that no longer meet their freshness contract. [Caching](07-caching/cache-design.md)

**TTL:** Time to live under a particular authority's expiration rules. It does not inherently bound source-data age. [Caching](07-caching/cache-design.md)

**Cache stampede:** Many concurrent misses triggering duplicate regeneration work. **Hot key:** one key concentrating disproportionate traffic/cost. [Cache failures](07-caching/cache-failures.md)

## Security and identity

**Authentication:** Establishing a principal through accepted identity evidence. **Authorization:** deciding whether that principal may perform an action on a resource in context. [Trust](08-security/trust-and-authorization.md)

**Session:** An authenticated interaction lifecycle recognized across requests. **Cookie:** browser-managed scoped state that may be attached to HTTP requests. [Sessions](08-security/sessions-jwt-oauth.md)

**Bearer token:** A credential whose possession permits its authorized use under the protocol. **JWT:** a token format carrying claims, often signed; the format alone does not establish trust. [Tokens](08-security/sessions-jwt-oauth.md)

**OAuth:** A framework for delegated authorization. **OIDC:** an identity layer built on OAuth 2.0. **PKCE:** a code-redemption binding mechanism using a client-held verifier. [Identity protocols](08-security/sessions-jwt-oauth.md)

**CORS:** A browser-enforced cross-origin access permission mechanism. **CSRF:** an attack causing unwanted authenticated requests through ambient credentials. [Browser security](08-security/browser-and-input-security.md)

**XSS:** Untrusted content executing as script in a trusted application's origin. **SSRF:** attacker-directed server requests crossing a server-side network trust boundary. [Input security](08-security/browser-and-input-security.md)

**Salt:** A per-password non-secret value used in password hashing to defeat shared/precomputed guesses. [Password storage](08-security/trust-and-authorization.md)

## Messaging and coordination

**Event:** A recorded fact that occurred. **Command:** an intent requesting an action. A rejected command need not become the corresponding business event. [Event sourcing](20-production-patterns/cqrs-and-event-sourcing.md)

**Acknowledgement:** A protocol-specific statement of progress; its durability/processing scope must be named. [Queues](09-messaging-streaming/queues-and-workers.md)

**DLQ:** A dead-letter queue isolating failed/expired work for owned investigation and redrive. **Poison message:** content that repeatedly triggers deterministic failure. [Queues](09-messaging-streaming/queues-and-workers.md)

**Consumer group:** Consumers sharing partition assignments/progress within one logical subscription under the stream platform's model. **Offset:** a position in a partition log. [Kafka](09-messaging-streaming/kafka-and-event-streams.md)

**Partial failure:** Some components/communication paths fail while others continue, leaving participants with incomplete knowledge. [Distributed systems](10-distributed-systems/partial-failure-and-consistency.md)

**Linearizability:** Operations appear atomic between invocation and response while respecting real-time ordering. **Eventual consistency:** replicas converge under stated quiescence, communication, and repair assumptions. [Consistency](10-distributed-systems/partial-failure-and-consistency.md)

**Causal consistency:** Observations preserve causally related order while allowing concurrent events to differ in order. [Consistency](10-distributed-systems/partial-failure-and-consistency.md)

**Quorum:** A set of participating acknowledgements/observations whose intersection properties support a protocol's guarantees. [Quorums](10-distributed-systems/replication-and-quorums.md)

**Lease:** Temporary authority granted under an expiration/renewal contract. **Fencing token:** an ordered authority epoch checked by the protected resource to reject superseded work. [Leases](10-distributed-systems/leases-and-fencing.md)

**Consensus:** Agreement on decisions under a stated failure model, often used to maintain a committed replicated log. [Consensus](10-distributed-systems/consensus-and-leadership.md)

**Happens-before:** A causal partial order derived from local ordering, message send/receive, and transitivity. [Logical time](10-distributed-systems/logical-time.md)

**Lamport clock:** A logical counter preserving the implication from happens-before to increasing timestamp. **Vector clock:** per-actor logical progress enabling causal comparison under its model. [Logical time](10-distributed-systems/logical-time.md)

## System data structures

**Bloom filter:** A compact probabilistic membership structure with false positives and no false negatives under its ordinary insert-only assumptions. [Bloom filters](11-system-data-structures/bloom-filters.md)

**Consistent hashing:** A placement family limiting key movement when membership changes. [Placement](11-system-data-structures/consistent-hashing.md)

**B+ tree:** A balanced high-fanout ordered structure commonly using leaf entries and internal routing separators. [B+ trees](11-system-data-structures/b-plus-trees.md)

**LSM tree:** A storage organization combining mutable memory state with immutable sorted runs and compaction. [LSM trees](11-system-data-structures/lsm-trees.md)

**Compaction:** Reorganization/merging of stored runs or segments to manage versions, layout, and space under visibility rules. [LSM trees](11-system-data-structures/lsm-trees.md)

**Skip list:** An ordered linked structure with probabilistic shortcut levels. [Skip lists](11-system-data-structures/skip-lists.md)

**Merkle tree:** A recursive content-hash hierarchy supporting efficient comparison or proofs relative to a root. [Merkle trees](11-system-data-structures/merkle-trees.md)

**HyperLogLog:** A compact mergeable sketch estimating distinct cardinality from hash statistics. [HLL](11-system-data-structures/hyperloglog.md)

**Inverted index:** A term-to-document/posting mapping supporting text retrieval and related search operations. [Search](11-system-data-structures/inverted-indexes.md)

## Operations and patterns

**Circuit breaker:** A policy temporarily suppressing calls after observed failure and cautiously probing recovery. **Bulkhead:** an isolation boundary for resource capacity. [Reliability](13-reliability/resilience-and-recovery.md)

**Load shedding:** Deliberate rejection/removal of work to preserve useful service under overload. **Jitter:** randomized timing used to reduce synchronized retries or renewals. [Reliability](13-reliability/resilience-and-recovery.md)

**RPO:** Target maximum acceptable data-loss window. **RTO:** Target time to restore useful service after disruption. [Recovery](13-reliability/resilience-and-recovery.md)

**SLI:** A measured service behavior. **SLO:** an objective for that behavior. **SLA:** a contractual service commitment with defined consequences. [SLOs](14-observability/slos-and-alerting.md)

**Trace:** Related work across an operation. **Span:** a timed unit/relationship within tracing. [Observability](14-observability/logs-metrics-traces.md)

**Container:** A packaged process environment using isolation/resource mechanisms. **Image:** immutable filesystem/configuration input for starting containers. [Containers](15-containers/containers-and-docker.md)

**Pod:** Kubernetes's scheduling/lifecycle unit for tightly coupled containers. **Reconciliation:** repeatedly driving observed state toward declared desired state. [Kubernetes](17-kubernetes/kubernetes-model.md)

**Outbox:** A durable event-publication intent committed with a local business change. **Inbox:** a consumer's durable identity/effect coordination boundary. [Reliable patterns](20-production-patterns/outbox-inbox-and-sagas.md)

**Saga:** A sequence of local transactions with explicit recovery/compensation across a workflow. **Compensation:** a new action addressing a prior effect, not literal rollback of history. [Sagas](20-production-patterns/outbox-inbox-and-sagas.md)

**CQRS:** Separation of command and query models. **Event sourcing:** authoritative state represented as an event history. [Models](20-production-patterns/cqrs-and-event-sourcing.md)

**Projection:** A derived representation built from authoritative facts/history. **Audit log:** a protected record of accountable actions and outcomes. [Data lifecycle](20-production-patterns/data-lifecycle-and-tenancy.md)

**Canary:** A controlled release to a limited population before broader exposure. **Feature flag:** a managed runtime exposure/behavior decision with a lifecycle. [Delivery](18-ci-cd/safe-delivery.md)
