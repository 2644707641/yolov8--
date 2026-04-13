# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

YOLOv8 parking space detection app — FastAPI backend runs YOLOv8 inference, Vue 3 frontend provides the UI. Runs in **dual mode**: with Supabase env vars → cloud persistence; without → local JSON files.

## Commands

```bash
# Backend (MUST run from backend/ directory — relative paths depend on it)
cd backend && .venv/Scripts/python -m uvicorn main:app --reload --port 8000
cd backend && .venv/Scripts/python -m pytest test_*.py -v --timeout=60

# Frontend (pnpm, not npm/yarn)
cd frontend && pnpm dev
cd frontend && pnpm build
cd frontend && pnpm test          # Vitest once
cd frontend && pnpm test:watch   # Vitest watch mode

# One-click Windows startup
运行项目.bat
```

## Architecture

**Backend** (`backend/`) — FastAPI on port 8000

- `main.py` — App factory, lifespan creates shared `httpx.AsyncClient`, mounts router
- `app/api/routes.py` — Aggregates sub-routers: system, history, settings, detection, files, model_weights, analysis
- `app/api/common.py` — Shared helpers: auth resolution, storage policy, cleanup normalization
- `app/core/config.py` — `Settings` dataclass loaded from root `.env` via `load_dotenv`
- `app/services/detection.py` — YOLO inference + semaphore concurrency (default 2) + model LRU cache (max 4)
- `app/services/storage.py` — Supabase CRUD; falls back to `local_state.py` JSON files
- `app/services/ai_analysis.py` — Spatial heuristics + optional async LLM analysis
- `app/services/live_stream.py` — RTSP/network stream with WebSocket binary protocol (4-byte length prefix)

**Frontend** (`frontend/`) — Vue 3 + Vite on port 3000

- `vite.config.js` — `envDir: '..'` reads root `.env`; proxy `/api` → `http://localhost:8000`
- `src/stores/auth.js` — Supabase auth with Chinese error translation
- `src/stores/detection.js` — Detection params, SSE streaming, history, AI analysis state
- `src/router/index.js` — Auth guard requires `authStore.ready`; routes: overview, workspace, history, model-weights, realtime, settings

## Key Patterns

- **Single `.env`** at project root — both backend (`load_dotenv`) and frontend (`envDir: '..'`) read from it
- **Model resolution priority**: user active weight (Supabase) → local registry → default weight
- **Detection concurrency** controlled by `asyncio.Semaphore` (configurable via `MAX_CONCURRENT_DETECTIONS`)
- **Live detection** uses WebSocket with binary frames + BYTETracker for real-time tracking
- **Frontend API**: `axios` for REST, native `fetch` for SSE detection streaming

## Style Conventions

- Indentation: 2 spaces (JS/Vue/JSON), 4 spaces (Python)
- Vue components: `PascalCase` filenames; stores/utils: lowercase
- Python: `snake_case` functions, `PascalCase` classes
- Commits: `feat:`, `fix:`, `perf:`, `chore:` with optional scope
