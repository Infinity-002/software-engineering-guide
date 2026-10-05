# TypeScript and runtime boundaries

Relay receives `{ "priority": "urgent" }` from an API, but the UI expects `"low" | "high"`. An annotation cannot change the received bytes. TypeScript checks relationships in source code before execution; the resulting JavaScript still needs runtime validation at untrusted boundaries.

## Structural types express capabilities

TypeScript generally uses structural compatibility: a value can satisfy a type because it has the required shape, not because it explicitly declared that name. This helps compose libraries, but two identifiers with the same representation can be accidentally interchangeable. Carefully chosen wrapper types or validated brands can express meaningful distinctions when the domain needs them.

Interfaces describe object contracts and support declaration merging. Type aliases can name object types, unions, intersections, and other type expressions. Choose by meaning and local conventions; neither is universally “more type safe.” An intersection means both sets of requirements apply, not “choose either.” Intersecting incompatible field types can produce an impossible field.

## Model valid states

```typescript
type LoadState<T> =
  | { kind: "idle" }
  | { kind: "loading" }
  | { kind: "ready"; data: T }
  | { kind: "failed"; message: string };

function label(s: LoadState<string[]>): string {
  switch (s.kind) {
    case "idle": return "Not loaded";
    case "loading": return "Loading";
    case "ready": return `${s.data.length} tasks`;
    case "failed": return s.message;
    default: {
      const impossible: never = s;
      return impossible;
    }
  }
}
```

The discriminant narrows the union. Unlike independent `loading`, `error`, and `data` flags, this model rules out some contradictory states. It is a design choice: a stale-while-refreshing UI may intentionally need data and a loading status together, so model that state explicitly rather than forcing the wrong union.

`never` represents an impossible value in this control-flow position. `unknown` accepts arbitrary input but requires checking before use. `any` opts out of checking and can spread unsound assumptions through callers. A type assertion says “trust me”; it does not inspect or convert the value.

## Validate where bytes enter

```typescript
type Task = { id: string; title: string };

function parseTask(value: unknown): Task {
  if (typeof value !== "object" || value === null) {
    throw new Error("Expected task object");
  }
  if (!("id" in value) || typeof value.id !== "string" ||
      !("title" in value) || typeof value.title !== "string") {
    throw new Error("Invalid task shape");
  }
  return { id: value.id, title: value.title };
}
```

This focused parser establishes shape, not complete business validity. Production validation may also bound lengths, validate IDs, reject unknown fields where appropriate, and distinguish safe user errors from internal faults. Schema libraries can reduce repeated checks, but authorization still belongs after identity and resource context are known.

Avoid `const task = await response.json() as Task`. Parse an `unknown` value instead and handle non-success HTTP responses separately. Generated API types reduce drift between teams; they still do not prove that a network peer or persisted old record follows today's schema.

## Generics preserve relationships

A generic `first<T>(items: readonly T[]): T | undefined` preserves the relationship between input elements and output. Returning `unknown` would lose information; returning a caller-selected arbitrary `T` from unvalidated JSON would invent information. Good generics express a relationship the implementation can honor.

Utility types such as `Pick`, `Omit`, `Partial`, and `Readonly` transform compile-time shapes. `Partial<Task>` makes fields optional; it does not define patch semantics, distinguish deletion from omission, or validate a request. `Readonly` is generally shallow and does not freeze runtime objects.

Mapped types iterate over keys. Conditional types select a type based on a type relationship:

```typescript
type Flags<T> = { [K in keyof T]: boolean };
type ElementOf<T> = T extends readonly (infer U)[] ? U : never;
```

Conditional types involving a naked type parameter can distribute over unions. Powerful type programming is useful for libraries, but a difficult-to-read type can cost more than a small explicit domain type. Inference usually makes ordinary code clearer; annotate boundaries and places where intent would otherwise widen incorrectly.

## Failure modes and judgment

Types do not enforce authorization, sanitize HTML, validate database migrations, eliminate races, or guarantee termination. They can prevent many local mistakes while the system remains wrong globally. Strict compiler options improve feedback, but escape hatches, declaration files, and external data remain trust boundaries.

Use types to expose impossible states and preserve relationships. Use runtime validation to establish facts about values. Use database constraints and transactions to preserve shared invariants. Each layer protects a different boundary.

## Exercises

1. **Debug:** Why is `function decode<T>(text: string): T` suspicious if it only calls `JSON.parse`?
2. **Implementation:** Extend `parseTask` with a priority union and length bounds; test invalid and missing fields.
3. **Design:** Model optimistic task creation, including pending, confirmed, and failed states with a retry identity.
4. **Interview:** Explain `unknown`, `any`, and `never` using an external API response.

<details><summary>Hints</summary>

A generic supplied solely by the caller cannot establish a runtime fact. Return `unknown`, accept a validator, or use a schema-specific parser. Model optimistic identity separately from the authoritative ID if reconciliation needs both.

</details>

## Further reading and connections

[TypeScript handbook](https://www.typescriptlang.org/docs/handbook/intro.html), [narrowing](https://www.typescriptlang.org/docs/handbook/2/narrowing.html), and [type manipulation](https://www.typescriptlang.org/docs/handbook/2/types-from-types.html). Continue to [backend validation](../05-backend/server-architecture.md) and [trust boundaries](../08-security/trust-and-authorization.md).
