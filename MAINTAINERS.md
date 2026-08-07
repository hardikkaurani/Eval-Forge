# EvalForge Project Maintainers

This document lists the core maintainers, triage leads, and security contacts for the **EvalForge** repository.

---

## 👑 Lead Maintainers & Steering Committee

| Name / GitHub Handle | Role | Primary Focus Area | Location |
|---|---|---|---|
| [@hardikkaurani](https://github.com/hardikkaurani) | Lead Architect & Project Creator | Core Gateway, LLM Engine, System Design | India |

---

## 🛠️ Domain Maintainers

| Name / GitHub Handle | Focus Area | Responsibility |
|---|---|---|
| **Backend & Engine Lead** | `backend/app/evaluation/` | LLM Judge Engine, G-Eval, Provider Drivers |
| **Frontend & UI Lead** | `frontend/src/` | React 18 SPA, WebSockets, Tailwind Styling |
| **Infra & DevOps Lead** | `docker/`, `.github/` | Docker Compose, Nginx, CI/CD Workflows |
| **Security Lead** | `app/core/security.py` | API Key Hashing, RBAC, Vulnerability Triage |

---

## 🛡️ Security Response Team

For confidential security disclosures, contact:
- **Email:** `security@evalforge.dev`
- **Private Advisory:** [GitHub Security Advisories](https://github.com/hardikkaurani/Eval-Forge/security/advisories/new)

---

## 📋 Triage & Code Review Guidelines

Maintainers follow these operational rules:
- Respond to incoming issues and PRs within **24–48 hours**.
- Ensure all CI workflow checks pass before merging PRs.
- Always use **Squash and Merge** to maintain a clean linear `main` branch history.
- Tag issues appropriately using the [.github/labels.yml](.github/labels.yml) taxonomy.
