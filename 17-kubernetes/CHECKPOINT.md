# Checkpoint: Kubernetes

Attempt without notes. Explain mechanisms and draw histories before opening the rubric.

## Scenario

A Deployment requests five replicas. Two pods remain Pending, one crash-loops, and two Running pods have no Service traffic.

## Questions

1. Trace reconciliation through API, scheduler, controllers, kubelet, and workload objects.
2. Distinguish Deployment, ReplicaSet, Pod, Service, and Ingress/controller responsibilities.
3. Investigate requests/limits, events, probes, selectors, ports, and network policy.
4. Design rolling update, graceful drain, autoscaling, secret/config updates, and persistent-volume behavior.

## Evidence to produce

Diagnose each symptom from object status/events and application evidence in a disposable cluster, or write the exact evidence plan if no cluster is available.

Score each answer: 0 = names only; 1 = correct happy path; 2 = failure mechanism and repair; 3 = assumptions, trade-offs, and validation. Pass when every question reaches 2 and the evidence is reproducible. Revisit weak chapters before advancing.

<details><summary>Review rubric after attempting</summary>

Lifecycle state is not readiness, and desired replicas do not create missing capacity. Secrets are not encrypted merely by base64 encoding. Kubernetes coordinates workloads but does not implement application data correctness.

</details>

[Section reading order](README.md) · [Progress](../PROGRESS.md) · [Project briefs](../projects/README.md)
