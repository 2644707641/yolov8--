"""
AI 智能分析服务：启发式空间分区 + LLM 增强。
"""

from __future__ import annotations

import json
import logging
import re
from typing import Any, Dict, List, Optional
from urllib.parse import urlsplit, urlunsplit

import httpx

logger = logging.getLogger("yolov8.ai_analysis")

_EMPTY_KEYWORDS = {"empty", "free", "available", "vacant", "spare", "空"}

_ZONE_LABELS = {
    (0, 0): "左上",
    (0, 1): "上方",
    (0, 2): "右上",
    (1, 0): "左侧",
    (1, 1): "中央",
    (1, 2): "右侧",
    (2, 0): "左下",
    (2, 1): "下方",
    (2, 2): "右下",
}

_ZONE_ORDER = [
    (0, 0), (0, 1), (0, 2),
    (1, 0), (1, 1), (1, 2),
    (2, 0), (2, 1), (2, 2),
]

_LLM_SYSTEM_PROMPT = (
    "你是一个智能停车位分析助手。"
    "根据各区域空车位和占用数量，给出简短、可执行的停车建议。"
    "优先推荐空位多且空闲率高的区域。"
)

_LLM_USER_PROMPT_TEMPLATE = (
    "各区域车位分布：\n{spatial_data}\n\n"
    "总空车位：{total_empty}\n"
    "总占用车位：{total_occupied}\n"
    "最空闲区域：{best_zone}（{best_empty_count}个空位）\n\n"
    "请给出简洁停车建议。"
)


def _is_empty_class(class_name: Any) -> bool:
    """判断检测类别是否为空车位。"""
    if class_name is None:
        return False
    if not isinstance(class_name, str):
        class_name = str(class_name)
    name_lower = class_name.lower()
    return any(keyword in name_lower for keyword in _EMPTY_KEYWORDS)


def _assign_zone(
    bbox: List[float],
    img_width: int,
    img_height: int,
) -> tuple[int, int]:
    """将 bbox 中心点映射到 3x3 九宫格区域 (row, col)。"""
    cx = (bbox[0] + bbox[2]) / 2
    cy = (bbox[1] + bbox[3]) / 2
    col = min(2, max(0, int(cx / (img_width / 3)))) if img_width > 0 else 1
    row = min(2, max(0, int(cy / (img_height / 3)))) if img_height > 0 else 1
    return row, col


