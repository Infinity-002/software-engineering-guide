# Checkpoint: Cloud architecture

Attempt without notes. Explain mechanisms and draw histories before opening the rubric.

## Scenario

Relay expands to two zones. API autoscaling increases database failures, and attachment egress costs exceed compute costs.

## Questions

1. Choose compute, object/block storage, managed database, queue, and cache primitives from workload needs.
2. Draw VPC/subnet/routes/firewalls, public entry, private data paths, and IAM identities.
3. Explain zone/region failure domains and shared correlated risks.
4. Estimate storage, egress, replication, telemetry, and fleet-wide connections before changing scale policy.

## Evidence to produce

Produce a vendor-neutral architecture plus representative AWS mapping, a cost worksheet in Markdown, and a regional recovery outline.

Score each answer: 0 = names only; 1 = correct happy path; 2 = failure mechanism and repair; 3 = assumptions, trade-offs, and validation. Pass when every question reaches 2 and the evidence is reproducible. Revisit weak chapters before advancing.

<details><summary>Review rubric after attempting</summary>

Managed services retain limits and contracts. Network privacy is not authorization. Autoscaling respects downstream capacity, and multi-zone deployment does not protect against every shared failure.

</details>

[Section reading order](README.md) · [Progress](../PROGRESS.md) · [Project briefs](../projects/README.md)
