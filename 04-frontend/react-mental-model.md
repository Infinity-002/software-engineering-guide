# React as a state-to-UI system

Relay's task card has a title, completion checkbox, and pending-save indicator. Manually updating each DOM node after every event creates synchronization problems: one branch forgets the indicator, another changes the title but not its accessible name. React lets you describe the UI for a state and reconcile changes over time. The hard part becomes designing state and ownership correctly.

## Render is a calculation; commit changes the host UI

A component is a function of props, state, and subscribed context that returns a UI description. Rendering calls component code. Committing applies selected changes to the DOM. A render can happen without a DOM change, and work can be interrupted or discarded. Therefore render code must not charge a card, mutate shared objects, or create unmanaged subscriptions.

Updates to state can schedule rendering; rendering a parent ordinarily causes its children to be considered again; context changes can update consumers. A prop does not independently “emit” a render event: new props arrive through the parent render path. Memoization can skip work in eligible cases, but correctness must not depend on a memoization cache.

State belongs to a component's identity in the tree. Reconciliation compares descriptions and matches identity by type, position, and keys. A stable key says which item this is among siblings. An array index becomes the wrong identity when items reorder, causing local input state to follow positions. A new random key every render remounts components and discards state.

> The virtual DOM is not inherently faster than direct DOM operations. It is an abstraction for describing updates; performance depends on work avoided, work introduced, and the workload.

## State is a snapshot

```tsx
function Counter() {
  const [count, setCount] = useState(0);
  return <button onClick={() => {
    setCount(c => c + 1);
    setCount(c => c + 1);
  }}>{count}</button>;
}
```

Assume `useState` is imported from React. Each updater computes from the queued prior state, so one click adds two. Calling `setCount(count + 1)` twice uses the same render snapshot twice and commonly results in one increment. React batches compatible updates to avoid unnecessary intermediate commits; batching is not a promise that every asynchronous update in every context behaves identically.

Do not mutate a state object in place and expect React to discover every change. Produce a new representation of changed state. Keep derived data derived: compute a filtered task list from tasks and a filter rather than storing three independently synchronized copies.

## Hooks express persistent relationships

Hooks associate state and other behavior with a component's render position. Call them at the top level of components or custom hooks according to React's rules; conditional hook calls disturb that association. A custom hook shares logic, not automatically a single shared state instance.

Refs hold mutable values across renders without scheduling a render when changed. Use them for DOM handles or nonvisual bookkeeping, not as hidden replacements for state that determines output. A controlled input gets its value from state and reports edits through an event handler; an uncontrolled input retains its value in the DOM. Controlled forms make validation and conditional UI explicit, while large forms may benefit from carefully managed subscriptions and uncontrolled primitives.

## Effects synchronize external systems

An effect is appropriate when the committed UI should synchronize with something outside React, such as a subscription or browser API. Dependencies describe reactive values used by that synchronization. Cleanup stops the previous synchronization before replacement or unmount. Development Strict Mode can deliberately exercise setup/cleanup to expose mistakes. React documents this contract in [Synchronizing with Effects](https://react.dev/learn/synchronizing-with-effects).

```tsx
useEffect(() => {
  const connection = connectToRoom(roomId); // application API
  connection.open();
  return () => connection.close();
}, [roomId]);
```

The effect belongs to the selected room's lifecycle. Sending a chat message belongs to the explicit user event, so put that mutation in an event handler. Computing `fullName` from two props belongs in render, not an effect that sets another state variable. Suppressing dependency warnings often conceals a stale-closure bug; change the ownership/design instead.

Fetching in an effect needs cancellation or stale-result handling, loading/error states, deduplication, and caching. A server-state library or framework loader can centralize these requirements. It does not remove the need to choose cache keys and authorization boundaries.

## Context, errors, Suspense, and performance

Context passes values to descendants without threading every prop. Changing a provider value can update consumers; an object recreated every render can create unnecessary work. Context is useful for cohesive dependencies such as theme or session context, but it is not automatically an efficient database for all rapidly changing application data.

Error boundaries isolate supported descendant rendering failures and show recovery UI. They do not catch every asynchronous callback or event-handler exception. Handle request failures in the request state model. Suspense describes a fallback while supported resources are pending; arbitrary `fetch()` calls do not become Suspense-enabled simply because they appear below a boundary. Place boundaries according to useful user-visible progress.

`memo`, `useMemo`, and `useCallback` can avoid work or preserve references when measured costs justify them. They add dependency and comparison complexity. Profile commits and expensive calculations before memoizing every expression. An architectural fix, such as moving rapidly changing state closer to its consumer, can outperform scattered memoization.

## Exercises

1. **Predict:** A list uses array-index keys and the first item is deleted. What can happen to an edited input in the second item?
2. **Debug:** An effect runs a payment request whenever `cart` changes. Explain why this is the wrong trigger.
3. **Implementation:** Build a task filter without effect-derived state. Add an external subscription and prove cleanup on room change.
4. **Interview:** Name render triggers, distinguish render from commit, and explain why a render might leave the DOM unchanged.

<details><summary>Hints</summary>

Identity can move to a different logical item. A payment needs explicit intent and an idempotency identity, independent of effect scheduling. Test subscription counts under remount and parameter changes, not just the initial happy path.

</details>

## Further reading and connections

[React: state as a snapshot](https://react.dev/learn/state-as-a-snapshot), [preserving and resetting state](https://react.dev/learn/preserving-and-resetting-state), and [render and commit](https://react.dev/learn/render-and-commit). Continue to [state ownership](state-and-data-fetching.md) and [browser rendering](browser-internals.md).
