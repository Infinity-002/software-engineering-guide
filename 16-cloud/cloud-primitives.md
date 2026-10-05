# Cloud primitives and failure domains

Cloud services rent capabilities: compute, storage, networking, identity, and managed operations. They change who maintains components, but the application still owns its data model, trust boundaries, failure contracts, and cost. Start with those concepts before memorizing service names.

## Compute and storage choices

Virtual machines provide an operating-system environment with flexible runtime control and patching responsibility. Containers package processes and can run on VMs or managed platforms. Serverless functions run bounded invocations under a provider-managed execution model; they can simplify bursty event handling but introduce concurrency limits, cold paths, time limits, and external-state requirements.

Object storage manages blobs addressed by keys with metadata and service-defined consistency. It suits attachments, media, backups, and artifacts. Block storage presents volumes to machines and suits filesystems/databases that need block access. File storage exposes shared filesystem semantics. These are different APIs and performance models; an object store is not simply a mounted disk with infinite IOPS.

Managed databases reduce operational work such as provisioning and backups but do not eliminate query tuning, schema migration risk, connection limits, or restore validation. Managed queues/caches similarly retain their delivery and consistency semantics. Know the configured service tier and regional guarantees rather than assuming “managed” means no failure.

## Network boundaries

A VPC is a logically isolated network environment. Subnets divide address space and often align with availability zones. Route tables decide where traffic goes; security groups/firewall rules decide which traffic is allowed. A private subnet can still have outbound Internet access through a NAT path, while inbound reachability depends on routes and exposed endpoints.

```text
Internet -> DNS/CDN -> public load balancer
                         |
                 private API subnets
                    /          \
           database subnets   service endpoints/egress
```

“Private” does not authenticate the caller. Apply service identity, least privilege, and TLS where appropriate. Outbound access deserves limits too: SSRF can exploit a service's network privileges. NAT gateways, cross-zone traffic, and data egress can become significant cost and capacity factors.

## Identity and failure domains

IAM governs which principal can perform which provider action on which resource. Prefer workload identities and short-lived credentials over embedded long-lived keys. Separate deployment authority from runtime authority. A web process that can modify its own IAM role or delete backups turns an application compromise into an infrastructure compromise.

Availability zones are separate provider-defined failure domains within a region; regions provide broader geographic separation with larger latency and operational trade-offs. Multi-zone deployment can handle some infrastructure failures, but a bad release or shared dependency can affect all zones. Multi-region design adds data replication, conflict/failover, routing, and cost questions. It is not a checkbox for infinite availability.

## Autoscaling follows a signal, not intuition

Horizontal autoscaling adds instances; vertical scaling changes instance capacity. Choose a signal tied to the workload: CPU for compute-heavy work, queue age/backlog and processing rate for workers, concurrency/latency where appropriate. Account for warmup, cooldown, minimum capacity, and downstream limits.

Adding API replicas can multiply database pools and overload PostgreSQL. Adding workers can overload an email provider. Autoscaling needs a system-wide capacity budget and admission control. Scale-in requires draining and safe ownership transfer; deleting instances with active work can cause retries and latency spikes.

## Representative AWS mapping

| Concept | Representative AWS service |
|---|---|
| VM compute | EC2 |
| Managed containers | ECS, EKS, Fargate in supported combinations |
| Functions | Lambda |
| Object/block storage | S3 / EBS |
| Managed relational database | RDS, Aurora |
| Load balancing | Elastic Load Balancing |
| Network isolation | VPC |
| Identity | IAM |
| DNS/CDN | Route 53 / CloudFront |
| Queue/event delivery | SQS / SNS / EventBridge, with different semantics |
| Managed cache | ElastiCache |

This mapping is orientation, not an assertion that services are interchangeable or have identical guarantees. Verify current quotas, regional support, pricing, and durability/consistency documentation before implementation.

## Cost is an architectural signal

Estimate requests, compute-seconds, stored bytes, replicated bytes, IOPS, log volume, and network transfer separately. A cheap compute instance can sit behind expensive egress or unbounded telemetry. Set budgets and resource ownership, but do not optimize cost by silently weakening backups or security.

Use infrastructure as code to make environment changes reviewable and reproducible. State drift, secrets, and provider-side changes still need detection. A disaster-recovery plan must include infrastructure definitions, identities, keys, and DNS/routing, not only database snapshots.

## Exercises

1. **Design:** Deploy Relay across two zones with one region. Mark public/private paths, identities, data authority, and correlated failure risks.
2. **Predict:** API autoscaling doubles replicas and latency worsens. Explain the database-pool mechanism.
3. **Calculate:** Estimate monthly attachment storage and egress from uploads/day, average size, retention, and downloads/upload.
4. **Interview:** Choose VM, managed containers, or functions for a long-running WebSocket service and a nightly image job.

<details><summary>Hints</summary>

Count all replicas' connection limits together. Functions suit bounded event work when duration/concurrency constraints fit; long-lived connections need a platform explicitly supporting that lifecycle. Cost estimates should include replication, retries, and retained versions.

</details>

## Further reading and connections

[AWS Well-Architected Framework](https://docs.aws.amazon.com/wellarchitected/latest/framework/welcome.html), [AWS shared responsibility](https://aws.amazon.com/compliance/shared-responsibility-model/), and [AWS VPC concepts](https://docs.aws.amazon.com/vpc/latest/userguide/what-is-amazon-vpc.html). Connect to [recovery](../13-reliability/resilience-and-recovery.md), [uploads](../12-fullstack/realtime-and-uploads.md), and [Kubernetes](../17-kubernetes/kubernetes-model.md).
