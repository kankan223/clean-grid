# CONTRIBUTING — CleanGrid (Team Collaboration Mode)

**Team Collaboration Mode:** Two-developer workflow enforced. No direct commits to `main`. Follow these guardrails strictly.

## Quick Acknowledgement
- This repository is now in "Team Collaboration Mode".
- Do NOT write or push application code directly to `main`.
- **Reminder (mandatory):** Run `git pull origin main --rebase` before creating a new branch or pushing changes.

---

## 1. Required Git Workflow (Strict)

### Step 1: Update your local main first
```sh
git checkout main
git pull origin main --rebase
```

### Step 2: Create feature/fix branches from a clean main
**Branch naming examples:**
- `feature/security-hardening`
- `fix/frontend-map-ui`
- `chore/docs/update-ci`

```sh
git checkout -b feature/<short-descriptor>
```

### Step 3: Work locally, commit often with descriptive messages
**Commit message format:** `TYPE(scope): short description`

**Types:** `feat`, `fix`, `chore`, `docs`, `refactor`, `test`, `perf`

**Examples:**
```sh
git add .
git commit -m "feat(auth): add refresh token rotation"
git commit -m "fix(map): dynamic import to avoid SSR hydration"
git commit -m "chore(docs): update CONTRIBUTING guide"
```

### Step 4: Before push — rebase with remote main
```sh
git fetch origin
git rebase origin/main
```

- **If rebase succeeds:**
  ```sh
  git push origin feature/<branch-name>
  ```

- **If conflicts arise:** Follow Section 3 (Merge Conflict Protocol) below.

### Step 5: Create a Pull Request (PR) targeting `main`
- **PR checklist:**
  - ✅ Tests passing
  - ✅ Linting passing (eslint, ruff, mypy)
  - ✅ At least one reviewer approval
  - ✅ Clear PR description (purpose, changes, test steps)

- **Merge strategy:** "Squash and merge" or "Rebase and merge" (no fast-forward).

---

## 2. Pull Before Push — Critical Reminder

**Always run this before creating a branch or pushing changes:**

```sh
git pull origin main --rebase
```

This ensures you're always working on the latest version and minimizes merge conflicts.

---

## 3. Merge Conflict Protocol

If a conflict happens during `merge` or `rebase`:

### Step 1: Abort immediately
**For rebase:**
```sh
git rebase --abort
```

**For merge:**
```sh
git merge --abort
```

### Step 2: Inspect conflicting files carefully
- Review both versions in the conflict markers (`<<<<<<<`, `=======`, `>>>>>>>`).
- Prioritize architectural rules from [`docs/tech-stake.md`](docs/tech-stake.md) (anti-hallucination guardrails).
- Favor explicit, testable changes over implicit behavior.

### Step 3: Resolve manually
- Edit conflicting files to combine or choose the correct version.
- Test locally to ensure resolution is correct.

### Step 4: Re-run tests and linters locally
```sh
# Backend
cd backend
python -m pytest tests/

# Frontend
cd ../frontend
npm run lint
npm run build
```

### Step 5: Rebase again onto latest `main` and push
```sh
git fetch origin
git rebase origin/main
git push origin feature/<branch-name> --force-with-lease
```

---

## 4. Pull Request & Review Rules

Every PR must include:
- **Purpose summary:** What problem does this solve?
- **Files changed explanation:** What did you modify and why?
- **Manual test steps:** How can reviewers verify this works?
- **Screenshots/logs (if applicable):** For UI/UX or complex logic changes.

**Approval requirements:**
- At least one approval required before merge.
- Do not merge your own PR unless emergency and second dev approves.
- Resolve all conversations before merging.

---

## 4.1 Remote Branch Debug/Security Patch Workflow

This workflow is for reviewing a teammate's feature branch and applying debug/security patches before merge.

### Step 1: Configure Git for cross-OS line endings (per clone)

**Windows (recommended for this repo):**
```sh
git config --local core.autocrlf false
git config --local core.eol lf
git config --local core.safecrlf warn
```

**Linux/macOS:**
```sh
git config --local core.autocrlf false
git config --local core.eol lf
git config --local core.safecrlf warn
```

Optional verification:
```sh
git config --local --get-regexp "core.autocrlf|core.eol|core.safecrlf"
```

### Step 2: Safely fetch and check out their remote branch
```sh
git fetch origin --prune
git branch -r
git checkout -b fix/<module>-patch-<initials> origin/<remote-feature-branch>
```

### Step 3: Commit debug/security patches with naming convention
Use commit format: `fix(module): short description`

```sh
git add -A
git commit -m "fix(<module>): <debug-or-security-patch-description>"
```

Examples:
```sh
git commit -m "fix(auth): validate refresh token expiry on rotation"
git commit -m "fix(reports): sanitize uploaded filename before storage"
```

### Step 4: Pull latest main and handle merge conflicts
```sh
git fetch origin
git checkout main
git pull --ff-only origin main
git checkout fix/<module>-patch-<initials>
git merge origin/main
```

If conflicts occur:
```sh
git status
# Resolve conflict markers in files, then:
git add <resolved-files>
git commit -m "fix(<module>): resolve merge conflicts with main"
```

### Step 5: Push the patched branch back to remote
```sh
git push -u origin fix/<module>-patch-<initials>
```

If the team wants updates pushed directly to the original remote feature branch:
```sh
git push origin HEAD:<remote-feature-branch>
```

---

## 5. Local Environment & Safe Commands

### Use the unified startup script (recommended)
This automatically initializes both `backend/venv` and `ai-service/venv` and installs dependencies:

```sh
chmod +x start-dev.sh
./start-dev.sh
```

