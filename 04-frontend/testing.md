# Testing frontend behavior

Relay's task form passes a test asserting that `setState` was called, yet users lose drafts on a failed save. The test observed an implementation detail rather than the behavior that matters. Begin with a contract: what can the user do, what do they perceive, and which state must survive failure?

## Test at the boundary where the risk lives

Unit tests fit pure transformations such as sorting, validation rules, and state reducers. Component tests exercise rendered behavior, focus, events, and state transitions. Integration tests connect components to routing, data fetching, and realistic request handling. End-to-end tests exercise a deployed or locally running stack in a real browser.

These are scopes, not a rule that every feature needs every scope. Use a small number of E2E journeys for critical integration risks and cheaper focused tests for detailed edge cases. A form's keyboard behavior needs a browser-like interaction model; a database uniqueness race needs a real database and concurrent requests, not a DOM test.

## A useful task-creation contract

1. A labeled title input and submit button are reachable by keyboard.
2. Submission preserves the draft while pending.
3. Validation errors are understandable and associated with the field.
4. A successful save shows the authoritative task exactly once.
5. A transport failure preserves the draft and permits a safe retry.
6. A late response after navigation cannot replace another workspace's state.

Tests should find controls by accessible role/name when possible, making missing semantics visible. Avoid selectors tied to CSS layout or internal component structure unless the behavior genuinely depends on them. Snapshot tests can detect broad output changes, but large snapshots are easy to approve without understanding whether behavior improved.

## Mocking chooses what reality to omit

Mocking a custom hook can make every test green while its actual request key leaks data across tenants. Intercepting at the HTTP boundary preserves more of the real client behavior while keeping tests deterministic. A real test server adds contract confidence but costs setup and isolation. Choose deliberately.

Test realistic failure shapes: non-2xx responses, malformed payloads, timeouts, out-of-order completion, empty data, and authorization loss. A fake that always resolves immediately omits pending states and races. Use controlled deferred responses so the test determines order rather than relying on random sleeps.

```text
test scenario (pseudocode)
  start search "rea"; hold response A
  start search "react"; hold response B
  resolve B with React results
  resolve A with older results
  assert visible results still belong to "react"
```

This tests the relevance invariant without asserting how it is implemented. A second test can verify that obsolete requests are aborted if resource cleanup is part of the contract.

## Avoid timing and environment traps

Wait for observable conditions, not arbitrary delays. Fake timers help timer-driven logic but can interact with microtasks and framework scheduling; advance the relevant queues intentionally. A simulated DOM does not implement all layout, browser storage, navigation, or accessibility behavior. Use a real browser for the behaviors it cannot faithfully represent.

Keep test data isolated by test/workspace. E2E tests that share one account and mutate the same list can fail based on execution order. A retrying test runner can conceal flakes; record first-attempt failures and investigate the race. Tests must not depend on production accounts or send real notifications unintentionally.

## When not to add another test

A reversible spacing adjustment rarely needs a new automated test that asserts its exact CSS. Review it visually at relevant sizes. Spend testing effort on invariants, complex state transitions, and failure boundaries. Conversely, a payment-confirmation screen deserves tests for unknown outcomes even if the component contains very little code.

## Exercises

1. **Debug:** Rewrite a test that asserts a hook was invoked into one that asserts user-visible behavior.
2. **Implementation:** Test out-of-order search responses and a failed save that preserves the draft.
3. **Design:** Allocate unit, component, integration, and E2E coverage for login, upload, and task deletion.
4. **Interview:** Which bugs can a mocked API never reveal, and how would you cover the most important ones?

<details><summary>Review criteria</summary>

Tests fail for broken behavior, survive harmless refactors, isolate data, and control concurrency explicitly. Contract drift, cookie policy, proxy behavior, and database constraints need evidence beyond component mocks.

</details>

## Further reading and connections

[Testing Library principles](https://testing-library.com/docs/guiding-principles/), [Playwright best practices](https://playwright.dev/docs/best-practices), and [React act](https://react.dev/reference/react/act). Continue to [backend testing](../05-backend/testing-and-evolution.md) and [safe delivery](../18-ci-cd/safe-delivery.md).