def analyze_spatial_distribution(
    detections: List[dict],
    img_width: int = 1920,
    img_height: int = 1080,
) -> Optional[Dict[str, Any]]:
    """启发式空间分析，输出区域推荐。"""
    if not detections:
        return None

    zone_stats: Dict[tuple[int, int], Dict[str, int]] = {}
    for det in detections:
        bbox = det.get("bbox")
        if not bbox or len(bbox) < 4:
            continue
        try:
            normalized_bbox = [float(v) for v in bbox[:4]]
        except (TypeError, ValueError):
            continue

        class_name = det.get("class") or "未知"
        zone_key = _assign_zone(normalized_bbox, img_width, img_height)
        if zone_key not in zone_stats:
            zone_stats[zone_key] = {"empty": 0, "occupied": 0, "total": 0}
        if _is_empty_class(class_name):
            zone_stats[zone_key]["empty"] += 1
        else:
            zone_stats[zone_key]["occupied"] += 1
        zone_stats[zone_key]["total"] += 1

    if not zone_stats:
        return None

    total_empty = 0
    total_occupied = 0
    scored_zones: List[Dict[str, Any]] = []

    max_empty_count = 0
    for stats in zone_stats.values():
        total_empty += stats["empty"]
        total_occupied += stats["occupied"]
        if stats["empty"] > max_empty_count:
            max_empty_count = stats["empty"]

    for zone_key, stats in zone_stats.items():
        vacancy_rate = stats["empty"] / stats["total"] if stats["total"] > 0 else 0.0
        empty_norm = stats["empty"] / max_empty_count if max_empty_count > 0 else 0.0
        score = vacancy_rate * 0.6 + empty_norm * 0.4
        scored_zones.append({
            "key": zone_key,
            "empty": stats["empty"],
            "occupied": stats["occupied"],
            "total": stats["total"],
            "vacancyRate": vacancy_rate,
            "score": score,
        })

    has_empty = [z for z in scored_zones if z["empty"] > 0]
    has_empty.sort(key=lambda z: (z["score"], z["empty"]), reverse=True)

    best_zone_key = has_empty[0]["key"] if has_empty else None
    best_empty_count = has_empty[0]["empty"] if has_empty else 0
    best_occupied_count = has_empty[0]["occupied"] if has_empty else 0

    recommended_keys: List[tuple[int, int]] = []
    for z in has_empty:
        if z["score"] >= 0.4 and z["empty"] >= 2:
            recommended_keys.append(z["key"])
        elif len(recommended_keys) < 2:
            recommended_keys.append(z["key"])

    zones_list = []
    best_label = None
    for zone_key in _ZONE_ORDER:
        stats = zone_stats.get(zone_key, {"empty": 0, "occupied": 0, "total": 0})
        label = _ZONE_LABELS[zone_key]
        vacancy_rate = stats["empty"] / stats["total"] if stats["total"] > 0 else 0.0
        is_recommended = zone_key in recommended_keys
        is_best = zone_key == best_zone_key and best_empty_count > 0

        if is_best:
            recommendation = "强烈推荐"
        elif is_recommended and stats["empty"] >= 2:
            recommendation = "推荐"
        elif stats["empty"] > 0:
            recommendation = "有空位"
        elif stats["occupied"] > 0:
            recommendation = "已满"
        else:
            recommendation = ""

        if is_best:
            best_label = label
        zones_list.append({
            "label": label,
            "row": zone_key[0],
            "col": zone_key[1],
            "empty": stats["empty"],
            "occupied": stats["occupied"],
            "total": stats["total"],
            "vacancyRate": round(vacancy_rate, 2),
            "isBest": is_best,
            "isRecommended": is_recommended,
            "recommendation": recommendation,
        })

    recommended_labels = [_ZONE_LABELS[k] for k in recommended_keys]

    if best_label and best_empty_count > 0:
        summary = f"{best_label}最空闲（{best_empty_count}空{best_occupied_count}占），建议优先前往。"
    elif total_empty == 0 and total_occupied > 0:
        summary = "当前画面未发现空车位。"
    else:
        summary = "未检测到足够车位信息，无法提供方位建议。"

    return {
        "zones": zones_list,
        "recommendedZones": recommended_labels,
        "bestZone": best_label,
        "bestZoneEmptyCount": best_empty_count,
        "totalEmpty": total_empty,
        "totalOccupied": total_occupied,
        "summary": summary,
        "imgDimensions": {"width": img_width, "height": img_height},
    }


def _build_chat_completions_url(api_url: str) -> str:
    """兼容根地址、/v1 和完整 chat/completions 地址。"""
    normalized = (api_url or "").strip().rstrip("/")
    if not normalized:
        return ""
    if normalized.endswith("/chat/completions"):
        return normalized
    if normalized.endswith("/v1"):
        return f"{normalized}/chat/completions"

    parsed = urlsplit(normalized)
    path = parsed.path.rstrip("/")
    if not path:
        path = "/v1/chat/completions"
    else:
        path = f"{path}/v1/chat/completions"
    return urlunsplit((parsed.scheme, parsed.netloc, path, parsed.query, parsed.fragment))


def _extract_message_content(data: Dict[str, Any]) -> str:
    """解析 OpenAI 兼容响应内容。"""
    choices = data.get("choices")
    if not isinstance(choices, list) or not choices:
        return ""

    first_choice = choices[0] or {}
    message = first_choice.get("message") or {}
    content = message.get("content")

    if isinstance(content, str):
        return content.strip()

    if isinstance(content, list):
        text_parts: List[str] = []
        for item in content:
            if isinstance(item, str) and item.strip():
                text_parts.append(item.strip())
                continue
            if not isinstance(item, dict):
                continue
            text_value = item.get("text")
            if isinstance(text_value, str) and text_value.strip():
                text_parts.append(text_value.strip())
        return "\n".join(text_parts).strip()

    text = first_choice.get("text")
    if isinstance(text, str):
        return text.strip()

    return ""


