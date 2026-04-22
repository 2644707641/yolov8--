# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

YOLOv8-based parking space detection app with a FastAPI backend and Vue 3 frontend. Runs in dual mode: with Supabase (cloud auth + storage) or without (local JSON file storage). The frontend always requires Supabase for authentication.

## Development Commands

```bash
# Backend (from repo root)
cd backend && .venv/Scripts/python.exe -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# Frontend
cd frontend && pnpm dev          # dev server on :3000
cd frontend && pnpm build        # production build
cd frontend && pnpm test         # Vitest once
cd frontend && pnpm test:watch   # Vitest watch mode

# Backend single test
cd backend && .venv/Scripts/python.exe -m pytest test_detection_service.py -v --timeout=60
cd backend && .venv/Scripts/python.exe test_history_api.py   # standalone script style
```

Frontend dev server proxies `/api` to `localhost:8000` (configured in `vite.config.js`).

## Architecture

### Backend (`backend/`)

**Entry**: `main.py` — creates FastAPI app, initializes Supabase client (optional), shared `httpx.AsyncClient`, and local settings store on `app.state`.

**Config**: `app/core/config.py` — `Settings` dataclass reads from root `.env` via `python-dotenv`. `BASE_DIR` resolves to repo root so both frontend and backend env vars load from one file. Key settings: `SUPABASE_URL/KEY`, `JWT_SECRET`, upload/model/result dirs, `MAX_CONCURRENT_DETECTIONS`, AI API config.

**Routes** (all mounted under `api/` via `routes.py`):
- `detection_routes.py` — `/api/detect` (image/video upload + SSE progress), `/api/upload-model`, `/ws/detect-live` (WebSocket real-time inference)
- `history_routes.py` — `/api/history` CRUD with archive/restore
- `settings_routes.py` — `/api/settings` user + app preferences
- `files_routes.py` — `/api/results/{name}`, `/api/uploads/{name}` static file serving with auth
- `model_weight_routes.py` — Supabase-backed model weight management
- `analysis_routes.py` — `/api/ai/analyze-llm` async LLM parking advice
- `system_routes.py` — health, version, storage stats

**Services** (`app/services/`):
- `detection.py` — Core YOLOv8 inference. LRU model cache (max 4), semaphore-controlled concurrency, custom annotation colors (green=empty, red=occupied), video tracking with ByteTrack fallback, ffmpeg post-processing. Exposes `run_detection()`, `infer_live_frame_sync()`, `infer_live_array_sync()`, `detect_live_frame_sync()`.
- `ai_analysis.py` — Two-phase analysis: heuristic 3x3 spatial zone scoring (sync, always runs), then optional LLM call via OpenAI-compatible API. `run_full_analysis()` is the unified entry; `run_llm_only()` for async retry endpoint.
- `auth.py` — JWT validation against `SUPABASE_JWT_SECRET` (HS256, audience="authenticated"). Returns user_id from `sub` claim.
- `local_state.py` — Thread-safe JSON file read/write for settings and history in `backend/runtime/`. Single lock protects the entire JSON payload.
- `model_registry.py` — In-memory `Dict[str, Path]` mapping user_id to uploaded model path, async-lock guarded.
- `model_weights.py` — Supabase storage CRUD for model weights, with local cache download.
- `storage.py` — File upload to Supabase buckets and local filesystem.
- `live_stream.py` — Network stream (RTSP/HTTP) capture validation and frame reading.
- `live_runtime_stats.py` — Tracking ID registry with TTL-based pruning for live sessions.
- `local_cleanup.py` — Periodic local file/record cleanup by retention and max-records.
- `system_monitor.py` — Active task/stream counters for system status endpoint.
- `validators.py` — File extension and size validation.

**Common helpers** (`app/api/common.py`): shared dependencies injected into route handlers — `resolve_model_path()` (priority: Supabase active weight > local registry > default weight), auth resolution, settings access, local cleanup orchestration.

