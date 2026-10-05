# Bytes, serialization, hashing, and time

Two services can agree on a field name and still disagree on its meaning. One sends cents, another interprets dollars. One sends local time, another assumes UTC. Representation is part of the protocol, not a cosmetic detail.

## From values to bytes

An **encoding** maps a representation into another representation. UTF-8 encodes Unicode text as bytes; Base64 encodes arbitrary bytes as printable characters. Base64 is reversible without a secret and is not encryption. A hash maps input to a fixed-size digest; it is not generally reversible, but low-entropy inputs can be guessed. Encryption protects confidentiality under a key. A signature or MAC protects authenticity/integrity under a different trust model.

Unicode code points, encoded bytes, and user-perceived characters are different units. A visible character may contain multiple code points. JavaScript string length counts UTF-16 code units. Therefore a “100-character” validation rule must specify its unit, and truncating raw UTF-8 bytes can cut a character. Normalize text only when the product's comparison rules require it; identifiers, names, and passwords have different semantics.

**Serialization** turns structured values into a transferable format such as JSON or Protocol Buffers. It must define field names, types, missing values, numeric ranges, and evolution rules. JSON has no native date or binary type. JavaScript numbers cannot exactly represent every 64-bit integer, so a database `bigint` identifier may need a decimal string on the wire. Monetary amounts should use an agreed integer minor unit or decimal representation, with currency and rounding rules; binary floating-point surprises become business bugs.

```json
{
  "eventId": "evt_018",
  "schemaVersion": 1,
  "amountMinor": "1999",
  "currency": "USD",
  "occurredAt": "2026-10-04T10:30:00Z"
}
```

This example chooses strings for integers that may cross runtime limits. A schema validator must still enforce range and meaning. An interface declaration on the receiving TypeScript side does not validate these bytes.

## Hashes solve several different problems

A hash table uses a hash to select a bucket, then compares actual keys to resolve collisions. A cryptographic content hash makes accidental collision extraordinarily unlikely and resists deliberate collision attacks under its security assumptions. A password hash deliberately spends resources to slow guessing. These are different goals: the fastest hash is usually the wrong password-storage primitive.

Distributed placement requires stable hashing across processes and versions. A language's process-randomized built-in hash may be excellent for attack resistance in a local table but unsuitable for permanent partition placement. Canonical serialization matters too: hashing JSON with different whitespace or key order can give different bytes for the same logical object. See [consistent hashing](../11-system-data-structures/consistent-hashing.md).

## Time is a measurement with assumptions

A **wall clock** answers “what date/time is it?” It can jump because of synchronization or administrative changes. A **monotonic clock** measures elapsed time without wall-clock adjustments; its reference point is usually meaningful only within a machine/runtime. Use wall time for human-visible timestamps and monotonic time for local duration and deadline calculations where available.

```typescript
const started = performance.now();
await doWork(); // application-defined asynchronous operation
const elapsedMs = performance.now() - started;
```

`Date.now()` before and after an operation can give a distorted duration if the wall clock changes. Persisting a monotonic timestamp and comparing it after reboot is also wrong unless the platform explicitly supports that meaning.

A timestamp does not prove causality. If API-1's clock is ahead, its event can appear later than an event that actually followed it. Record event IDs, versions, and causal links where ordering matters. Time zones are rules for displaying instants and interpreting local civil times; they are not fixed offsets. “Run at 09:00 every day in Kolkata” and “run every 24 hours” express different scheduling contracts in the general case.

## Failure scenarios and judgment

A webhook signature fails intermittently because the receiver parses and reserializes JSON before verifying it. Verify the exact bytes required by the signature protocol. A retention job deletes new records because timestamps arrived without units and milliseconds were treated as seconds. Make units visible in schemas. A lease holder compares its local wall clock with another machine's timestamp and overestimates remaining ownership. Clock assumptions belong in the safety argument, as [leases](../10-distributed-systems/leases-and-fencing.md) explains.

Do not invent a binary protocol merely to save a few bytes before measuring bottlenecks. JSON is inspectable and widely supported; typed binary schemas help when payload volume, CPU, or contract tooling justify the cost. Neither format automatically supplies compatibility or validation.

## Exercises

1. **Predict:** What happens when `9007199254740993` passes through a JavaScript number and then JSON?
2. **Debug:** A retry expires too early after a laptop wakes. List clock and suspend-behavior assumptions to inspect.
3. **Design:** Specify a `Money`, an event timestamp, and a daily reminder schedule without ambiguous units.
4. **Implementation:** Serialize equivalent objects with different key order and compare hashes. Design a canonicalization policy before using hashes as logical identity.
5. **Interview:** Explain why a signed value need not be secret and an encrypted value still needs integrity protection.

<details><summary>Hints</summary>

The integer exceeds the exact range of the usual JavaScript number representation. Keep it as a string or use an explicitly supported integer representation at both ends. A daily schedule needs a time zone and a policy for ambiguous or missing local times.

</details>

## Further reading

[RFC 8259: JSON](https://www.rfc-editor.org/rfc/rfc8259), [Unicode FAQ](https://www.unicode.org/faq/), and [High Resolution Time](https://www.w3.org/TR/hr-time/) provide representation and clock details. Continue to [TypeScript boundaries](../04-frontend/typescript-boundaries.md) and [logical time](../10-distributed-systems/logical-time.md).