def _extract_sse_message_content(raw_text: str) -> str:
    """解析被网关包装成 SSE 的 chat completion 响应。"""
    text_parts: List[str] = []
    for line in raw_text.splitlines():
        stripped = line.strip()
        if not stripped.startswith("data:"):
            continue
        payload = stripped[5:].strip()
        if not payload or payload == "[DONE]":
            continue
        try:
            chunk = json.loads(payload)
        except json.JSONDecodeError:
            continue

        for choice in chunk.get("choices", []) or []:
            delta = choice.get("delta") or {}
            delta_content = delta.get("content")
            if isinstance(delta_content, str) and delta_content:
                text_parts.append(delta_content)

            message = choice.get("message") or {}
            message_content = message.get("content")
            if isinstance(message_content, str) and message_content:
                text_parts.append(message_content)

    return "".join(text_parts).strip()


def _sanitize_llm_suggestion(text: str) -> str:
    """清理常见 Markdown 标记，输出可直接展示的纯文本。"""
    if not text:
        return ""

    cleaned = text.replace("\r\n", "\n").replace("\r", "\n")

    # 去除代码块与行内代码
    cleaned = re.sub(r"```[\s\S]*?```", "", cleaned)
    cleaned = re.sub(r"`([^`]*)`", r"\1", cleaned)

    # Markdown 链接: [text](url) -> text
    cleaned = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r"\1", cleaned)

    # 标题/引用/列表标记
    cleaned = re.sub(r"^\s{0,3}#{1,6}\s*", "", cleaned, flags=re.MULTILINE)
    cleaned = re.sub(r"^\s*>\s*", "", cleaned, flags=re.MULTILINE)
    cleaned = re.sub(r"^\s*[-*+]\s+", "", cleaned, flags=re.MULTILINE)

    # 粗体/斜体标记
    cleaned = re.sub(r"\*\*|__|\*|_", "", cleaned)

    # 合并空行并裁剪
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned).strip()
    return cleaned


async def call_llm_analysis(
    spatial_result: Dict[str, Any],
    api_url: str,
    api_key: str,
    model: str = "gpt-3.5-turbo",
    timeout: float = 60.0,
    client: Optional[httpx.AsyncClient] = None,
) -> Dict[str, Any]:
    """调用 OpenAI 兼容 API 生成自然语言停车建议。"""
    zones_summary_parts = []
    for zone in spatial_result.get("zones", []):
        zones_summary_parts.append(
            f"{zone['label']}：空{zone['empty']}个，占用{zone['occupied']}个"
        )
    spatial_data_text = "\n".join(zones_summary_parts)

    user_prompt = _LLM_USER_PROMPT_TEMPLATE.format(
        spatial_data=spatial_data_text,
        total_empty=spatial_result.get("totalEmpty", 0),
        total_occupied=spatial_result.get("totalOccupied", 0),
        best_zone=spatial_result.get("bestZone", "未知"),
        best_empty_count=spatial_result.get("bestZoneEmptyCount", 0),
    )

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": _LLM_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.7,
        "max_tokens": 300,
        "stream": False,
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }

    url = _build_chat_completions_url(api_url)

    try:
        if client is not None:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
        else:
            async with httpx.AsyncClient(
                timeout=timeout,
                follow_redirects=True,
                http2=True,
            ) as temp_client:
                response = await temp_client.post(url, json=payload, headers=headers)
                response.raise_for_status()

        content_type = (response.headers.get("content-type") or "").lower()
        response_text = response.text or ""
        if "text/event-stream" in content_type or response_text.lstrip().startswith("data:"):
            data = {"model": model, "usage": None}
            content = _extract_sse_message_content(response_text)
        else:
            data = response.json()
            content = _extract_message_content(data)

        if not content:
            logger.warning("LLM 返回格式不兼容: url=%s body=%s", url, str(data)[:500])
            return {
                "success": False,
                "error": "AI 返回格式不兼容，请检查接口或模型配置",
            }

        return {
            "success": True,
            "suggestion": _sanitize_llm_suggestion(content),
            "model": data.get("model", model),
            "usage": data.get("usage"),
        }
    except httpx.TimeoutException:
        logger.warning("LLM API 超时: url=%s model=%s", url, model)
        return {
            "success": False,
            "error": "AI 分析响应超时，已展示基础分析结果",
        }
    except httpx.ConnectError:
        logger.warning("LLM API 连接失败: url=%s", url)
        return {
            "success": False,
            "error": "AI 分析服务暂不可用",
        }
    except httpx.RequestError as exc:
        logger.warning("LLM API 请求失败: url=%s type=%s detail=%s", url, type(exc).__name__, exc)
        return {
            "success": False,
            "error": f"AI 服务请求失败：{type(exc).__name__}",
        }
    except httpx.HTTPStatusError as exc:
        status_code = exc.response.status_code
        logger.warning(
            "LLM API 返回错误: status=%s url=%s body=%s",
            status_code, url, exc.response.text[:200],
        )
        if status_code in (401, 403):
            return {
                "success": False,
                "error": "AI 服务认证失败，请检查 API Key",
            }
        if status_code == 429:
            return {
                "success": False,
                "error": "AI 请求过于频繁，请稍后重试",
                "retryable": True,
            }
        return {
            "success": False,
            "error": f"AI 服务返回错误：HTTP {status_code}",
        }
    except Exception as exc:
        logger.exception("LLM 分析异常: %s", exc)
        return {
            "success": False,
            "error": f"AI 分析失败：{type(exc).__name__}",
        }


