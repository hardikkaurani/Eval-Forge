# Contributing to EvalForge

Thank you for your interest in contributing to EvalForge! We want to make contributing to this project a rewarding experience. As an open-source platform, we rely on community contributions to expand evaluation metrics, improve performance, and enhance developer tools.

---

## 🗺️ Git Branching Strategy
- **`main`**: The stable branch. Contains releases and verified production-grade code.
- **`develop`**: The integration branch. All feature branches (`feat/`) and bug fixes (`fix/`) should target `develop` for testing before merging into `main`.

---

## 🛠️ Local Development Setup

### 1. Prerequisites
- Docker & Docker Compose
- Python 3.12+ (for local backend development)
- Node.js 18+ & npm (for local frontend development)

### 2. Launch Stack via Docker Compose
To spin up all services (FastAPI, React UI, PostgreSQL, Redis, Celery Workers) in development mode:
```bash
docker compose -f docker-compose.yml up --build
```
The API will be available at `http://localhost:8000` and the web console at `http://localhost:5173`.

### 3. Backend Development
To run the backend locally outside of Docker:
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Or `.venv\Scripts\activate` on Windows
pip install -r requirements.txt
python -m pytest
```

---

## 🎨 Coding & Style Guidelines

To keep the repository clean and maintainable, we enforce the following development tools.

### Python Backend
We use **Ruff** for linting, import sorting, and code formatting.
- Format and organize imports:
  ```bash
  ruff format app
  ruff check app --fix
  ```
- Run static checks:
  ```bash
  ruff check app
  ```

### TypeScript Frontend
We use **ESLint** for code analysis and **Prettier** for formatting.
- Format code:
  ```bash
  npm run format
  ```
- Run lint checks:
  ```bash
  npm run lint
  ```

---

## 💬 Commit Message Convention

We follow the [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) specification:
- `feat`: A new feature (e.g., `feat(engine): add DeepSeek judge provider`)
- `fix`: A bug fix (e.g., `fix(auth): resolve JWT token expiration buffer`)
- `docs`: Documentation changes (e.g., `docs(readme): add installation details`)
- `style`: Changes that do not affect the meaning of the code (formatting)
- `refactor`: A code change that neither fixes a bug nor adds a feature
- `test`: Adding missing tests or correcting existing tests
- `chore`: Maintenance tasks, dependencies updates, version bumps

---

## 🤝 The Pull Request Process

1. **Fork** the repository and create your branch from `develop`.
2. Keep your PRs focused. Do not mix unrelated refactoring with feature development.
3. Make sure to write unit/integration tests for any new metrics, routes, or services.
4. Verify all linting, formatting, and unit tests pass locally before pushing.
5. Create a Pull Request (PR) describing your changes using the Pull Request Template.
6. A maintainer will review your code. Address feedback promptly. Once approved and all CI checks pass, your changes will be merged!
