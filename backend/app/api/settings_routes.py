from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Header, HTTPException, Request, status

from app.api.common import (
    API_VERSION,
    SettingsUpdate,
    auth_service,
    build_storage_policy,
    detection_service,
    get_app_settings_store,
    get_local_cleanup_meta,
    get_local_cleanup_settings,
    get_local_storage_stats,
    get_supabase_client,
    get_user_settings_store,
    logger,
    local_state,
    normalize_local_cleanup_settings,
    normalize_realtime_prefs,
    pack_detection_params,
    run_local_cleanup_for_app,
    settings,
)

router = APIRouter()


def build_settings_response(defaults, *, app, supabase_client, realtime=None):
    local_cleanup_settings = get_local_cleanup_settings(app)
    local_cleanup_meta = get_local_cleanup_meta(app)
    local_stats = get_local_storage_stats(app)
    response = {
        "success": True,
        "settings": {
            "defaults": pack_detection_params(defaults),
            "system": {
                "apiTitle": settings.api_title,
                "apiVersion": API_VERSION,
                "defaultModelName": settings.default_model_name,
                "maxUploadSizeMb": settings.max_upload_size_mb,
                "maxConcurrentDetections": settings.max_concurrent_detections,
            },
            "storage": build_storage_policy(
                supabase_client,
                local_cleanup_settings,
                local_cleanup_meta=local_cleanup_meta,
                local_stats=local_stats,
            ),
        },
    }
    if realtime is not None:
        response["settings"]["realtime"] = realtime
    return response


@router.get("/api/settings")
async def get_settings(
    request: Request,
    authorization: Optional[str] = Header(None),
):
    supabase_client = get_supabase_client(request)
    user_id = await auth_service.validate_authorization(authorization, supabase_client)

    store = get_user_settings_store(request.app)
    user_settings = store.get(user_id, {})
    defaults = user_settings.get("defaults")
    if not defaults:
        defaults = detection_service.normalize_params({})
        user_settings["defaults"] = defaults
        store[user_id] = user_settings
        local_state.save_user_settings(settings.user_settings_store_file, user_id, user_settings)

    realtime = normalize_realtime_prefs(user_settings.get("realtime"))

    return build_settings_response(defaults, app=request.app, supabase_client=supabase_client, realtime=realtime)


@router.put("/api/settings")
async def update_settings(
    request: Request,
    payload: SettingsUpdate,
    authorization: Optional[str] = Header(None),
):
    supabase_client = get_supabase_client(request)
    user_id = await auth_service.validate_authorization(authorization, supabase_client)

    store = get_user_settings_store(request.app)
    app_settings = get_app_settings_store(request.app)
    user_settings = store.get(user_id, {})
    current_defaults = user_settings.get("defaults") or detection_service.normalize_params({})
    current_defaults_front = pack_detection_params(current_defaults)
    current_local_cleanup = get_local_cleanup_settings(request.app)

    merged_raw = {
        **current_defaults_front,
        **(payload.defaults or {}),
    }
    normalized = detection_service.normalize_params(merged_raw)
    storage_payload = payload.storage or {}
    if storage_payload and not isinstance(storage_payload, dict):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="storage 必须是对象",
        )
    local_cleanup_payload = storage_payload.get("localCleanup") if storage_payload else None
    normalized_local_cleanup = normalize_local_cleanup_settings(
        local_cleanup_payload,
        current_local_cleanup,
    )

    user_settings["defaults"] = normalized
    current_realtime = user_settings.get("realtime")
    normalized_realtime = normalize_realtime_prefs(payload.realtime, current_realtime)
    user_settings["realtime"] = normalized_realtime
    store[user_id] = user_settings
    app_settings["localCleanup"] = normalized_local_cleanup
    request.app.state.app_settings = app_settings
    local_state.save_user_settings(settings.user_settings_store_file, user_id, user_settings)
    local_state.save_app_settings(settings.user_settings_store_file, app_settings)

    return build_settings_response(normalized, app=request.app, supabase_client=supabase_client, realtime=normalized_realtime)


@router.post("/api/settings/storage/cleanup")
async def cleanup_local_storage_now(
    request: Request,
    authorization: Optional[str] = Header(None),
):
    supabase_client = get_supabase_client(request)
    user_id = await auth_service.validate_authorization(authorization, supabase_client)

    store = get_user_settings_store(request.app)
    user_settings = store.get(user_id, {})
    defaults = user_settings.get("defaults") or detection_service.normalize_params({})
    if not user_settings.get("defaults"):
        user_settings["defaults"] = defaults
        store[user_id] = user_settings
        local_state.save_user_settings(settings.user_settings_store_file, user_id, user_settings)

    realtime = normalize_realtime_prefs(user_settings.get("realtime"))

    cleanup_result = run_local_cleanup_for_app(
        request.app,
        logger=logger,
        force=True,
    )

    return {
        **build_settings_response(defaults, app=request.app, supabase_client=supabase_client, realtime=realtime),
        "cleanup": {
            "removedRecords": cleanup_result["summary"]["removed_records"],
            "removedArchives": cleanup_result["summary"]["removed_archives"],
            "removedFiles": cleanup_result["summary"]["removed_files"],
            "cleanedAt": cleanup_result["cleanedAt"],
        },
    }