async def run_full_analysis(
    detections: List[dict],
    img_width: int,
    img_height: int,
    ai_config: Optional[Dict[str, Any]] = None,
    client: Optional[httpx.AsyncClient] = None,
) -> Dict[str, Any]:
    """统一入口：先启发式，再按配置调用 LLM。"""
    spatial_result = None
    try:
        spatial_result = analyze_spatial_distribution(
            detections=detections,
            img_width=img_width,
            img_height=img_height,
        )
    except Exception as exc:
        logger.warning("启发式分析异常: %s", exc)

    llm_result = None
    if ai_config and spatial_result:
        api_url = (ai_config.get("apiUrl") or "").strip()
        api_key = (ai_config.get("apiKey") or "").strip()
        model_name = (ai_config.get("model") or "gpt-3.5-turbo").strip()
        if api_url and api_key:
            llm_result = await call_llm_analysis(
                spatial_result=spatial_result,
                api_url=api_url,
                api_key=api_key,
                model=model_name,
                client=client,
            )

    return {
        "spatial": spatial_result,
        "llm": llm_result,
    }


async def run_llm_only(
    detections: List[dict],
    img_width: int,
    img_height: int,
    ai_config: Optional[Dict[str, Any]] = None,
    client: Optional[httpx.AsyncClient] = None,
) -> Dict[str, Any]:
    """仅执行 LLM 分析（用于异步重试接口）。"""
    spatial_result = None
    try:
        spatial_result = analyze_spatial_distribution(
            detections=detections,
            img_width=img_width,
            img_height=img_height,
        )
    except Exception as exc:
        logger.warning("启发式分析异常: %s", exc)

    if not ai_config or not spatial_result:
        return {"spatial": spatial_result, "llm": None}

    api_url = (ai_config.get("apiUrl") or "").strip()
    api_key = (ai_config.get("apiKey") or "").strip()
    model_name = (ai_config.get("model") or "gpt-3.5-turbo").strip()
    if not api_url or not api_key:
        return {"spatial": spatial_result, "llm": None}

    llm_result = await call_llm_analysis(
        spatial_result=spatial_result,
        api_url=api_url,
        api_key=api_key,
        model=model_name,
        client=client,
    )
    return {"spatial": spatial_result, "llm": llm_result}
