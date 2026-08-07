# Security Policy & Vulnerability Management

At **EvalForge**, security is a top priority. As an open-source evaluation platform processing sensitive enterprise prompts, model outputs, and API credentials, we are committed to upholding strict security practices and maintaining transparency.

---

## Supported Versions

We release security patches for the following versions of EvalForge:

| Version | Supported | Security Patch Status |
|---|---|---|
| 1.0.x (Current `main`) | ✅ Yes | Actively supported with high-priority patches |
| 0.9.x | ⚠️ Critical Only | Critical security fixes only |
| < 0.9.0 | ❌ No | Deprecated — Please upgrade to v1.0+ |

---

## Reporting a Vulnerability

**Please do NOT report security vulnerabilities through public GitHub issues.**

If you discover a security vulnerability, credential leak, authentication flaw, or remote code execution vector in EvalForge, please report it privately:

1. **GitHub Private Advisory:** Submit a private vulnerability report via [GitHub Security Advisories](https://github.com/hardikkaurani/Eval-Forge/security/advisories/new).
2. **Security Team Email:** Contact our security response team directly at `security@evalforge.dev`.

### What to Include in Your Report
To help us triage and resolve the issue quickly, please include:
- A description of the vulnerability and potential security impact.
- Step-by-step reproduction instructions or proof-of-concept (PoC) exploit script.
- Affected components (e.g., FastAPI route, JWT authentication middleware, Celery worker, dependencies).
- Any suggested mitigations or patches.

---

## Response SLAs & Triage Timeline

Our security team adheres to the following response timeline:

- **Initial Acknowledgment:** Within **24 hours** of submission.
- **Triage & Severity Assessment:** Within **48 hours**.
- **Patch Resolution & Private Advisory:** Within **7 to 14 days** (depending on severity).
- **Public Disclosure / CVE Assignment:** Coordinated disclosure after fix release.

---

## Security Hardening Best Practices

EvalForge incorporates built-in security features:
- **API Key Hashing:** API keys are stored in PostgreSQL using salted SHA-256 hashes (`app/core/security.py`).
- **Secret Masking:** Logger filters automatically mask API tokens (`sk-****`) in logs and response bodies.
- **Security Headers:** Strict Transport Security (HSTS), Content Security Policy (CSP), and `X-Frame-Options` middleware.
- **Rate Limiting:** Sliding-window rate limiting on all public API endpoints.
- **Air-Gapped Operation:** Zero outbound telemetry or forced cloud dependencies.

---

## Security Bounty & Recognition

We deeply appreciate security researchers who responsibly report vulnerabilities. Valid security disclosures are recognized in our **Security Wall of Fame** and release notes.