### Backend Manual Setup
```sh
cd backend
source venv/bin/activate
python -m pip install -r requirements.txt
PYTHONPATH=. alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

**Main entrypoint:** [`backend/app/main.py`](backend/app/main.py)

### AI Service Manual Setup
```sh
cd ai-service
source venv/bin/activate
python -m pip install -r requirements.txt
uvicorn app.main:app --reload --port 8001
```

**Main entrypoint:** [`ai-service/app/main.py`](ai-service/app/main.py)

### Frontend Setup
```sh
cd frontend
npm install
npm run dev
```

---

## 6. Debugging Missing-Dependency Errors

If you see `ModuleNotFoundError` (e.g., `fastapi`, `torch`, `pydantic`):

1. **Run the startup script:**
   ```sh
   ./start-dev.sh
   ```
   This installs both backend and ai-service dependencies automatically.

2. **Check logs:**
   - Backend install log: `logs/backend-install.log`
   - Frontend log: `logs/frontend.log`
   - Runtime logs: `logs/backend.log`, `logs/ai-service.log`

3. **Confirm venv activation and pip install success:**
   ```sh
   # Verify backend venv
   ls -la backend/venv/bin/python
   
   # Verify ai-service venv
   ls -la ai-service/venv/bin/python
   ```

4. **Reinstall if needed:**
   ```sh
   cd backend && source venv/bin/activate && pip install -r requirements.txt --force-reinstall
   cd ../ai-service && source venv/bin/activate && pip install -r requirements.txt --force-reinstall
   ```

---

## 7. Merge & Release Policy

- **`main` must always be deployable.** Do not merge breaking changes.
- All merges require passing CI (unit tests, linters).
- Use feature flags for risky changes in production.
- Tag releases with semantic versioning: `v1.0.0`, `v1.1.0-beta`, etc.

---

## 8. Code Style & Testing

### Backend (FastAPI + Python)
- **Style:** `ruff` for linting, `mypy` for type checking
- **Testing:** `pytest` for unit tests
- **Format:** Autoformat with `black` if configured

**Run locally:**
```sh
cd backend
source venv/bin/activate
ruff check .
mypy app/
pytest tests/
```

### Frontend (Next.js + TypeScript)
- **Style:** `eslint`, `prettier` for formatting
- **Type checking:** TypeScript strict mode
- **Testing:** Jest for unit tests (optional)

**Run locally:**
```sh
cd frontend
npm run lint
npm run type-check
npm run build
```

---

## 9. Key Documentation & References

**Before starting any work, read these:**

| File | Purpose |
|------|---------|
| [`docs/tech-stake.md`](docs/tech-stake.md) | Architecture guardrails & anti-hallucination rules |
| [`implementation-roadmap.md`](implementation-roadmap.md) | Feature phases (current: Phase 2/3) |
| [`project-brain.md`](project-brain.md) | Active working memory & context |
| [`frontend-structure.md`](frontend-structure.md) | Frontend component hierarchy & SSR patterns |
| [`start-dev.sh`](start-dev.sh) | Automated dev environment setup |

---

## 10. New Developer Task Priorities

Based on "Security Hardening" and "Frontend Bug Fixes" mandates:

### **Security Tasks:**

**Task 1: Rate Limiting + Abuse Prevention**
- Implement Redis-backed sliding window counters per IP.
- Enforce: 10 reports/IP/hour, 100 requests/IP/minute on critical endpoints.
- Reference: [`docs/tech-stake.md`](docs/tech-stake.md) (slowapi pattern mentioned).
- **Branch:** `feature/rate-limiting`
- **Files to modify:**
  - `backend/app/main.py` (add middleware)
  - `backend/requirements.txt` (add `slowapi`)

**Task 2: Auth & Route Protection Hardening**
- Implement JWT refresh token rotation.
- Add server-side role checks for admin routes.
- **Branch:** `feature/jwt-refresh-rotation`
- **Files to modify:**
  - `backend/app/routers/admin.py`
  - `backend/app/core/auth.py`
  - Unit tests for JWT refresh flow

**Task 3: CORS Configuration (Production Safety)**
- Whitelist only Vercel domain in production.
- Keep localhost/`*` for development.
- **Branch:** `fix/cors-production-origin`
- **Files to modify:**
  - `backend/app/main.py` (CORS settings)

### **Frontend Tasks:**

**Task 4: Map UI/Hydration Fixes**
- Audit Leaflet usage and confirm dynamic import pattern with `ssr: false`.
- Fix any Next.js hydration warnings.
- Ensure map initializes without client-only errors.
- **Branch:** `fix/frontend-map-hydration`
- **Files to modify:**
  - `frontend/src/components/Map.tsx` (or similar)
  - Confirm pattern aligns with [`frontend-structure.md`](frontend-structure.md)

**Task 5: Frontend UX Polish**
- Improve empty/error/loading states on report and admin pages.
- Add loading skeletons and toast error flow for FormData submissions.
- Implement fetch retry behavior.
- **Branch:** `fix/frontend-ux-polish`
- **Files to modify:**
  - `frontend/src/app/(map)/page.tsx`
  - `frontend/src/app/admin/page.tsx`
  - Loading & error components

---

## 11. Emergency Contact & Escalation

If you encounter:
- **Blocked on a bug:** Create an issue on GitHub and tag the other developer.
- **Merge conflict you can't resolve:** Stop, abort, and ask in Slack/Discord before forcing.
- **Main is broken:** Revert the offending commit immediately and create a hotfix.

---

**Last updated:** April 19, 2026  
**Maintained by:** Ken + New Developer (Team Collaboration Mode)