**PyTorch patch** (`app/core/pytorch_patch.py`): Monkey-patches `torch.load` to set `weights_only=False`, patches `fuse_conv_and_bn`/`fuse_deconv_and_bn` for non-contiguous tensor compatibility, adds `DetectionModel` to safe globals. Called once at import time in `detection.py`.

### Frontend (`frontend/src/`)

**Tech**: Vue 3 + Vite + Pinia + Vue Router + Tailwind CSS + Supabase JS client. No Vue Query — API calls use `fetch`/`axios` directly from stores.

**Router** (`router/index.js`): All authenticated routes under `AppShell` layout with `requiresAuth` guard. Routes: `/overview`, `/workspace` (Dashboard), `/history`, `/model-weights`, `/realtime`, `/settings`. `/login` is guest-only.

**Stores** (Pinia composition API):
- `auth.js` — Supabase auth (login/register/logout), auto-session restore, Chinese error message translation.
- `detection.js` — Full detection workflow: upload model, run detection (SSE streaming for progress), history CRUD, AI analysis with async LLM retry + cooldown. Settings persisted to `localStorage` under key `yolov8.settings.v1`.

**Key components**:
- `AiAnalysisPanel.vue` — Displays spatial zone grid + LLM parking advice
- `Realtime.vue` — WebSocket-based live detection (camera or network stream)
- `Dashboard.vue` — Main workspace for image/video detection

**Auth flow**: Supabase client initialized in `config/supabase.js` (requires `VITE_SUPABASE_URL` + `VITE_SUPABASE_ANON_KEY`). Backend validates JWT from Supabase session. Protected file URLs use `buildProtectedApiUrl()` utility that appends token as query param.

## Dual-Mode Data Flow

When `SUPABASE_URL` + `SUPABASE_KEY` are set in `.env`:
- Auth → Supabase, file storage → Supabase buckets, history → Supabase DB
- Model weights → Supabase `model-weights` bucket with per-user cache in `models/cache/`

When not set:
- Auth still requires JWT secret (frontend always uses Supabase)
- History/settings → local JSON files in `backend/runtime/`
- Files → local `uploads/` and `results/` directories
- Model weights → in-memory registry only (lost on restart)

## Environment Configuration

Single `.env` at repo root. Frontend reads via Vite (`VITE_` prefix), backend reads via `python-dotenv` from `BASE_DIR/.env`. Copy `.env.example` to start.

Critical vars: `SUPABASE_URL`, `SUPABASE_KEY` (service_role), `SUPABASE_JWT_SECRET`, `VITE_SUPABASE_URL`, `VITE_SUPABASE_ANON_KEY`, `AI_API_URL`, `AI_API_KEY`, `AI_MODEL`.

## Code Conventions

- **Python**: 4-space indent, snake_case, type hints on public APIs, Chinese comments for key logic
- **JavaScript/Vue**: 2-space indent, camelCase, PascalCase for Vue SFCs, `*.spec.js` in `__tests__/` dirs
- **API responses**: JSON with Chinese error `detail` messages
- **Model weight resolution**: Supabase active → local registry → default path (`default/best.pt`)
- **Video codec fallback**: Windows defaults to mp4v, then MJPG/XVID/avc1/H264; other platforms try H264 first
- **SSE format for detection progress**: `data:{"stage":"...","percent":N,"message":"..."}` followed by `data:{"stage":"result","data":{...}}`
- **WebSocket binary protocol for live detection**: 4-byte big-endian meta length + JSON meta + JPEG frame bytes

## Testing

- Frontend: Vitest + jsdom + `@vue/test-utils`. Setup in `frontend/src/tests/setup.js`. Tests in `__tests__/` dirs adjacent to components.
- Backend: Assert-based `test_*.py` scripts runnable standalone or via pytest. Tests require the backend `.venv` Python interpreter.
