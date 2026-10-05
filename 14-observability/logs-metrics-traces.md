# Logs, metrics, traces, and request diagnosis

“The request took five seconds” is a symptom. Observability should let you determine whether those seconds were spent waiting for a pool, executing SQL, calling another service, retrying, or rendering in the browser. Instrument boundaries that explain work and waiting.

## Three signals, different questions

Logs record discrete events with context. Metrics summarize numerical behavior across many events. Traces connect spans representing related work along one operation. They complement each other: a metric detects a widespread regression, a trace locates its critical path, and a log explains a specific failure decision.

Structured logs should use fields such as timestamp, service, operation, severity, outcome, request/trace ID, and safe resource context. Log levels express operational significance, not merely how many messages a developer wants. Avoid secrets, full credentials, and unbounded payloads. Protect against log injection and constrain access/retention for personal data.

A correlation ID groups related records but does not by itself capture parent/child timing. Distributed tracing propagates trace context through HTTP/RPC and message metadata. A span has a start/end, attributes, events, and relationships. Asynchronous batch consumption may use links rather than pretending every event has one simple parent.

## Metrics need meaningful aggregation

A counter accumulates events such as completed requests and can reset when a process restarts; calculate rates with reset-aware tooling. A gauge measures a current quantity such as in-flight requests or queue depth. A histogram records a distribution using buckets or another supported representation, allowing aggregated latency analysis.

Do not average percentiles from replicas. A p99 is a quantile of a population, and averaging quantiles does not reconstruct the combined population. Aggregate compatible histogram observations/buckets, then calculate the quantile. Bucket boundaries affect precision around an SLO threshold.

If 990 requests take 20 ms and ten take five seconds, the mean is about 69.8 ms. That average conceals a severe experience for a subset. Report distributions, error rate, and sample population. Tail latency can worsen with fanout: waiting for all of many dependencies increases the chance that one slow branch determines completion.

## RED and USE organize investigation

RED measures request **rate**, **errors**, and **duration** for services. USE measures resource **utilization**, **saturation**, and **errors** for resources. CPU utilization says how busy CPU is; run-queue pressure reveals waiting for CPU. A pool at its connection limit may have growing acquisition wait even if database CPU is low.

Useful dashboards connect the two: request p95/p99 and errors alongside pool wait, database locks, queue age, event-loop delay, CPU, memory, disk, and network. Label routes by templates such as `/tasks/:id`, not raw IDs, to avoid exploding metric cardinality. High-cardinality details often belong in traces/logs with controlled sampling and retention.

## Worked five-second request

```text
root request: 5000 ms
  admission/pool wait: 3900 ms
  authorization SQL:    20 ms
  main SQL:             60 ms
  provider call:        900 ms (including a retry)
  serialization/send:  120 ms
```

The database queries are not the largest contributor. Inspect why the pool was occupied: leaked clients, transactions held during external calls, or simply too much admitted work. If the provider span overlaps other work, calculate the critical path rather than adding all span durations. Missing instrumentation can make time appear as a gap; a gap is a clue, not proof of CPU work.

Compare the slow trace with a healthy trace from the same route/version and similar workload. Use logs to connect a retry decision to its error classification. Check whether the browser's five seconds include DNS, connection, download, or main-thread time not covered by the server trace.

## OpenTelemetry and sampling

OpenTelemetry defines APIs, SDKs, semantic conventions, context propagation, and collection/export concepts for telemetry. A collector can receive, process, sample, and export signals to backends. Instrumentation is not the storage/query backend itself. These roles are described in [OpenTelemetry concepts](https://opentelemetry.io/docs/concepts/).

Sampling reduces cost but changes what evidence is available. Head sampling decides early; tail sampling can retain traces based on observed outcomes but needs buffering and complete enough data. Missing a rare failure in sampled traces does not prove it never happened. Preserve unsampled aggregate metrics and critical audit events under separate appropriate policies.

## Exercises

1. **Debug:** p99 rises while mean latency barely changes. What populations and resource metrics do you inspect?
2. **Implementation:** Instrument pool acquisition and SQL separately, then intentionally hold a connection to reproduce the difference.
3. **Design:** Choose labels for request metrics without exposing user IDs or creating millions of series.
4. **Interview:** Explain why averaging per-server p99 values is invalid and how histograms help.

<details><summary>Hints</summary>

Quantiles depend on the full distribution and traffic weights. Trace wait time as well as execution. A service's root duration and a user's interaction duration are different measurement boundaries.

</details>

## Further reading and connections

[Prometheus metric types](https://prometheus.io/docs/concepts/metric_types/), [W3C Trace Context](https://www.w3.org/TR/trace-context/), and [Brendan Gregg's USE method](https://www.brendangregg.com/usemethod.html). Continue to [SLOs](slos-and-alerting.md), [request journey](../12-fullstack/the-life-of-a-request.md), and [incident lab](../21-case-studies/incident-lab.md).
