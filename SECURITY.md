# Security Policy

## Supported Versions

We actively support and resolve security vulnerabilities on the following versions:

| Version | Supported          | Patch Support |
| ------- | ------------------ | ------------- |
| 1.0.x   | :white_check_mark: | Active        |
| 0.1.x   | :x:                | Deprecated    |

## Reporting a Vulnerability

If you discover a potential security vulnerability in EvalForge, please notify us immediately. **Do not open a public GitHub issue.** Instead, send a detailed report directly to the security team.

Please email your report to: **security@evalforge.ai**

In your report, please include:
- A clear description of the vulnerability and its potential impact.
- Detailed step-by-step instructions to reproduce the vulnerability (including proof-of-concept code, payloads, or screenshots).
- Information about your deployment environment (Docker Compose, Kubernetes, VM setup).

We will review your submission, reply to confirm receipt within 24 hours, and coordinate a fix and release.

## Security Practices
- **Disclosure Policy**: We follow standard coordinated vulnerability disclosure (CVD) timelines. Fixes will be published in patch releases (e.g., `1.0.1`), and security advisories will be posted on GitHub.
- **Dependency Scanning**: Dependencies are scanned weekly for known CVEs.
- **Secrets Management**: Secrets should always be loaded via environment variables; the server automatically masks secret settings from configuration dump API endpoints.
