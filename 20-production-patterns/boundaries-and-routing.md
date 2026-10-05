# Gateways, BFFs, and service discovery

Relay's browser now calls task, notification, and attachment services. Routing, authentication integration, and client orchestration become repetitive. Three patterns can simplify the boundary, but each creates a new component whose failure and ownership must be understood.

## Pattern 1: API gateway

**Problem and naive solution.** Every client knows every service address and repeats authentication, throttling, and protocol rules. Updating service topology requires client changes, and policy becomes inconsistent.

**Mechanism.** A gateway provides a stable entry point and routes requests to services. It can enforce coarse authentication, request limits, protocol adaptation, and telemetry. Services still enforce resource-level authorization and business rules because the gateway may lack current domain context and internal calls can bypass it.

**Example.** `/api/tasks/*` routes to task APIs, `/api/uploads/*` to upload-intent handling, with consistent trace propagation and body limits. The gateway validates an external credential and forwards authenticated context through a trusted internal mechanism rather than accepting arbitrary caller-supplied identity headers.

**Failure modes.** A bad gateway configuration affects every route. Aggregating too much business logic turns it into a tightly coupled central service. Mismatched proxy/backend parsing creates security risk. Retrying a mutation automatically at the gateway can duplicate effects unless the route contract permits it.

**Trade-offs and use.** Gateways centralize common policy and hide topology but add latency, operational dependence, and a potential bottleneck. Scale and isolate them according to traffic, preserve end-to-end deadlines, and test route changes. For one small API, a reverse proxy may already provide everything needed; avoid an elaborate gateway product without a concrete requirement.

## Pattern 2: backend-for-frontend (BFF)

**Problem and naive solution.** A browser and mobile client need different data shapes, yet both make many calls to generic microservices. Each client reconstructs orchestration and handles inconsistent failures.

**Mechanism.** A BFF exposes operations tailored to a client experience and composes downstream data. It can keep sensitive provider tokens server-side while maintaining a browser session, or combine task summary and notification count into one page request.

**Example.** Relay's mobile home endpoint returns a compact summary with pagination cursors; the desktop editor endpoint returns richer metadata. The BFF parallelizes independent reads and defines partial-failure behavior for optional panels. Domain changes still go through authoritative services rather than duplicating business rules in every BFF.

**Failure modes.** One slow optional dependency delays the entire page. Per-client BFFs drift in authorization or validation. Large aggregation responses overfetch and become difficult to cache. Teams create a BFF for every UI fragment and end up with more network hops than before.

**Trade-offs and use.** Use a BFF when client-specific composition, security, or release ownership is substantial. It can reduce client complexity while increasing backend components. Avoid it when one well-designed API serves clients cleanly; a new service should eliminate meaningful complexity, not just relocate a few field names.

## Pattern 3: service discovery

**Problem and naive solution.** Hard-coded IP addresses fail as instances are replaced or scaled. A manually edited address list becomes stale during incidents.

**Mechanism.** A registry, DNS, platform service abstraction, or control plane maps service identity to current endpoints. Client-side discovery lets clients select instances; server-side discovery puts selection behind a proxy/load balancer. Health and membership updates propagate over time, so clients must tolerate stale entries and failed connections.

**Example.** Relay workers resolve a task service name, pool connections, and retry safe operations against current endpoints within a deadline. Kubernetes Services or a managed load balancer can supply this abstraction without an application-built registry.

**Failure modes.** Registry outage, stale DNS caches, long-lived pinned connections, and flapping health checks can all misroute or concentrate work. A service registration is not proof that the process can serve every operation. Connection reuse can outlive discovery TTL and needs lifecycle policy.

**Trade-offs and use.** Discovery decouples identity from location but adds control-plane state and convergence delay. Use the platform mechanism when it meets requirements. Avoid a custom discovery service for a static tiny deployment; operational simplicity may dominate hypothetical scaling flexibility.

## Module boundaries before service boundaries

A modular monolith can make task, attachment, and notification ownership explicit through interfaces and transaction rules while sharing one deployment. Extract a service when independent scaling, failure isolation, team ownership, or release cadence justifies network coordination. Shared database writes across nominally independent services can preserve tight coupling while losing local-call simplicity.

An interface should hide internal choices and expose a coherent capability. A gateway cannot repair a badly chosen service boundary that requires six synchronous calls to enforce one invariant. Trace the user operation and count coordination points before deciding extraction improved the system.

## Exercises

1. **Design:** Decide which checks belong in gateway, BFF, and task service for editing a private task.
2. **Predict:** Discovery removes a failed endpoint, but clients keep using it. Explain DNS and connection-pool lifetimes.
3. **Debug:** A mobile home request fails because an optional badge-count service is down. Define a partial-result contract.
4. **Interview:** Give a concrete reason to extract one Relay module into a service and a reason to keep another local.

<details><summary>Review criteria</summary>

Business authority stays clear, optional dependencies have bounded budgets, and discovery is treated as eventually propagated routing knowledge. The design accounts for bypass/internal calls rather than delegating all authorization to the edge.

</details>

## Further reading and connections

[Envoy architecture](https://www.envoyproxy.io/docs/envoy/latest/intro/arch_overview/arch_overview), [Azure BFF pattern](https://learn.microsoft.com/en-us/azure/architecture/patterns/backends-for-frontends), and [Kubernetes Services](https://kubernetes.io/docs/concepts/services-networking/service/). Connect to [proxies](../03-networking/edges-and-realtime.md), [backend architecture](../05-backend/server-architecture.md), and [Relay evolution](../21-case-studies/relay-evolution.md).
