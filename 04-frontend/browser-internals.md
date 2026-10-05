# How browsers turn documents into pixels

An API can respond in 20 ms while the page remains unusable for two seconds. The remaining work happens in the browser: parsing, executing, styling, laying out, painting, compositing, and responding to input. “The backend is fast” is therefore not a complete performance diagnosis.

## Processes and responsibility

Modern browsers separate responsibilities across processes and threads, often including browser coordination, networking, renderer processes, and GPU work. Exact placement depends on browser and isolation policy. A renderer executes page code and builds its presentation. Separate processes improve fault and security isolation, but do not make expensive main-thread work harmless.

The HTML parser incrementally creates the DOM. CSS parsing creates style rules represented through the CSSOM. Scripts can read or modify the document and may affect parsing progress. Resource discovery and loading overlap, so a request waterfall is a dependency graph rather than a simple sequential list.

```text
HTML bytes -> parse -> DOM ---------
                                  +-> style -> layout -> paint -> composite
CSS bytes  -> parse -> CSS rules ---
JS executes -----------------------> mutations can invalidate earlier work
```

The conceptual render tree includes visual objects and styling; it is not a literal copy of every DOM node. Hidden elements and generated content demonstrate why DOM structure and rendered structure differ. Layout computes geometry. Paint produces drawing work. Compositing combines layers into the final image, sometimes allowing updates without repainting all content. Implementations optimize heavily; avoid assuming every style change runs every stage.

## Reflow, repaint, and layout thrashing

“Reflow” commonly refers to layout work after geometry changes. “Repaint” refers to drawing changes. Moving an element with a transform may be composited efficiently in some circumstances, but layer promotion is not free and is not guaranteed for every element or effect.

```javascript
// Potential repeated read/write interleaving:
for (const box of boxes) {
  box.style.width = container.offsetWidth + "px";
}
```

If writes invalidate geometry relevant to subsequent reads, the browser may need to synchronously resolve layout. Read a shared measurement once, then batch writes. Measure in a performance trace before declaring a forced-layout problem; not every property read forces fresh layout every time.

`requestAnimationFrame` schedules work around rendering opportunities; it does not give an unlimited CPU budget. At 60 Hz a whole frame interval is about 16.7 ms, shared with browser work and other scripts. Long tasks delay input handlers and visual feedback. Offscreen work, huge DOM trees, and expensive selectors can amplify cost, but the trace should determine the bottleneck.

## Browser storage has several contracts

| Mechanism | Scope/purpose | Engineering consequence |
|---|---|---|
| Cookies | Scoped HTTP state with domain/path and other attributes | Can be attached automatically; security attributes matter |
| localStorage | Synchronous origin-scoped string storage | Can block and is readable by same-origin script |
| sessionStorage | Origin and page-session storage | Useful for tab/session UI state, not durable authority |
| IndexedDB | Asynchronous structured local database | Supports offline data with transactional access and schema upgrades |
| HTTP cache | Stored response representations | Controlled by freshness, validators, and cache keys |
| Service worker | Programmable request/event interception | Enables offline behavior but creates update/invalidation complexity |

Storage quotas and eviction policies vary. The browser can remove local data; a local copy is not automatically a backup. An origin combines scheme, host, and port. A “site” used in cookie policy is a different concept, so same-site does not imply same-origin. This distinction matters for [CORS and CSRF](../08-security/browser-and-input-security.md).

## Service workers introduce another deployment lifecycle

A service worker can intercept controlled-page fetches and respond from a Cache API store or the network. It has installation, activation, and update behavior separate from ordinary page navigation. An old worker can continue serving an old shell while a new backend expects a different client contract. Version assets, design update behavior, and avoid caching authenticated data under public keys.

Why not put every response in a service-worker cache? It can preserve stale permissions, sensitive content, or incompatible HTML/JavaScript combinations. Offline mutation also requires a conflict and retry policy. A queued local “delete” cannot be assumed valid days later after membership changes.

## Exercises

1. **Predict:** A DOM update changes text but not geometry. Which rendering stages might still run? Why is a universal answer unsafe?
2. **Debug:** A page has low network latency but delayed typing. Find evidence in a performance trace rather than the network panel alone.
3. **Implementation:** Build a large list, measure rendering, then virtualize or paginate it. Compare responsiveness and accessibility behavior.
4. **Design:** Specify offline task edits with reconnect conflict handling and logout cleanup.
5. **Interview:** Explain HTML-to-pixels and where JavaScript can interrupt progress.

<details><summary>Hints</summary>

Text can change glyph painting and sometimes layout. A trace distinguishes script, layout, and paint costs. Offline edits need base versions, authorization on sync, conflict handling, and an explicit policy for locally retained private data.

</details>

## Further reading and connections

[Chrome rendering performance](https://web.dev/articles/rendering-performance), [MDN IndexedDB](https://developer.mozilla.org/en-US/docs/Web/API/IndexedDB_API), and [Service Worker specification](https://w3c.github.io/ServiceWorker/) provide mechanisms. Connect to [frontend performance](performance.md), [React commits](react-mental-model.md), and [request tracing](../12-fullstack/the-life-of-a-request.md).
