# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-06-27

### Added
- Monorepo folder setup separating `frontend`, `backend`, `docs`, `examples`, `datasets`, `docker`, `scripts`, `tests`, and `.github` templates.
- FastAPI project shell with async database sessions (SQLAlchemy), CORS configuration, and structured logging setup.
- React, TypeScript, and Vite frontend workspace with customized vanilla styling, developer status monitor page, and ESLint/Prettier code quality integrations.
- GitHub Action CI workflows for automated linting, checking formatting, and builds on commits and pull requests.
- Configuration for dockerized deployments using `docker-compose.yml` supporting `postgres` and `redis` health checks.
- Professional markdown templates for issue reporting, security, pull requests, roadmap, and contributing standards.
