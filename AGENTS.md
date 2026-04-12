# Repository Guidelines

## Project Structure & Module Organization
This repo has a Vue frontend and a FastAPI backend.

- `frontend/`: Vite + Vue 3 app. Main code is in `src/` (`views/`, `components/`, `layouts/`, `stores/`, `router/`, `utils/`).
- `frontend/src/**/__tests__/`: frontend unit tests (`*.spec.js`) with Vitest.
- `backend/`: FastAPI app, YOLOv8 inference, and API integration.
- `backend/app/api/`: route modules (detection, history, settings, model weights, system).
- `backend/app/services/`: business logic (detection, auth, storage, live stream).
- `backend/app/core/`: shared config, logging, and runtime patches.
- `backend/test_*.py`: main backend pytest files.

## Build, Test, and Development Commands
- `cd frontend && pnpm install`: install frontend dependencies.
- `cd frontend && pnpm dev`: run frontend dev server.
- `cd frontend && pnpm build`: build production frontend assets.
- `cd frontend && pnpm test`: run Vitest (`pnpm test:watch` for watch mode).
- `cd backend && .\.venv\Scripts\python -m pip install -r requirements.txt`: install backend dependencies.
- `cd backend && .\.venv\Scripts\python -m uvicorn main:app --reload --port 8000`: run backend locally.
- `cd backend && .\.venv\Scripts\python -m pytest test_*.py -v`: run backend tests.
- Windows shortcut: use the repository root batch launcher to start frontend and backend together.

## Coding Style & Naming Conventions
Use `.editorconfig`: 2 spaces for JS/Vue/JSON/YAML, 4 spaces for Python, UTF-8, LF line endings.

- Vue components and views use `PascalCase` file names (for example, `ModelWeights.vue`).
- Store and utility modules use concise lowercase names (for example, `auth.js`, `protected-url.js`).
- Python modules/functions use `snake_case`; classes use `PascalCase`.
- Keep API and service functions small and composable.

## Testing Guidelines
- Frontend stack: Vitest + `@vue/test-utils` + `jsdom`.
- Backend stack: Pytest.
- Naming: frontend `*.spec.js`, backend `test_*.py`.
- Update tests for behavior changes; add regression tests for bug fixes.

## Commit & Pull Request Guidelines
Recent history uses Conventional Commits (`feat:`, `fix:`, `chore:`, and scopes like `feat(realtime):`).

- Keep commits atomic.
- PRs should include purpose, touched modules, and test evidence (`pnpm test`, `pytest`).
- For UI changes, include screenshots or short GIFs.
- Link related issues/tasks and call out `.env` or config changes.

## Security & Configuration Tips
- Keep secrets in `.env` only; never commit real credentials.
- Frontend reads env from repository root via Vite `envDir`.
- Treat model weights and runtime outputs as environment artifacts unless versioning is intentional.
