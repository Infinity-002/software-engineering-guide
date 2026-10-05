# Trust boundaries and authorization

Relay receives `workspaceId=7` and `role=admin` from a browser. Those values describe what a caller wants the server to believe; they do not establish authority. Ask at every boundary: **Who supplied this value, and why do we trust it?**

## Authentication identifies; authorization permits

Authentication establishes a principal under a mechanism such as a session or verified token. Authorization decides whether that principal may perform this operation on this resource in this context. A logged-in user is not automatically entitled to every object whose ID they can guess.

```text
untrusted request
  -> validate identity evidence
  -> load relevant resource/tenant context
  -> evaluate permission
  -> perform bounded operation
```

UI hiding is not authorization. A user can call the endpoint directly, modify JavaScript, or change request fields. Enforce checks on the server for every sensitive read and mutation. Scope queries by tenant and verify resource relationships; an opaque UUID reduces easy enumeration but is not a permission check.

RBAC assigns permissions through roles such as workspace editor. ABAC evaluates attributes such as resource owner, organization, time, or classification. Roles simplify common policy; attributes express context but can make policy harder to audit. Centralize reusable decisions while keeping resource-specific facts explicit. Deny by default when the policy lacks enough trustworthy context.

## Trust is directional and limited

A reverse proxy may be trusted to set the caller IP only if direct access is restricted and forwarded-header handling is configured. An internal service is not automatically trusted for every tenant merely because it is inside a VPC. An authenticated webhook identifies its sender under the signature protocol but still carries data that needs schema and business validation.

Apply least privilege to people, services, and infrastructure identities. The API's database user rarely needs schema-administration permissions. A worker that reads attachment objects need not delete backups. Prefer short-lived workload credentials where supported and rotate/revoke secrets with an operational procedure.

## Password storage resists offline guessing

Passwords have low entropy compared with random cryptographic keys. Store a salted password hash using a maintained password-hashing implementation such as Argon2id with parameters selected from current guidance and measured service capacity. A unique salt prevents identical passwords from sharing the same stored hash and defeats precomputed tables; it is not a secret. A pepper, if used, is a separate secret with its own rotation and recovery complexity.

Fast general-purpose hashes such as SHA-256 are inappropriate alone for password storage because an attacker can test guesses quickly. Encryption is also the wrong basic storage model when the server does not need to recover the password. Rate-limit online attempts, support secure reset flows, and avoid revealing whether a particular account exists through obvious response differences.

Do not manually compare cryptographic signatures or design password-hash formats. Libraries need correct configuration and upgrade handling. A password-hash upgrade can occur after successful login when the plaintext is temporarily available; never log it.

## Secrets and API keys have lifecycles

Keep secrets out of source control, client bundles, URLs, crash dumps, and routine logs. A secret manager provides controlled distribution and audit, but applications can still leak fetched values. Scope API keys, store verifier material appropriately, display raw keys only as needed, and support overlapping rotation windows. If a key leaks, removing it from the latest Git commit does not revoke it or erase history.

Audit security-relevant actions with principal, resource, action, result, and trustworthy time/context. Avoid storing raw secrets or unnecessary personal data in the audit trail. Protect audit access and retention; an attacker able to rewrite every record can erase accountability.

## Failure scenarios and alternatives

A membership is revoked, but an hour-lived token still says `admin`. The token's signature can be valid while its authorization claim is stale. Decide whether sensitive operations require current membership lookup, short lifetime, revocation/version checks, or another policy. Caching permissions creates a freshness contract with security consequences.

Why not trust all internal traffic? Compromised services, configuration errors, and cross-tenant bugs occur inside networks. Authenticate service identity, authorize its scope, and segment access according to the threat model. Encryption and network isolation help different boundaries; neither replaces application authorization.

## Exercises

1. **Design:** Draw trust boundaries for a browser, CDN, API, PostgreSQL, worker, and object store. Label every credential and its scope.
2. **Debug:** An authenticated user edits another tenant's task by changing an ID. Identify the missing invariant and a test that exposes it.
3. **Predict:** A role is removed while a cached token claim remains valid. What does cryptographic verification prove and what does it not prove?
4. **Interview:** Explain salt, pepper, password hashing, encryption, and signing without treating them as interchangeable.

<details><summary>Hints</summary>

Authorization must bind principal, tenant, resource, and action. A signature establishes integrity under a trusted key and context; it does not establish that every claim remains current or grants this operation.

</details>

## Further reading and connections

[OWASP authorization](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html), [password storage](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html), and [secrets management](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html). Continue to [identity protocols](sessions-jwt-oauth.md), [browser attacks](browser-and-input-security.md), and [multi-tenancy](../20-production-patterns/data-lifecycle-and-tenancy.md).
