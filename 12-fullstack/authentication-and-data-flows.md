# Authentication and data flows

Authentication is not finished when a form says “success.” The browser must store the intended credential, later requests must carry it under browser policy, the backend must recognize it, and each resource operation must still be authorized.

## Trace a session login

```text
user -> React login form -> POST /login -> bounded backend parser
  -> account lookup -> password-hash verification
  -> session creation -> Set-Cookie response -> browser cookie jar
  -> later authenticated request -> auth middleware
  -> current resource authorization -> application logic
```

Use HTTPS. The frontend provides accessible fields and safe feedback; the server validates inputs and rate-limits abuse. Password verification uses a maintained hashing library and stored parameters. On success, create/rotate an unpredictable session identity and send a narrowly scoped cookie. Do not return the password hash or log credentials.

The browser processes `Set-Cookie` under its policy; frontend JavaScript cannot ordinarily read that response header. `HttpOnly` prevents script access to the stored cookie, not its automatic attachment to matching requests. `Secure` restricts transport, and SameSite controls cross-site attachment under its rules. Domain/path scope and expiry must be deliberate.

## Cross-origin deployment adds browser policy

If the UI and API use different origins, the request may need `credentials: "include"` and the server must allow the exact permitted origin with credential support. The server must also correctly handle any preflight. Cookie SameSite and browser third-party-cookie policies can independently prevent attachment; a successful CORS response does not override all cookie restrictions.

```typescript
const response = await fetch("https://api.relay.example/tasks", {
  credentials: "include",
  headers: { Accept: "application/json" }
});
if (!response.ok) throw new Error(`Request failed: ${response.status}`);
const data: unknown = await response.json();
// Validate data before using it as an application type.
```

This is a transport example, not a complete error/UI implementation. A first-party same-origin proxy can simplify browser policy, but the proxy still needs secure forwarding and backend authorization. CORS is neither login nor CSRF protection; revisit [browser security](../08-security/browser-and-input-security.md).

## Cookies versus bearer headers

Cookies can be attached automatically, which improves session ergonomics and creates CSRF considerations. An explicitly attached bearer header is less exposed to classic ambient-cookie CSRF, but the application must safely obtain/store the token and protect it against script theft. An HttpOnly-cookie backend-for-frontend can keep provider tokens server-side at the cost of another session/service boundary.

Choose based on client type, origin topology, revocation, and threat model. A mobile API client and a browser application have different storage and transport capabilities. “JWT versus cookies” is not a meaningful comparison because one is a token format and the other a browser mechanism.

## Expiration, refresh, and logout

An expired session should produce a clear authentication response, preserve safe unsaved work where possible, and avoid infinite retry loops. If using refresh tokens, coordinate concurrent refresh attempts so one tab/request does not overwrite a newer credential with stale state. Handle rotation/reuse detection according to the identity provider's protocol.

Logout revokes server-side authority where supported, clears the browser credential with matching scope, and clears private client caches. Other tabs need a policy for learning the change. Revoked roles should not remain trusted merely because a UI cache still says “admin.” Reauthentication and authorization refresh are separate decisions.

## Trace a data fetch

```text
React/query key -> fetch -> HTTP -> API -> service -> SQL
  -> rows -> safe JSON -> HTTP response -> validated client data
  -> query cache -> subscribed component render
```

The service owns business meaning; SQL owns authoritative persisted facts; the client cache owns a temporary representation. A list response from a replica may lag a successful mutation. Decide whether to return the updated entity, read from the leader, wait for a replication position, or show an explicit pending state. Blindly retrying a read does not guarantee a freshness bound.

## Exercises

1. **Debug:** Login returns `200`, but the next request is unauthenticated. Inspect cookie storage, scope, SameSite, credentials mode, and origin policy separately.
2. **Predict:** Logout clears the current tab's state but not a stolen access token. What guarantee was actually achieved?
3. **Implementation:** Build a login/logout flow and verify it with real browser network/storage tools, including an expired session.
4. **Design:** Preserve an unsaved task draft across session expiry without leaking it after another user logs in.
5. **Interview:** Explain why fetching data and obtaining permission to fetch it are different contracts.

<details><summary>Hints</summary>

Check actual request cookies, not just React state. Partition retained drafts by identity and workspace, define cleanup, and reauthorize before submission. A successful HTTP response can fail to establish a usable session because browser policy rejects storage or attachment.

</details>

## Further reading and connections

[MDN cookies](https://developer.mozilla.org/en-US/docs/Web/HTTP/Cookies), [Fetch credentials](https://developer.mozilla.org/en-US/docs/Web/API/Request/credentials), and [OWASP session management](https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html). Connect to [JWT/OAuth](../08-security/sessions-jwt-oauth.md), [server state](../04-frontend/state-and-data-fetching.md), and [request tracing](the-life-of-a-request.md).
