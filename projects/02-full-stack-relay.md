# Project 2 — Full-stack Relay

Extend Project 1 with a React/TypeScript application, authenticated navigation, PostgreSQL-backed task data, and selected caching. The objective is to preserve user intent and security across the browser/server boundary, including stale data and failures.

## User journeys

Implement login/logout, workspace selection, task search/filter/sort, paginated list, detail/edit, and create/delete flows. Use semantic controls, visible keyboard focus, labeled inputs, and clear loading/empty/error/success states. Filters that should survive sharing/back navigation belong in the URL. Draft edits belong to the form; authoritative task data belongs to a server-state cache.

Validate external API data at runtime. A generated TypeScript client is useful but does not remove this boundary. Session handling should be verified in a real browser: inspect Set-Cookie, cookie scope, credentials mode, expiry, and logout cleanup.

## Architecture evolution

Start with direct API reads and establish correctness. Then add a query cache with keys including workspace, filters, ordering, and representation identity. Add Redis only for a measured repeated-read path such as a workspace summary. Keep permission-sensitive decisions authoritative and document a freshness budget for cached summaries.

Implement optimistic task completion with operation-specific reconciliation. A failed old mutation must not erase a newer successful edit. Show pending state separately from confirmed state, and return the server's authoritative version on success. Handle a 409/version conflict with a meaningful reload/merge choice.

## Milestones

1. Build accessible static forms/layout and test narrow screens, long titles, keyboard navigation, and zoom.
2. Connect login and one task read; verify origin/cookie policy through browser tools.
3. Add query ownership, routing, and form drafts without duplicated derived state.
4. Add concurrent mutations, relevance guards, and safe optimistic behavior.
5. Add selected caching, measure performance, and explain which work it avoids.

Profile one navigation and one typing interaction. Record network waterfall, main-thread work, and React commit evidence. Make one causal improvement, such as removing a request waterfall or splitting an optional editor bundle, and compare equivalent conditions.

## Required failure experiments

Delay search responses so the older query finishes last. Fail a save after the user has made another edit. Expire the session with an unsaved draft. Switch workspaces while a request is in flight. Remove membership while private data is cached. Disable Redis and verify bounded origin fallback. Reload on a slow network and observe whether useful content and accessible feedback remain understandable.

## Acceptance criteria

- [ ] Keyboard-only users can complete every core journey with visible focus and understandable errors.
- [ ] Query keys isolate users/workspaces and logout clears private cached state.
- [ ] Out-of-order responses cannot replace the current query's result.
- [ ] Failed saves preserve drafts and do not roll back unrelated successful work.
- [ ] Runtime parsing rejects malformed API data without crashing the entire application.
- [ ] Component tests assert behavior; a small E2E suite covers login, save, and permission failure.
- [ ] Performance evidence identifies the bottleneck and effect of one measured change.
- [ ] Redis freshness, invalidation, outage, and stale-fill behavior are documented and tested.

## Exercises and review

Trace one save from click to pixels using [the request journey](../12-fullstack/the-life-of-a-request.md). Explain why local UI state, URL state, form state, and server state have different owners. Compare CSR and server rendering for the private editor and public documentation, including hydration and caching costs.

<details><summary>Hints after implementation</summary>

Do not use effects to mirror values that can be derived during render. Abort obsolete requests where useful, but also associate results with their initiating identity. A same-origin deployment can simplify cookies/CORS, while server authorization remains mandatory.

</details>

## Further reading and connections

[Frontend curriculum](../04-frontend/README.md), [authentication flow](../12-fullstack/authentication-and-data-flows.md), [cache design](../07-caching/cache-design.md), and [React testing](../04-frontend/testing.md). Consult [TanStack Query docs](https://tanstack.com/query/latest/docs/framework/react/overview) for the selected library's current API and defaults.
