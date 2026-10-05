# Checkpoint: Security and trust boundaries

Attempt without notes. Explain mechanisms and draw histories before opening the rubric.

## Scenario

A valid JWT lets a user edit another workspace, a malicious website triggers a cookie-authenticated mutation, and a URL-preview endpoint reaches an internal address.

## Questions

1. Separate decoding, cryptographic verification, contextual claim validation, and resource authorization.
2. Draw trust boundaries and identify who supplied every tenant/resource/role value.
3. Explain CORS versus CSRF, HttpOnly limitations, XSS defenses, and safe cookie scope.
4. Threat-model SSRF across redirects, DNS changes, response size, and network egress.
5. Specify password hashing, secret rotation, and least-privilege service identities.

## Evidence to produce

Write negative integration tests for cross-tenant access, invalid token context, CSRF protection, and constrained URL fetching.

Score each answer: 0 = names only; 1 = correct happy path; 2 = failure mechanism and repair; 3 = assumptions, trade-offs, and validation. Pass when every question reaches 2 and the evidence is reproducible. Revisit weak chapters before advancing.

<details><summary>Review rubric after attempting</summary>

Authentication is not authorization, CORS is not a mutation guard, and signatures do not establish current permissions. The answer avoids homemade cryptography and treats frontend input as untrusted.

</details>

[Section reading order](README.md) · [Progress](../PROGRESS.md) · [Project briefs](../projects/README.md)
