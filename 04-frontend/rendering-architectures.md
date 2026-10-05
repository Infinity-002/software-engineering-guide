# CSR, SSR, hydration, and Server Components

Relay's public landing page and private task editor have different needs. The landing page can be mostly stable and cacheable; the editor needs user-specific data and rich interaction. A rendering architecture decides where work happens, when it happens, and what must travel to the browser.

## Follow the critical path

With client-side rendering (CSR), the browser commonly downloads a shell and JavaScript, executes it, fetches data, and constructs the useful UI. This fits interactive applications and can simplify static hosting, but JavaScript and data waterfalls can delay useful content.

Server-side rendering (SSR) creates HTML for a request on the server. It can deliver useful content earlier, especially when the server is close to data. It also adds server compute, dependency latency, and caching/privacy responsibilities. Sending HTML does not automatically make every button interactive.

Static site generation (SSG) produces output ahead of requests. It trades freshness and build/update work for cheap, cacheable serving. Incremental static regeneration (ISR) describes framework mechanisms that refresh precomputed output after deployment, often by time or invalidation. Exact freshness and failure behavior are framework-specific; state them explicitly.

```text
CSR: request -> shell -> JS -> data -> useful UI
SSR: request -> server data/render -> HTML -> JS -> interactive UI
SSG: precompute -> edge HTML -> optional JS/interactivity
```

These are simplified dependencies. Preloading, streaming, cached data, and framework routing can overlap stages.

## Hydration reconciles two executions

Hydration connects client-side component behavior to server-rendered HTML. The browser's first compatible render must agree with the server output. Rendering a random number or locale-dependent date differently on each side can cause a mismatch. Accessing `window` during server execution can fail because that environment has no browser global.

The solution is to define which data is shared and which output is intentionally client-only. Pass stable initial data, use explicit locale/time-zone decisions, and defer browser-dependent behavior appropriately. Hiding all content until an effect runs avoids some mismatches but may discard the benefit of server rendering.

Partial hydration and islands architectures reduce the amount of page behavior activated on the client. Streaming sends useful parts before all dependencies finish. A slow optional panel should not necessarily block the whole page; a security decision required for the main content should not be bypassed by streaming early. Once headers or bytes are sent, error handling and status changes become constrained.

## Server Components are a separate axis

React Server Components run in a server environment and can keep data-access code out of the browser bundle. Client Components support state, events, and browser APIs. In Next.js's App Router, layouts and pages are Server Components by default, while a client boundary marks interactive code. A Client Component can still participate in server prerendering; “client” does not mean it is never rendered on the server. These boundaries are documented in [Next.js Server and Client Components](https://nextjs.org/docs/app/getting-started/server-and-client-components).

SSR asks where HTML is generated; Server Components ask where component code executes and what representation crosses the boundary. Conflating them leads to incorrect bundle and data-access assumptions. Passing a secret as a prop into client-visible output still leaks it even if it was read only on the server. Every server action or mutation entry point must authenticate, authorize, and validate independently.

## Caching becomes multi-layered

There may be a data cache, rendered-output cache, CDN cache, and client router/query cache. A mutation must invalidate the relevant representations, not merely one layer with a convenient API. Framework defaults evolve. Pin versions and write explicit freshness requirements rather than learning “all fetches are cached” as a permanent rule.

For Relay, precompute public documentation, serve authenticated workspace pages with carefully scoped server data, and keep interactive editing client-side. A high-frequency dashboard may favor client data refresh after a useful initial render. An infrequently changing marketing page may need almost no client JavaScript.

Why not SSR everything? Server rendering can put slow backend dependencies directly on navigation's critical path and increase operational cost. Why not CSR everything? It can delay content on slow devices and networks. Choose by content stability, personalization, interaction, search/discovery requirements, and measured user experience.

## Exercises

1. **Predict:** Server HTML says `10:00`, first client render says `15:30`. Identify the missing contract.
2. **Design:** Assign rendering strategies to public docs, authenticated task lists, a drawing editor, and a product catalog. State cache and freshness rules.
3. **Debug:** A mutation succeeds but client navigation shows an old title. List the caches to inspect.
4. **Interview:** Explain why a Server Component is not simply another name for SSR.

<details><summary>Hints</summary>

Time zone, locale, and input timestamp must be agreed. Cache invalidation should follow the representation graph. A server-only execution boundary can reduce shipped code while HTML generation and hydration remain separate concerns.

</details>

## Further reading and connections

[React Server Components](https://react.dev/reference/rsc/server-components), [React hydrateRoot](https://react.dev/reference/react-dom/client/hydrateRoot), and [Next.js caching guide](https://nextjs.org/docs/app/guides/caching). Connect to [browser internals](browser-internals.md), [performance](performance.md), and [cache design](../07-caching/cache-design.md).
