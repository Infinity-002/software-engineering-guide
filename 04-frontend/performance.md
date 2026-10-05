# Measuring and improving frontend performance

Performance is how quickly a person receives useful content and responsive feedback under real device and network conditions. A small bundle can still render a slow page; a fast API can still sit behind a chain of unnecessary requests. Begin with a user journey and a measured bottleneck.

## User-visible measurements

Core Web Vitals currently include Largest Contentful Paint (LCP), Interaction to Next Paint (INP), and Cumulative Layout Shift (CLS). LCP reflects when the largest eligible visible content is painted, INP captures interaction responsiveness, and CLS measures unexpected visual movement. The published good thresholds are LCP at most 2.5 seconds, INP at most 200 ms, and CLS at most 0.1, assessed at the 75th percentile with the documented population rules. These metrics and thresholds are defined by [Web Vitals](https://web.dev/articles/vitals), not by an individual application's average benchmark.

Field measurements capture real users; lab runs provide controlled reproducibility. Segment by route, device, connection, geography, and release. Avoid putting raw user identifiers into metric labels. A desktop lab improvement can conceal a mobile regression if aggregate traffic changes.

## Read the waterfall as dependencies

Relay's task page loads HTML, then JavaScript, then workspace data, then tasks, then avatar images. Some dependencies are necessary; others exist only because fetching is nested in component effects. Identify the longest path to useful output. Start independent work earlier, combine requests when it removes expensive round trips, and avoid sending fields the UI never uses.

Preload tells the browser a resource is important for the current navigation; incorrect preloads compete with genuinely critical work. Prefetch speculates about future work and may waste bandwidth or violate user expectations on constrained connections. Lazy loading delays optional work, but lazy-loading the main visible image can worsen LCP.

## JavaScript and images consume different budgets

Bundle size costs transfer, parsing, compilation, and execution. Compression reduces transfer but does not remove runtime work. Tree shaking removes statically provable unused code when module and side-effect information permit it. Code splitting moves code off the initial path; too many tiny chunks can create overhead and waterfalls.

Images often dominate bytes. Use appropriate dimensions, responsive sources, efficient formats supported by the target environment, and explicit width/height or aspect ratio to reserve layout space. A CDN can transform and cache variants, but unbounded size parameters can create cost and cache-cardinality problems. Content-hashed assets support long freshness without difficult replacement races.

## Rendering and interaction diagnosis

Record a trace while typing, filtering, and navigating. Long JavaScript tasks can delay input even when React's actual DOM commit is small. Large lists can create expensive style/layout/paint work. Virtualization reduces rendered items but needs careful focus, scrolling, and accessibility behavior. Pagination may be simpler when the product permits it.

Memoization helps when repeated calculation or component work is material and inputs are stable. It cannot fix a slow network waterfall, and unstable object/function identities can defeat it. Moving state closer to the component that needs it may remove unnecessary work more cleanly than memoizing an entire tree.

## A concrete improvement loop

Suppose mobile task-list LCP is 4.1 seconds. Break it down: 0.4 seconds connection/server wait, 1.2 seconds script transfer, 1.1 seconds parse/execute, 0.8 seconds delayed data fetch, then rendering. An extra database index affecting 20 ms cannot solve this. Split the editor bundle, start list data earlier, and render a useful initial shell/data view. Compare the same cohort after release, including errors and INP, so the fix does not trade one problem for another.

Set performance budgets that reflect journeys: initial JavaScript, image bytes, maximum interaction work, and backend contribution. Budgets are guardrails, not proof of user satisfaction. Regression checks should use repeatable conditions and tolerate expected variance rather than failing on noise.

## Exercises

1. **Debug:** LCP is good but typing freezes. Which trace evidence distinguishes script, layout, and network causes?
2. **Design:** Choose what to preload, prefetch, and lazy-load on a task page with an optional rich-text editor.
3. **Implementation:** Capture a baseline waterfall and CPU trace, make one change, and report the causal evidence for improvement.
4. **Interview:** Why can a 40% smaller compressed bundle have little effect on INP?

<details><summary>Review criteria</summary>

The proposal names a bottleneck and user metric, preserves a comparable population, and checks side effects. Transfer bytes and interaction-time CPU are different budgets. Avoid optimizing a resource absent from the critical path.

</details>

## Further reading and connections

[Chrome DevTools performance](https://developer.chrome.com/docs/devtools/performance), [MDN resource hints](https://developer.mozilla.org/en-US/docs/Web/HTML/Attributes/rel/preload), and [React Profiler](https://react.dev/reference/react/Profiler). Connect to [browser mechanics](browser-internals.md), [rendering architectures](rendering-architectures.md), and [percentiles](../14-observability/logs-metrics-traces.md).
