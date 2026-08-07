# First Contributor Guide — EvalForge

Welcome to your first contribution to **EvalForge**! This guide is tailored to help you get your first Pull Request merged smoothly in under 10 minutes.

---

## ⚡ Quick 3-Step Setup

1. **Fork and Clone the Repository:**
   ```bash
   git clone https://github.com/YOUR_USERNAME/Eval-Forge.git
   cd Eval-Forge
   ```

2. **Run the Automatic Developer Setup Script:**
   ```bash
   # macOS / Linux
   chmod +x scripts/setup-dev-env.sh
   ./scripts/setup-dev-env.sh

   # Windows (PowerShell)
   .\scripts\setup-dev-env.ps1
   ```

3. **Pick a "Good First Issue":**
   Browse our curated issues tagged [`good first issue`](https://github.com/hardikkaurani/Eval-Forge/issues?q=is%3Aissue+is%3Aopen+label%3A"good+first+issue") or check [`docs/CONTRIBUTOR_ISSUES_CATALOG.md`](../docs/CONTRIBUTOR_ISSUES_CATALOG.md).

---

## 🛠️ Making Changes & Testing

Create a new topic branch:
```bash
git checkout -b fix/my-first-contribution
```

After writing your code, verify all static checks locally:

```bash
# Test backend
cd backend
pytest

# Test frontend
cd ../frontend
npm run typecheck
npm run lint
npx prettier --check "src/**/*.{ts,tsx,css,json,md}"
```

---

## 📩 Submitting Your First PR

Commit your changes using [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/):
```bash
git add .
git commit -m "fix(ui): resolve status badge contrast ratio on dark background"
git push origin fix/my-first-contribution
```

Open a Pull Request on GitHub. A maintainer will review your PR within 24 hours and welcome you to the contributor hall of fame! 🏆
