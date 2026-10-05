# Kubernetes as a reconciliation system

Running three containers is easy until one machine fails, a release needs gradual replacement, addresses change, and workloads compete for resources. Kubernetes lets you declare desired state and uses controllers to continually reconcile observed state toward it. It automates coordination work; it does not decide your application's correctness policy.

## Control plane and workers

The API server exposes cluster state and authorization. The scheduler chooses nodes for unscheduled pods according to resources and constraints. Controllers observe objects and create/update other objects to reduce differences from desired state. Persistent control-plane state is commonly stored in etcd. Worker nodes run a kubelet and container runtime, while networking/storage components provide the required integration.

```text
desired objects -> API/control-plane state -> controllers/scheduler
                                             |
                                      worker kubelets
                                             |
                                           pods
```

A pod is the scheduling/lifecycle unit for one or more tightly coupled containers sharing networking and configured storage. Containers in a pod can communicate through the pod's shared network namespace. A pod is replaceable; its identity/address is not a durable server identity. Put unrelated independently scaled services in separate pods.

## Workload and routing abstractions

A Deployment manages rollout and desired replicas through ReplicaSets. A ReplicaSet maintains the required number of matching pods. A Service gives a stable discovery/routing abstraction over selected endpoints. It does not guarantee an individual request succeeds or that all endpoints have current data.

Ingress describes HTTP routing under an installed controller; creating the object alone does not create a functioning external proxy in every cluster. Gateway API is another evolving routing API family. Cluster networking depends on the installed network implementation, and NetworkPolicy enforcement depends on support/configuration. Do not infer isolation merely from different namespaces.

ConfigMaps carry non-secret configuration. Secrets carry sensitive configuration through Kubernetes access controls, but base64 representation is not encryption. Configure storage encryption and RBAC appropriately, limit mounts/access, and understand how updates reach running processes. A secret changed in the API is not necessarily reread by an application using an environment variable.

## Scheduling and resource limits

Requests inform scheduling and capacity allocation. Limits constrain runtime usage according to resource behavior: CPU limits can throttle, while memory limit breaches can lead to termination. A too-small request can permit overpacking; a too-small CPU limit can create latency even when the node has apparent capacity. Measure application demand and reserve headroom for bursts and system components.

Volumes connect pods to storage. Ephemeral storage disappears with its lifecycle; persistent volumes/claims express longer-lived storage needs under a storage class/provider. Scheduling across zones must respect volume topology. A StatefulSet helps manage stable identities and storage associations for stateful workloads, but it does not implement database replication or safe failover for you.

## Probes and rolling changes

Readiness determines eligibility for service traffic. Liveness can trigger restart when a process is unhealthy. Startup probes protect slow initialization from premature liveness failure. A readiness probe that performs an expensive query on every pod every second can itself overload a dependency. A liveness probe tied to a shared outage can trigger a restart storm.

Rolling updates temporarily mix versions and consume extra capacity or reduce available replicas depending on policy. Configure readiness, graceful termination, surge/unavailable budgets, and application compatibility. A successful rollout status does not prove the user journey or data migration is correct.

Horizontal pod autoscaling changes replica counts based on configured metrics. Resource requests affect utilization-based decisions. Scale-in must drain connections and jobs. A PodDisruptionBudget constrains certain voluntary disruptions; it does not prevent every crash, forceful deletion, or all workload-controller changes. Spread replicas across relevant failure domains to avoid losing them together.

## Diagnose the reconciliation chain

A pod Pending may lack resources, have scheduling constraints, or wait for storage. A CrashLoopBackOff indicates repeated container failure, not a root cause; inspect termination reason, previous logs, configuration, and probes. A Running pod can still be unready or unreachable due to selectors, ports, network policy, or application binding.

Use the object status, events, logs, and resource metrics to identify the stage that failed. Avoid editing live pods as the permanent fix when a controller will recreate them from the old template. Update the declarative source and verify reconciliation.

## Why not Kubernetes for a tiny application?

A managed application platform or a VM with a supervised process can satisfy simple needs with less operational surface. Kubernetes becomes useful when scheduling, rollout, policy, and platform consistency justify its control plane, networking, storage, and upgrade responsibilities. More abstractions mean more places to inspect when a request cannot reach a process.

## Exercises

1. **Predict:** A Deployment has three desired replicas but only two nodes with enough requested memory. What state and events do you expect?
2. **Debug:** Pods are Running, but the Service has no usable endpoints. Inspect readiness and selectors before blaming DNS.
3. **Implementation:** Deploy a disposable API, roll versions while sending traffic, and measure errors during drain.
4. **Design:** Configure probes for a service whose database can be temporarily unavailable without a process restart helping.
5. **Interview:** Explain Deployment, ReplicaSet, Pod, Service, and Ingress by the problem each solves.

<details><summary>Hints</summary>

Desired state can exceed available capacity. Running describes lifecycle, not service readiness. Probes should distinguish process-local failure from shared dependency failure, and rollout verification should include user-visible outcomes.

</details>

## Further reading and connections

[Kubernetes architecture](https://kubernetes.io/docs/concepts/architecture/), [workloads](https://kubernetes.io/docs/concepts/workloads/), [resource management](https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/), and [probes](https://kubernetes.io/docs/concepts/configuration/liveness-readiness-startup-probes/). Connect to [containers](../15-containers/containers-and-docker.md), [consensus](../10-distributed-systems/consensus-and-leadership.md), and [safe releases](../18-ci-cd/safe-delivery.md).
