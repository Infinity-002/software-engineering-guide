# Sessions, JWT verification, OAuth, and OIDC

After login, Relay needs to recognize later requests without asking for a password every time. There are several ways to carry identity evidence. The right question is not “Which token format is modern?” but “Who can issue, validate, revoke, and use this credential?”

## Sessions and cookies

An opaque session ID refers to server-side session state. Generate it with a cryptographically secure random source, rotate it at authentication/privilege changes as appropriate, and expire/revoke it under policy. The browser can store it in a cookie marked `Secure`, `HttpOnly`, and an appropriate `SameSite` mode with narrow scope. `HttpOnly` prevents direct JavaScript reads, but injected same-origin script can still act through the browser.

Sessions centralize revocation and mutable authorization context, at the cost of a lookup and session-store availability. A cookie is a transport/storage mechanism; a session is an identity lifecycle. A JWT can also be put in a cookie, and an opaque token can be sent as a bearer header. Do not confuse these axes.

## Decode, verify, and trust are different steps

A typical signed JWT contains encoded header and claims plus a signature/MAC. Decoding Base64url makes the claims readable without checking integrity. Verification checks the cryptographic result using an allowed algorithm and trusted key. Trusting the claims additionally requires correct issuer, audience, token purpose, validity window, and application authorization policy.

```text
token bytes -> bounded parse -> allowed algorithm/key selection
  -> signature verification -> issuer/audience/time/purpose checks
  -> principal mapping -> resource authorization
```

Do not let an untrusted header freely choose arbitrary algorithms or remote key URLs. Key rotation requires a trusted key-discovery configuration and safe caching behavior. A token valid for service A may be invalid for service B. An ID token is not automatically an access token. Signed JWT content is usually visible; signing does not encrypt claims.

Expiration limits credential lifetime but creates a clock-tolerance decision. Small allowed clock skew should be deliberate, not an excuse for indefinitely valid tokens. Revocation before expiry needs state or another mechanism. A stolen bearer token grants its holder the token's usable authority until defenses stop it; the format does not prevent theft.

## OAuth delegates access; OIDC adds identity

OAuth 2.0 coordinates a client obtaining authorization to access a resource server. OpenID Connect adds an identity layer, including ID tokens and authentication semantics. Using an arbitrary OAuth access token as proof of login without the appropriate protocol checks invites confusion about who issued it and for whom.

An authorization-code flow with PKCE proceeds conceptually as follows:

1. The client creates a high-entropy verifier and derives a challenge.
2. It starts an authorization request with the challenge, intended redirect URI, scopes, and transaction-binding protections.
3. The authorization server authenticates the user and obtains the applicable authorization decision.
4. The client receives a short-lived code at the registered redirect endpoint.
5. The token endpoint checks the code, client/redirect binding, and PKCE verifier before issuing tokens.
6. The client validates the appropriate returned identity evidence and uses access tokens only for their intended resource.

PKCE binds redemption to the initiating client's secret verifier, mitigating intercepted-code use. It does not make arbitrary redirect URIs safe or replace all transaction/issuer checks. Use exact redirect validation and a maintained protocol library. `state` binds the response to the initiating transaction; OIDC `nonce` binds identity responses under that protocol's rules. Current security guidance deprecates insecure flow choices and is recorded in [RFC 9700](https://www.rfc-editor.org/rfc/rfc9700.html).

## Refresh, logout, and unknown state

Refresh tokens extend access without repeated interactive login. They are high-value credentials. Rotation and reuse detection can expose theft, but concurrent legitimate refreshes need a defined race policy. Do not let every failed API request independently launch refresh and overwrite credentials in arbitrary order.

Logout should invalidate server-side session/refresh authority and clear client state. A previously issued self-contained access token may remain valid until expiry unless a revocation mechanism is consulted. Browser cache and query cache cleanup matter too. “We deleted the token from this tab” is a local action, not global revocation.

Why not JWT everywhere? Opaque sessions can be simpler for a first-party web application needing immediate revocation. JWTs can help independently validating services under a clear issuer/audience/key model, but introduce claim freshness, key rotation, and token-size concerns. Choose from trust and lifecycle requirements.

## Exercises

1. **Debug:** A backend decodes a JWT and checks `role === 'admin'`. Name every missing trust step.
2. **Predict:** Logout revokes a refresh token but access tokens last 20 minutes. What can a thief still do under that design?
3. **Design:** Specify session expiry, renewal, logout, role revocation, and concurrent-tab behavior for Relay.
4. **Interview:** Explain OAuth, OIDC, PKCE, session cookies, and bearer tokens as different responsibilities.

<details><summary>Hints</summary>

Verification includes trusted algorithm/key selection and contextual claim checks before authorization. PKCE protects code redemption, not all browser attacks. An access-token revocation promise requires a mechanism beyond deleting local storage.

</details>

## Further reading and connections

[RFC 8725: JWT best practices](https://www.rfc-editor.org/rfc/rfc8725), [OpenID Connect Core](https://openid.net/specs/openid-connect-core-1_0.html), and [OWASP session management](https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html). Continue to [full-stack login](../12-fullstack/authentication-and-data-flows.md) and [CSRF/CORS](browser-and-input-security.md).
