# JavaScript execution and memory

JavaScript can keep many network requests in flight because waiting for the network does not require executing JavaScript continuously. Understanding this is more useful than memorizing that JavaScript is “single-threaded.” A browser has many subsystems and may run workers; one JavaScript agent ordinarily executes one job at a time.

## Scope, bindings, and functions

An execution context tracks the state needed to run code. Lexical scope resolves variable names according to where code was written. A closure retains access to its lexical environment after the outer function returns. It captures bindings, not necessarily frozen copies of their values.

```javascript
function makeCounter() {
  let n = 0;
  return () => ++n;
}
const a = makeCounter();
const b = makeCounter();
console.log(a(), a(), b()); // 1, 2, 1
```

Each call creates a separate environment. Closures are useful for encapsulation and callbacks; they can also retain large object graphs unexpectedly.

“Hoisting” describes observable declaration behavior, not literal movement of source lines. A `var` binding is initialized to `undefined` before its assignment runs. `let` and `const` bindings exist but cannot be accessed before initialization, the temporal dead zone. Function declarations have their own initialization rules. `const` prevents rebinding; it does not deeply freeze an object.

For ordinary functions, `this` generally depends on the call form. `obj.method()` supplies `obj`; extracting the method and calling it independently loses that association unless it is bound. Arrow functions capture the surrounding `this` instead of creating one. Do not explain `this` as “the object where the function was defined.”

## Objects, prototypes, classes, and modules

Property lookup checks the object, then follows its prototype chain until it finds a property or reaches the end. A class organizes constructor and prototype behavior; it does not replace JavaScript's object model. Own properties and inherited properties differ, which matters when iterating untrusted objects. Prototype pollution is a security problem when attacker-controlled keys modify shared object behavior.

ES modules define explicit imports/exports, module scope, and dependency relationships. Imports are live bindings, not copied snapshots. Module evaluation and cycles can create initialization surprises. Tree shaking works best when tools can reason about static dependencies and side effects; exporting code does not guarantee unused code can always be removed.

## Stack, tasks, and microtasks

The call stack holds active function calls. Run-to-completion means a job normally finishes before another job runs on the same agent. Timers, input, and other host activities schedule tasks. Promise reactions and `queueMicrotask` schedule microtasks. The browser drains microtasks at specified checkpoints, commonly after a task, before proceeding to another task. Rendering opportunities are coordinated by the browser and are not guaranteed after every callback.

```javascript
console.log("A");
setTimeout(() => console.log("B"), 0);
Promise.resolve().then(() => console.log("C"));
queueMicrotask(() => console.log("D"));
console.log("E");
// In this ordinary browser script: A E C D B
```

The timer's zero delay means “eligible after the delay and scheduling rules,” not “run immediately.” Microtasks created while draining the microtask queue can extend that drain; an infinite chain can starve input and rendering. Node has additional scheduling details, so do not copy browser ordering claims onto every Node API.

## Promises are completion values

A promise represents eventual fulfillment or rejection. Constructing a promise runs its executor synchronously. `await` suspends the async function's continuation while the surrounding agent can do other work; it does not block the entire browser thread waiting for the result.

```javascript
async function example() {
  console.log("inside");
  await Promise.resolve();
  console.log("continued");
}
example();
console.log("outside");
// inside, outside, continued
```

`Promise.all` coordinates already-started work but does not cancel remaining operations when one rejects. Use explicit cancellation mechanisms where supported. `try/catch` catches a rejection when you `await` it inside the `try`; an unobserved promise started elsewhere will not magically throw into that stack frame.

## Predict bindings rather than memorizing puzzles

Consider a loop that schedules callbacks:

```javascript
for (var i = 0; i < 3; i++) {
  setTimeout(() => console.log(i), 0);
}
// 3, 3, 3 after the current job completes
```

All three closures refer to the same function/global `var` binding, which has reached 3 when the timers run. Replacing `var` with `let` creates the loop's per-iteration bindings, so the callbacks observe 0, 1, and 2. Nothing about timer speed changed; the binding model changed. This same reasoning explains a callback retaining one React render's state snapshot.

