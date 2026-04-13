# Repository Guidelines

## Project Structure & Module Organization
- `backend/`: FastAPI service. API routes live in `backend/app/api/`, business logic in `backend/app/services/`, and shared config/logging in `backend/app/core/`.
- `frontend/`: Vue 3 + Vite client. Views are in `frontend/src/views/`, reusable UI in `frontend/src/components/`, layouts in `frontend/src/layouts/`, and Pinia stores in `frontend/src/stores/`.
- Tests are colocated by stack: backend tests use `backend/test_*.py`; frontend tests use `frontend/src/**/__tests__/*.spec.js`.
- Runtime outputs (`logs/`, `runs/`, `backend/uploads/`, `backend/results/`, `backend/runtime/`) are generated artifacts, not source.

## Build, Test, and Development Commands
- One-click local startup (Windows): `运行项目.bat` (starts backend on `8000` and frontend on `5173` if ports are free).
- Frontend:
  - `cd frontend && pnpm dev` — start Vite dev server.
  - `cd frontend && pnpm build` — build production assets.
  - `cd frontend && pnpm test` — run Vitest once.
- Backend (run from `backend/` so relative paths resolve correctly):
  - `.\.venv\Scripts\python -m uvicorn main:app --reload --port 8000`
  - `.\.venv\Scripts\python -m pytest test_*.py -v --timeout=60`

## Coding Style & Naming Conventions
- Follow `.editorconfig`: UTF-8, LF, trim trailing whitespace, final newline.
- Indentation: 2 spaces for `js/vue/json/yml`; 4 spaces for Python.
- Vue component files use `PascalCase` (for example `Realtime.vue`); stores/utilities use lowercase names (for example `auth.js`).
- Python modules and functions use `snake_case`; classes use `PascalCase`.

## Testing Guidelines
- Frontend: Vitest + `@vue/test-utils`; use `*.spec.js` under `__tests__/`.
- Backend: pytest with `test_*.py` naming in `backend/`.
- Keep backend test runs bounded with `--timeout=60` to avoid hangs in local and CI workflows.
- Update or add tests for every behavior change in API routes, detection flow, or store logic.

## Commit & Pull Request Guidelines
- Prefer Conventional Commits seen in history: `feat:`, `fix:`, `perf:`, `chore:` (optional scope, e.g., `feat(realtime): ...`).
- Keep commits focused and logically grouped.
- PRs should include: change summary, reason/impact, linked issue or task, and test evidence (`pnpm test`, `pytest ...`).
- For UI-facing changes, include screenshots or short GIFs.

## Security & Configuration Tips
- Start from `.env.example` and avoid committing real secrets.
- Validate Supabase/auth environment variables before deployment.
- Treat model weights and generated outputs as environment-specific assets.
