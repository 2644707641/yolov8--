# Repository Guidelines

## Project Structure & Module Organization
- `backend/` hosts the FastAPI service.
- API routes are in `backend/app/api/`, business logic in `backend/app/services/`, and shared config/logging in `backend/app/core/`.
- `frontend/` is a Vue 3 + Vite app.
- Views live in `frontend/src/views/`, reusable UI in `frontend/src/components/`, layouts in `frontend/src/layouts/`, stores in `frontend/src/stores/`, and router config in `frontend/src/router/`.
- Backend tests use `backend/test_*.py`; frontend tests use `frontend/src/**/__tests__/*.spec.js`.
- Generated runtime directories (`logs/`, `runs/`, `uploads/`, `results/`, `runtime/`) are artifacts, not source.

## Build, Test, and Development Commands
- One-click local startup (Windows): `运行项目.bat` (starts backend on `8000` and frontend on `5173` when available).
- Frontend:
  - `cd frontend && pnpm dev` starts Vite dev server.
  - `cd frontend && pnpm build` builds production assets.
  - `cd frontend && pnpm test` runs Vitest once.
- Backend (run inside `backend/` so relative paths resolve correctly):
  - `.\\.venv\\Scripts\\python -m uvicorn main:app --reload --port 8000`
  - `.\\.venv\\Scripts\\python -m pytest test_*.py -v --timeout=60`

## Coding Style & Naming Conventions
- Follow `.editorconfig`: UTF-8, LF line endings, trim trailing whitespace, final newline.
- Indentation: 2 spaces for `js/vue/json/yml`, 4 spaces for Python.
- Vue components use `PascalCase` file names (for example `Realtime.vue`).
- Python modules/functions use `snake_case`; classes use `PascalCase`.
- Keep comments focused on non-obvious logic and remove dead code during refactors.

## Testing Guidelines
- Frontend testing stack: Vitest + `@vue/test-utils`.
- Backend testing stack: pytest; keep runs bounded with `--timeout=60`.
- Name frontend tests `*.spec.js` under `__tests__/`; backend tests `test_*.py`.
- Add or update tests for any route, detection flow, auth, or store behavior changes.

## Commit & Pull Request Guidelines
- Prefer conventional prefixes used in history: `feat:`, `fix:`, `perf:`, `chore:` (optional scope like `feat(realtime): ...`).
- Keep commits focused and avoid mixing unrelated changes.
- PRs should include: change summary, impact/risk, linked issue/task, and test evidence (`pnpm test`, `pytest ...`).
- Include screenshots or short GIFs for UI changes.

## Security & Configuration Tips
- Start from `.env.example` / `.env.local.example`; never commit real secrets.
- Validate Supabase/auth environment variables before deployment.
- Treat model weights and generated outputs as environment-specific assets, not portable source files.