```javascript
console.log(before); // undefined
var before = 7;

// In a separate script/function:
// console.log(later); // ReferenceError: binding not initialized
let later = 7;
```

The `var` declaration establishes an initialized binding before its assignment. The lexical declaration does not permit access before initialization. An undeclared name is a different error from a declared but uninitialized lexical binding, even though both can produce a ReferenceError.

For `this`, inspect the call:

```javascript
"use strict";
const user = {
  name: "Mira",
  readName() { return this.name; }
};
console.log(user.readName()); // Mira
const detached = user.readName;
// detached(); // TypeError here: this is undefined in this strict call
const bound = user.readName.bind(user);
console.log(bound()); // Mira
```

An arrow assigned as a method would retain its surrounding `this`; the object's literal syntax would not bind it automatically. Use an arrow for callbacks when lexical receiver behavior is intended, and ordinary methods when call-site receiver behavior is part of the interface.

Prototype lookup is equally concrete:

```javascript
const defaults = { theme: "light" };
const preferences = Object.create(defaults);
console.log(preferences.theme); // inherited: light
preferences.theme = "dark";    // own property shadows inherited value
console.log(defaults.theme);    // light
delete preferences.theme;
console.log(preferences.theme); // inherited again: light
```

Deleting an own property can reveal an inherited one. When processing untrusted dictionaries, distinguish own properties from inherited values and use appropriate data structures/validation. A class method usually resides on the prototype, whereas instance fields belong to each instance; that difference affects sharing and memory, not merely syntax.

## Errors cross asynchronous boundaries explicitly

```javascript
async function fails() { throw new Error("boom"); }

async function caller() {
  try {
    await fails();
  } catch (error) {
    console.log(error.message); // boom
  }
}
```

Calling `fails()` without awaiting or attaching a rejection handler inside that `try` would return a rejected promise instead of throwing synchronously into the caller's stack. Give background tasks an explicit owner that observes failure. Do not use an empty catch merely to silence an unhandled rejection: define recovery, safe user feedback, and telemetry. The general rule is that every started asynchronous operation needs a completion, cancellation, or intentional detached-work policy.

## Memory and failure scenarios

Garbage collection reclaims unreachable objects. A listener retained on a long-lived object can keep its callback and captured data reachable. Clean up subscriptions when their ownership ends. Detached DOM nodes may remain alive through references. A memory profile should identify retaining paths, not merely allocation counts.

A search UI can show old results when request A starts first, request B starts second, and A finishes last. The event loop executed every callback correctly; the application failed to define which response is still relevant. Cancel obsolete requests where possible and also guard against stale completion. [State ownership](state-and-data-fetching.md) develops this example.

Why not solve every slow task with promises? Promises schedule continuations; they do not parallelize CPU computation. Break work into bounded chunks, use a worker, or move it to a service according to the workload. Each choice adds communication and lifecycle costs.

## Exercises

1. **Predict:** Add a second `.then()` after the first promise callback above. Place it relative to `D`, and explain why.
2. **Debug:** A `setInterval` callback sees an old React state value. Explain the closure before proposing a framework fix.
3. **Implementation:** Create a deliberately retained listener, remove it, and inspect heap snapshots for retained objects.
4. **Interview:** Explain why `await` inside `forEach` does not make `forEach` wait for all callbacks.

<details><summary>Hints</summary>

The second reaction becomes runnable only after the preceding promise settles, so already-queued microtasks can precede it. `forEach` ignores returned promises; choose sequential `for...of` with `await` or explicitly bounded concurrent work. React render functions create new lexical environments.

</details>

## Further reading

[ECMAScript specification](https://tc39.es/ecma262/), [HTML event loops](https://html.spec.whatwg.org/multipage/webappapis.html#event-loops), and [MDN closures](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Closures). Connect to [concurrency](../01-foundations/concurrency-and-io.md) and [React](react-mental-model.md).
