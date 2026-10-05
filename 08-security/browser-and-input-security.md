# Browser security and hostile input

Relay can authenticate a user correctly and still execute an attacker's instruction. The attacker may control a task title, URL, SQL parameter, HTML fragment, or another website the user visits. Security depends on the interpreter and trust boundary that receives that value.

## CORS and CSRF solve different problems

The same-origin policy restricts how one origin can read/interact with another's resources. CORS lets a server authorize selected cross-origin browser access through response headers. For some requests, the browser first sends an `OPTIONS` preflight describing the proposed method and headers. A successful preflight is permission under browser policy, not application authentication.

Some cross-origin requests can be sent without preflight. Therefore “CORS blocks the response” does not mean the server never received the request. Non-browser clients are not constrained by browser CORS enforcement. Never use CORS as the only protection for a mutation.

CSRF exploits automatically attached credentials, commonly cookies, to cause a victim's browser to make an unwanted authenticated request. Use appropriate SameSite cookie policy, anti-CSRF tokens and/or strict origin verification under the application's threat model, and safe HTTP method discipline. Same-site and same-origin differ; a hostile sibling subdomain can matter. Credentialed cross-origin CORS requires explicit allowed origins rather than wildcard origin permission.

## XSS crosses the script-execution boundary

Cross-site scripting occurs when untrusted content becomes executable script in the application's origin. Output encoding must match context: HTML text, attributes, URLs, JavaScript, and CSS have different rules. React escapes ordinary text interpolation, but raw HTML insertion, unsafe URL handling, third-party scripts, and DOM APIs can still create XSS.

If rich text is required, use a maintained sanitizer with a deliberately small allowed vocabulary. Sanitizing once does not protect later transformations that reintroduce unsafe markup. A Content Security Policy can restrict script sources/execution and reduce impact, but is defense in depth, not a substitute for correct output handling. Prefer nonce/hash-based policies where appropriate rather than broadly allowing inline script.

Storing long-lived bearer credentials in localStorage exposes them to same-origin script reads, including XSS. An HttpOnly cookie reduces direct token theft, but XSS can still perform authenticated actions and read accessible data. Token placement changes attack paths; it does not cure XSS.

## Injection depends on the interpreter

SQL injection turns data into SQL syntax. Use bound parameters for values and allowlisted identifiers. Command injection turns data into shell syntax. Prefer direct executable/argument APIs, avoid shells, and validate allowed operations. Escaping rules differ across shells and platforms, making ad hoc string concatenation fragile.

SSRF makes the server fetch an attacker-chosen destination. A “fetch this image URL” feature can reach internal services or cloud metadata. Restrict schemes and destinations, handle redirects deliberately, validate resolved addresses, account for DNS rebinding, and use network egress controls. A string check for `localhost` is insufficient because addresses have many representations and names can resolve differently over time.

```text
user URL -> parser -> destination policy -> DNS/address checks
  -> constrained outbound network -> bounded response processing
```

Even an allowed host can return a huge or compressed response that exhausts memory. Bound time, bytes, redirects, and decompressed size. Authorization to fetch is not permission to process unlimited data.

## Headers and framing

Use HTTPS with a suitable HSTS rollout policy, `X-Content-Type-Options: nosniff`, and framing restrictions such as CSP `frame-ancestors` to reduce clickjacking. A restrictive Referrer-Policy can reduce leakage of URL details. Headers must fit deployment needs; blindly copying a policy can break legitimate embedding or resource loading.

Clickjacking tricks users into interacting with a hidden or misleading embedded UI. Framing controls address that presentation boundary. Cookies need deliberate domain/path scope, but path is not a strong isolation boundary against hostile same-origin script. Separate security-sensitive applications by origin when isolation is required.

## Exercises

1. **Predict:** A malicious page submits a form to a cookie-authenticated endpoint, but cannot read the response. Can state still change?
2. **Debug:** A backend allows any CORS origin reflected from the request and enables credentials. Explain the trust error.
3. **Design:** Threat-model a URL-preview feature through redirects, DNS, response size, and parsing.
4. **Implementation:** Build tests for malicious text, unauthorized origins, missing CSRF proof, and cross-tenant IDs in a local test environment.
5. **Interview:** Explain why TLS, CORS, CSP, and authorization are not interchangeable protections.

<details><summary>Hints</summary>

A response-read restriction does not undo a mutation. Reflecting arbitrary origins grants an attacker's site browser access under the configured credential behavior. The URL-preview server has network privileges the browser may not have, so it needs its own destination and resource policy.

</details>

## Further reading and connections

[OWASP CSRF prevention](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html), [XSS prevention](https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html), [SSRF prevention](https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html), and [Fetch standard](https://fetch.spec.whatwg.org/). Connect to [browser storage](../04-frontend/browser-internals.md), [authentication flow](../12-fullstack/authentication-and-data-flows.md), and [uploads](../12-fullstack/realtime-and-uploads.md).
