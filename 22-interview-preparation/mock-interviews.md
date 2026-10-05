# Four complete mock interview sessions

Use a timer and a blank document. Ask a partner to reveal the follow-ups gradually, or cover them while attempting the first prompt. The goal is reasoning under changing constraints, not recalling a diagram. Record assumptions and revisit them when new information arrives.

## Session 1: frontend engineering — 50 minutes

**0–5 minutes, requirements.** Build an accessible task-search page with filters, pagination, and editable titles. Ask about URL sharing, slow networks, keyboard use, and concurrent edits.

**5–20 minutes, implementation sketch.** Define state ownership, query keys, TypeScript runtime validation, component boundaries, and loading/error/empty states. Show one mutation path and how a title draft differs from server state. Use semantic controls and specify focus behavior after save/failure.

**20–30 minutes, injected failure.** The user types quickly; responses arrive out of order. Then an optimistic edit fails after a second edit succeeds. Explain request relevance and operation-specific reconciliation. A whole-cache rollback is no longer sufficient.

**30–40 minutes, performance.** The list has 10,000 rows and typing becomes slow. Choose measurements before proposing memoization. Discuss pagination/virtualization, main-thread work, bundle splitting, and accessibility consequences.

**40–50 minutes, testing and architecture.** Write behavior tests for stale response, failed save, and keyboard operation. Discuss CSR versus server rendering for this private page and a public task-share page.

<details><summary>Evaluation and follow-up</summary>

Look for explicit authority, stable keys, correct event/effect distinction, runtime parsing, relevance guards, and preservation of user intent. Penalize treating TypeScript as input validation or using an effect for a purchase-like mutation. Follow up by revoking workspace access while stale data remains cached. A strong answer removes sensitive state and rechecks permission on the server.

</details>

## Session 2: backend and database — 55 minutes

**0–8 minutes, contract.** Design an API for reserving the last available seat in a workshop. Define authenticated principal, reservation lifecycle, expiry, retries, and whether payment is in scope.

**8–23 minutes, persistence.** Propose tables, constraints, and the transaction/conditional-update boundary. Show two concurrent requests and prove capacity cannot go negative. Design error responses and status lookup.

**23–33 minutes, ambiguous outcome.** The database commits but the response is lost. The client retries on another API replica. Introduce a durable idempotency key with request fingerprint and explain simultaneous retries.

**33–43 minutes, asynchronous work.** A successful reservation must trigger an email. The process crashes before publication. Use an outbox, then explain a worker crash after email submission before acknowledgement. State the external provider limitation.

**43–55 minutes, performance/debugging.** A report endpoint becomes slow at 50 million reservations. Inspect plan, statistics, indexes, pool wait, and locks. Discuss read replicas and why a new reservation may not appear immediately there.

<details><summary>Evaluation and follow-up</summary>

The core invariant belongs in authoritative atomic state. The answer must distinguish local transaction, event intent, broker acknowledgement, and external effect. An in-memory mutex or “check then insert” without a constraint is insufficient. Follow up with reservation expiry racing payment confirmation; expect a versioned state machine and a business compensation policy.

</details>

## Session 3: full-stack production incident — 45 minutes

**0–5 minutes, symptom.** Users report that task saves hang after a release. Ask for scope, timeline, recent changes, and whether writes eventually appear.

**5–15 minutes, evidence.** Available facts: browser requests take five seconds; API SQL spans are short; pool wait is high; provider calls take three seconds; database CPU is low. Choose the next discriminating measurement and draw the request path.

**15–25 minutes, mitigation.** The release opened transactions before calling a provider. Explain a safe rollback/flag action and how to verify recovery. Discuss why adding replicas may worsen pool demand.

**25–35 minutes, repair.** Move external work out of long transactions using a versioned workflow. Preserve consistency when the underlying task changes during the call. Add timeout, cancellation, and unknown-outcome handling.

**35–45 minutes, prevention.** Define instrumentation, fault-injection tests, rollout signals, and an incident write-up. Explain how the UI should preserve a draft during uncertain outcomes.

<details><summary>Evaluation and follow-up</summary>

Strong candidates distinguish observations from hypotheses, stabilize before speculative tuning, and verify user outcomes. They connect browser behavior, server queueing, transaction ownership, and external uncertainty. Follow up with a failed rollback caused by a destructive schema migration; expect expand/contract and recovery reasoning.

</details>

## Session 4: system design — 60 minutes

**0–10 minutes, requirements.** Design a distributed scheduler for millions of recurring jobs. Clarify precision, time zones, missed-run policy, cancellation, tenant limits, and side-effect guarantees.

**10–20 minutes, estimates and model.** Estimate average/peak due runs and worker capacity. Define schedule, run, attempt, and effect identities. Specify APIs and state transitions.

**20–35 minutes, architecture.** Start with a database-backed scheduler, then add partition ownership and durable dispatch only where the workload requires it. Explain due-time indexing, queue backpressure, outbox, and replay.

**35–45 minutes, adversarial follow-ups.** The owner pauses beyond lease expiry, another owner takes over, then the old one resumes. A clock jumps backward. A worker completes a payment but fails to acknowledge. Explain which boundary uses fencing, uniqueness, monotonic waiting, and provider idempotency.

**45–55 minutes, operations/security.** Define dispatch-lateness SLI, stale-owner telemetry, DLQ ownership, recovery after a region outage, and per-tenant authorization/quotas. Discuss signed workload definitions versus arbitrary executable code.

**55–60 minutes, trade-offs.** Remove one unnecessary component and state the measured condition that would justify adding it later.

<details><summary>Evaluation and follow-up</summary>

The design must not equate lease expiry with stopping old execution, wall time with safe duration, or queue delivery with one business effect. It should preserve durable run identity through retries and state the missed-run policy. Follow up with one million schedules at the top of the hour to test skew and admission reasoning.

</details>

## Exercises

Run each session twice, changing one requirement on the second attempt. Score requirement clarity, correctness, failure reasoning, evidence, security, and communication from 0–3 each. Write one concrete correction per category rather than “study more.” Reattempt weak mechanisms after completing their chapter exercise.

## Further reading and connections

Use [reasoning questions](reasoning-interviews.md), [the system-design method](../19-system-design/methodology.md), [leases](../10-distributed-systems/leases-and-fencing.md), and [incident cases](../21-case-studies/incident-lab.md). Primary references are collected in [REFERENCES.md](../REFERENCES.md); [Google SRE incident management](https://sre.google/sre-book/managing-incidents/) supports the incident session.
