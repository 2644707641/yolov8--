# Repository Guidelines

## Project Structure & Module Organization
- `backend/`: FastAPI service for detection, auth, settings, and history.
- `backend/app/api/`: Route modules (e.g., `detection_routes.py`, `history_routes.py`).
- `backend/app/services/`: Core business logic (detection pipeline, storage, auth helpers).
- `frontend/`: Vue 3 + Vite client.
- `frontend/src/views/`: Page-level views (`Realtime.vue`, `Settings.vue`, `History.vue`).
- `frontend/src/components/`: Reusable UI components.
- `frontend/src/stores/`: Pinia stores (`auth.js`, `detection.js`).
- `logs/`, `runs/`, `backend/uploads/`, `backend/results/`: runtime artifacts; do not commit generated output unless required.

## Build, Test, and Development Commands
- One-click local start (Windows): `运行项目.bat` (starts backend on `8000` and frontend on `5173`).
- Frontend:
  - `cd frontend && pnpm dev` — start Vite dev server.
  - `cd frontend && pnpm build` — production build.
  - `cd frontend && pnpm test` — run Vitest once.
- Backend (run from `backend/` to keep relative paths valid):
  - `.\.venv\Scripts\python -m uvicorn main:app --reload --port 8000` — start API.
  - `.\.venv\Scripts\python -m pytest test_*.py -v --timeout=60` — run backend tests.

## Coding Style & Naming Conventions
- Follow `.editorconfig`: UTF-8, LF, trim trailing whitespace, final newline.
- Indentation: 2 spaces for `js/vue/json/yml`, 4 spaces for Python.
- Vue components use `PascalCase` filenames; stores/utilities use lowercase names.
- Python modules/functions use `snake_case`; classes use `PascalCase`.
- Keep functions focused; place shared logic in `backend/app/services/` or `frontend/src/components/`.

## Testing Guidelines
- Frontend: Vitest + `@vue/test-utils`; place tests in `__tests__/` with `*.spec.js`.
- Backend: pytest with `test_*.py` naming in `backend/`.
- For backend test runs, always set max timeout to 60s to avoid hangs.
- Add/update tests with every behavior change, especially for APIs and state stores.

## Commit & Pull Request Guidelines
- Use Conventional Commits seen in history: `feat:`, `fix:`, `perf:`, `chore:`; optional scope like `feat(realtime): ...`.
- Keep commits small and logically grouped.
- PRs should include:
  - What changed and why.
  - Linked issue/task (if any).
  - Test evidence (`pnpm test`, `pytest ...` output summary).
  - UI screenshots/GIFs for frontend behavior changes.

## Security & Configuration Tips
- Copy from `.env.example`; never commit real secrets from `.env`.
- Treat model weights and runtime outputs as environment-specific assets.
- Validate Supabase and auth-related env vars before deploying.
