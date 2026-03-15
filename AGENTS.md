# Repository Guidelines

## Project Structure & Module Organization

This repository has two main apps: `backend` and `frontend`. The FastAPI entrypoint is `backend/main.py`, and most server code lives under `backend/app`, split by `api`, `services`, and `core`. Backend API and security tests currently live as root-level files such as `backend/test_history_api.py` and `backend/test_security_api.py`. The frontend is a Vite + Vue 3 app in `frontend/src`; keep pages in `views`, reusable UI in `components`, routing in `router`, shared state in `stores`, and helpers in `utils`. Treat `models`, `uploads`, `results`, and `runtime` as data or runtime-output directories, not places for business logic.

## Build, Test, and Development Commands

Use `cd frontend && npm run dev` for local frontend development, `cd frontend && npm run build` for production builds, and `cd frontend && npm run preview` to verify the built bundle. Run frontend tests with `cd frontend && npm run test`. Install backend dependencies with `pip install -r backend/requirements.txt`, then start the API with `cd backend && python -m uvicorn main:app --reload`. Run backend tests with `python -m pytest backend/test_*.py -q`. When running automated tests, keep command timeouts within 60 seconds.

## Coding Style & Naming Conventions

Follow `.editorconfig`: use 4 spaces for Python and 2 spaces for `js`, `vue`, and JSON files. Use `snake_case` for Python modules, functions, and variables. Use `PascalCase` for Vue component filenames and clear `camelCase` names for stores and utility functions. Prefer small focused modules, remove dead compatibility code during refactors, and add brief Chinese comments only for non-obvious workflow or model logic.

## Testing Guidelines

Place frontend tests near features under `frontend/src/**/__tests__` using `*.spec.js`. Add or update tests whenever you change a view, route, or Pinia store. Backend tests should center on FastAPI `TestClient` flows and cover both success and failure paths for auth, history, settings, and upload-related APIs.

## Commit & Pull Request Guidelines

Recent history mixes Chinese summaries and conventional prefixes like `chore:`; either style is acceptable if the scope is clear and focused. Keep each commit limited to one feature or fix. PRs should include the affected modules, commands used for verification, risk notes, and screenshots for UI changes.

## Security & Configuration Tips

Never commit `.env`, local credentials, Supabase secrets, uploaded samples, generated logs, or large model weights unless explicitly required. If you change deployment or auth behavior, verify `vercel.json`, frontend environment variables, and backend configuration together.
