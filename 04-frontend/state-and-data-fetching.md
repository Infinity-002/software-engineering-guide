# State ownership and server-state caches

Relay has a selected tab, a task list, an unsaved title, and a logged-in workspace. Putting all four into one global store hides that they have different owners and lifetimes. State management starts by identifying authority.

## Classify before choosing a library

| State | Authority and lifetime | Typical home |
|---|---|---|
| Local UI state | This interaction or component | Local state/reducer |
| Global client state | Shared client preference/workflow | Context or a client store |
| Server state | Remote service; local copy can become stale | Query cache |
| URL state | Shareable navigation/history | Route and search parameters |
| Form state | Uncommitted user edits and validation | Form-local state/library |

The server task title and a draft title are different values. Refreshing server data should not silently erase an unsaved draft. A filter in the URL supports bookmarks and back/forward navigation; duplicating it in a global store creates a synchronization problem. Decide what is canonical and derive the other views.

Context distributes dependencies. Redux uses explicit actions and reducers to make state transitions inspectable; it can be useful for complex shared workflows. Zustand provides a smaller external-store model with selective subscriptions. TanStack Query and similar tools manage remote-data lifecycles: fetching, freshness, retries, deduplication, and invalidation. These tools solve overlapping but different problems; a global store is not a cache-coherence strategy by itself.

## A query key is a data identity

The key for tasks might include `workspaceId`, filter, and sort. Omitting workspace identity can show one tenant's cached tasks in another workspace. Include all inputs that change the representation, while avoiding unstable object identities or irrelevant values that prevent reuse. On logout or identity changes, clear or isolate private cached data.

Freshness and retention are separate. A value can be stale but still worth displaying while refreshing; an unused value may remain cached for quick navigation. A background refresh should not necessarily replace the whole page with a spinner. Model first load, refresh, empty result, error with stale data, and permission loss as distinct experiences.

## Request races are a relevance problem

The user types “rea,” then “react.” The first query is slow and finishes after the second. Accepting whichever response arrives last shows the wrong results. Abort obsolete requests where supported, and ensure a response updates only the query identity that initiated it. Abort is a resource optimization and a relevance aid; it does not guarantee a server-side mutation was undone.

Dependent requests can form a waterfall: fetch user, then workspace, then tasks. If the workspace is already in the route, tasks need not wait for the user fetch merely because the component tree is nested. Parallelize independent requests, move fetching to the correct ownership level, or design an aggregation endpoint when network latency dominates.

## Optimistic updates are a small distributed protocol

When a user completes a task, the UI may predict success immediately. It should retain enough information to reconcile with the authoritative response. A naive rollback restores an entire old task list if one update fails. That can erase a later successful edit from another operation.

Prefer operation-specific patches or version-aware reconciliation. Assign a stable mutation identity, cancel or account for conflicting refreshes, record the pending operation, and apply the server's authoritative version on completion. If two optimistic changes overlap, their completion order may differ from submission order. This is why “save old state and restore on error” is only safe under limited concurrency assumptions.

Invalidation says cached knowledge is no longer fresh; it does not itself prove that every dependent view has been refetched successfully. Updating the detail cache while forgetting the list count produces inconsistent UI. Centralize related key conventions and state which views can lag. Authorization failures should remove or restrict sensitive stale data rather than treating it like an ordinary transient network failure.

## Why not make everything global?

Global state broadens who can modify and depend on a value. That makes ownership less clear and can increase rendering and testing complexity. Keep ephemeral input local unless there is a concrete sharing requirement. Conversely, copying the same server entity into many local states makes updates hard to reconcile. Choose the smallest scope that matches the authority and lifetime.

## Exercises

1. **Design:** Classify theme, task title, draft title, page number, access token, and “modal open.” Explain ambiguous cases.
2. **Predict:** Two optimistic edits fail/succeed in reverse order. Show why whole-snapshot rollback can lose a successful change.
3. **Implementation:** Build search with delayed out-of-order responses. Prove that an obsolete response never replaces the current query's result.
4. **Interview:** A UI shows stale account information after Redis was added. Separate browser query-cache, HTTP-cache, application-cache, and replica-lag hypotheses.

<details><summary>Review criteria</summary>

Each value has one explicit authority; cache keys include identity and representation dimensions; mutations have a concurrency policy; loading and stale-error states preserve useful context without retaining unauthorized data.

</details>

## Further reading and connections

[Redux essentials](https://redux.js.org/tutorials/essentials/part-1-overview-concepts), [Zustand introduction](https://zustand.docs.pmnd.rs/learn/getting-started/introduction), and [TanStack Query overview](https://tanstack.com/query/latest/docs/framework/react/overview). Connect to [cache consistency](../07-caching/cache-design.md), [optimistic locking](../20-production-patterns/data-lifecycle-and-tenancy.md), and [authentication flows](../12-fullstack/authentication-and-data-flows.md).
