# Contributing to EvalForge

Thank you for your interest in contributing to EvalForge! We want to make contributing to this project as easy and transparent as possible.

## 🛠️ Development Standards

To maintain code quality and style alignment across all contributions, we enforce strict linting and formatting rules.

### Python Backend Standards
We use **Ruff** for linting and import sorting, and **Black** for code formatting.

- Run formatting before committing:
  ```bash
  black backend/app
  ```
- Run linting:
  ```bash
  ruff check backend/app
  ```

### TypeScript Frontend Standards
We use **ESLint** for code quality linting and **Prettier** for formatting.

- Format code:
  ```bash
  npm run format
  ```
- Run lint checks:
  ```bash
  npm run lint
  ```

---

## 🤝 Contribution Process

1. **Fork** the repository and create your branch from `main` or `dev`.
2. Ensure your branch name follows our conventions:
   - `feat/feature-name` for new features
   - `fix/bug-name` for bug fixes
   - `docs/documentation-update` for documentation changes
3. Make your changes in a clean, isolated commit structure.
4. Verify all tests and lints pass locally.
5. Create a Pull Request (PR) detailing your modifications using our [PR Template](.github/pull_request_template.md).

---

## 📜 Code of Conduct

By participating, you are expected to uphold our [Code of Conduct](./CODE_OF_CONDUCT.md). Please report any unacceptable behavior to the project maintainers.
