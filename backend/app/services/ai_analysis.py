"""
AI 智能分析服务：启发式空间分区 + LLM 增强。

每次检测完成后自动触发：
1. 启发式分析（零成本毫秒级）始终执行，同步返回
2. LLM 分析通过独立端点异步调用，不阻塞检测响应
"""

from __future__ import annotations

import json
import logging
from typing import Any, Dict, List, Optional

import httpx

logger = logging.getLogger("yolov8.ai_analysis")

# ── 空车位关键词（与 detection.py 保持一致）────────────────────────────────
_EMPTY_KEYWORDS = {"empty", "空", "free", "available", "vacant", "spare"}

# 九宫格方位标签
_ZONE_LABELS = {
    (0, 0): "左上", (0, 1): "上方", (0, 2): "右上",
    (1, 0): "左侧", (1, 1): "中央", (1, 2): "右侧",
    (2, 0): "左下", (2, 1): "下方", (2, 2): "右下",
}

# 九宫格有序排列（前端渲染用）
_ZONE_ORDER = [
    (0, 0), (0, 1), (0, 2),
    (1, 0), (1, 1), (1, 2),
    (2, 0), (2, 1), (2, 2),
]


def _is_empty_class(class_name: str) -> bool:
    """判断检测类别是否为空车位。"""
    name_lower = class_name.lower()
    return any(kw in name_lower for kw in _EMPTY_KEYWORDS)


def _assign_zone(
    bbox: List[float],
    img_width: int,
    img_height: int,
) -> tuple[int, int]:
    """将 bbox 中心点映射到 3x3 九宫格区域 (row, col)。"""
    cx = (bbox[0] + bbox[2]) / 2
    cy = (bbox[1] + bbox[3]) / 2
    col = min(2, int(cx / (img_width / 3))) if img_width > 0 else 1
    row = min(2, int(cy / (img_height / 3))) if img_height > 0 else 1
    return (row, col)


def analyze_spatial_distribution(
    detections: List[dict],
    img_width: int = 1920,
    img_height: int = 1080,
) -> Optional[Dict[str, Any]]:
    """
    启发式空间分析：将检测框映射到九宫格区域，
    统计每个区域的空车位/占用车位数量，按空闲程度推荐。

    推荐逻辑：
    - 空闲率 = 空车位 / 总车位（无车位时为 0）
    - 优先推荐有空车位且空闲率高的区域
    - 空车位多但拥挤（占用也多）的区域优先级低于空车位稍少但更空闲的区域

    返回结构：
    {
        "zones": [
            {"label": "左上", "empty": 5, "occupied": 1, "total": 6,
             "vacancyRate": 0.83, "recommendation": "推荐", "isBest": true},
            ...
        ],
        "recommendedZones": ["左侧", "右下"],
        "bestZone": "左侧",
        "bestZoneEmptyCount": 5,
        "totalEmpty": 12,
        "totalOccupied": 15,
        "summary": "左侧最空闲（5空/1占），建议前往该区域停车",
        "imgDimensions": {"width": 1920, "height": 1080}
    }
    """
    if not detections:
        return None

    zone_stats: Dict[tuple, Dict[str, int]] = {}

    for det in detections:
        bbox = det.get("bbox")
        if not bbox or len(bbox) < 4:
            continue
        class_name = det.get("class", "未知")
        zone_key = _assign_zone(bbox, img_width, img_height)
        if zone_key not in zone_stats:
            zone_stats[zone_key] = {"empty": 0, "occupied": 0, "total": 0}
        if _is_empty_class(class_name):
            zone_stats[zone_key]["empty"] += 1
        else:
            zone_stats[zone_key]["occupied"] += 1
        zone_stats[zone_key]["total"] += 1

    if not zone_stats:
        return None

    # 计算空闲率，确定推荐区域
    total_empty = 0
    total_occupied = 0
    scored_zones: List[Dict[str, Any]] = []

    for zone_key, stats in zone_stats.items():
        total_empty += stats["empty"]
        total_occupied += stats["occupied"]
        vacancy_rate = stats["empty"] / stats["total"] if stats["total"] > 0 else 0.0
        scored_zones.append({
            "key": zone_key,
            "empty": stats["empty"],
            "occupied": stats["occupied"],
            "total": stats["total"],
            "vacancyRate": vacancy_rate,
        })

    # 排序：有空车位的区域按空闲率降序，空闲率相同按空车位数降序
    has_empty = [z for z in scored_zones if z["empty"] > 0]
    has_empty.sort(key=lambda z: (z["vacancyRate"], z["empty"]), reverse=True)

    best_zone_key = has_empty[0]["key"] if has_empty else None
    best_empty_count = has_empty[0]["empty"] if has_empty else 0
    best_occupied_count = has_empty[0]["occupied"] if has_empty else 0

    # 推荐区域：空闲率 >= 50% 的区域，或空车位最多的前 3 个区域
    recommended_keys = []
    for z in has_empty:
        if z["vacancyRate"] >= 0.5 or len(recommended_keys) < 3:
            recommended_keys.append(z["key"])

    # 构建有序 zones 列表
    zones_list = []
    best_label = None
    for zone_key in _ZONE_ORDER:
        stats = zone_stats.get(zone_key, {"empty": 0, "occupied": 0, "total": 0})
        label = _ZONE_LABELS[zone_key]
        vacancy_rate = stats["empty"] / stats["total"] if stats["total"] > 0 else 0.0
        is_recommended = zone_key in recommended_keys
        is_best = zone_key == best_zone_key and best_empty_count > 0

        # 推荐等级
        if is_best:
            recommendation = "强烈推荐"
        elif is_recommended and vacancy_rate >= 0.5:
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

    summary = ""
    if best_label and best_empty_count > 0:
        if len(recommended_labels) > 1:
            others = "、".join(recommended_labels[1:])
            summary = (
                f"{best_label}最空闲（{best_empty_count}空/{best_occupied_count}占），"
                f"建议优先前往；{others}也有空位可选"
            )
        else:
            summary = f"{best_label}最空闲（{best_empty_count}空/{best_occupied_count}占），建议前往该区域停车"
    elif total_empty == 0 and total_occupied > 0:
        summary = "当前画面中未发现空车位，所有车位均被占用"
    else:
        summary = "未检测到足够的车位信息，无法提供方位建议"

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


# ── LLM 增强分析 ────────────────────────────────────────────────────────────

_LLM_SYSTEM_PROMPT = (
    "你是一个智能停车位分析助手。根据以下各区域的车位占用数据，给出实用的停车推荐。\n"
    "要求：\n"
    "1. 综合考虑空车位数和空闲率，推荐最适合停车的区域\n"
    "2. 空车位多但占用也多的区域（拥挤）优先级低于空车位稍少但更空闲的区域\n"
    "3. 如果多个区域都空闲，给出最优选择和备选区域\n"
    "4. 给出明确的方位建议（如\"建议优先前往左侧，右下也可作为备选\"）\n"
    "5. 回答不超过 200 字\n"
    "6. 不要输出字数统计、字数标注（如\"128字\"）或任何关于回答长度的元信息\n"
    "7. 不要使用 Markdown 格式（如 **加粗**），直接输出纯文本"
)

_LLM_USER_PROMPT_TEMPLATE = (
    "各区域车位分布（空闲率=空车位/总车位）：\n{spatial_data}\n\n"
    "总空车位：{total_empty}\n"
    "总占用车位：{total_occupied}\n"
    "最空闲区域：{best_zone}（{best_empty_count}个空车位）\n\n"
    "请综合空闲率分析，给出停车建议："
)


async def call_llm_analysis(
    spatial_result: Dict[str, Any],
    api_url: str,
    api_key: str,
    model: str = "gpt-3.5-turbo",
    timeout: float = 60.0,
    client: Optional[httpx.AsyncClient] = None,
) -> Dict[str, Any]:
    """
    调用 OpenAI 兼容 API 生成自然语言停车建议。

    返回：
    成功 -> {"success": True, "suggestion": "...", "model": "...", "usage": {...}}
    失败 -> {"success": False, "error": "...", "retryable": bool}
    """
    # 构建 zones 摘要文本（非 JSON，更省 token）
    zones_summary_parts = []
    for zone in spatial_result.get("zones", []):
        zones_summary_parts.append(
            f"{zone['label']}：空{zone['empty']}个，占{zone['occupied']}个"
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

    # 确保 api_url 以 /chat/completions 结尾
    url = api_url.rstrip("/")
    if not url.endswith("/chat/completions"):
        url = f"{url}/chat/completions"

    try:
        if client is not None:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
        else:
            async with httpx.AsyncClient(timeout=timeout) as temp_client:
                response = await temp_client.post(url, json=payload, headers=headers)
                response.raise_for_status()
                data = response.json()

        content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
        if not content.strip():
            return {
                "success": False,
                "error": "AI 返回了空内容，请稍后重试",
            }

        return {
            "success": True,
            "suggestion": content.strip(),
            "model": data.get("model", model),
            "usage": data.get("usage"),
        }

    except httpx.TimeoutException:
        logger.warning("LLM API 超时: url=%s model=%s", api_url, model)
        return {
            "success": False,
            "error": "AI 分析响应超时，已展示基础分析结果",
        }
    except httpx.ConnectError:
        logger.warning("LLM API 连接失败: url=%s", api_url)
        return {
            "success": False,
            "error": "AI 分析服务暂不可用",
        }
    except httpx.HTTPStatusError as exc:
        status_code = exc.response.status_code
        logger.warning(
            "LLM API 返回错误: status=%s url=%s body=%s",
            status_code, api_url, exc.response.text[:200],
        )
        if status_code in (401, 403):
            return {
                "success": False,
                "error": "AI 服务认证失败，请联系管理员",
            }
        if status_code == 429:
            return {
                "success": False,
                "error": "AI 请求过于频繁，请稍后重试",
                "retryable": True,
            }
        return {
            "success": False,
            "error": f"AI 服务返回错误（HTTP {status_code}）",
        }
    except Exception as exc:
        logger.warning("LLM 分析异常: %s", exc)
        return {
            "success": False,
            "error": "AI 分析暂时不可用，请稍后重试",
        }


async def run_full_analysis(
    detections: List[dict],
    img_width: int,
    img_height: int,
    ai_config: Optional[Dict[str, Any]] = None,
    client: Optional[httpx.AsyncClient] = None,
) -> Dict[str, Any]:
    """
    统一入口：先执行启发式分析，再根据 ai_config 决定是否调用 LLM。

    返回：
    {
        "spatial": {...} | null,   # 启发式结果
        "llm": {...} | null        # LLM 结果（null=未配置, error=失败）
    }
    """
    # 1. 启发式分析（始终执行，异常兜底）
    spatial_result = None
    try:
        spatial_result = analyze_spatial_distribution(
            detections=detections,
            img_width=img_width,
            img_height=img_height,
        )
    except Exception as exc:
        logger.warning("启发式分析异常: %s", exc)

    # 2. LLM 分析（需要配置 + 有检测结果）
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
        # 未配置 → llm_result 保持 null，前端展示引导提示

    return {
        "spatial": spatial_result,
        "llm": llm_result,
    }


async def run_llm_only(
    detections: List[dict],
    img_width: int,
    img_height: int,
    ai_config: Dict[str, Any],
    client: Optional[httpx.AsyncClient] = None,
) -> Dict[str, Any]:
    """
    仅执行 LLM 分析（用于异步重试端点）。
    先做启发式分析（LLM 需要空间数据作为输入），再调用 LLM。

    返回：
    {
        "spatial": {...} | null,
        "llm": {...} | null
    }
    """
    spatial_result = None
    try:
        spatial_result = analyze_spatial_distribution(
            detections=detections,
            img_width=img_width,
            img_height=img_height,
        )
    except Exception as exc:
        logger.warning("启发式分析异常: %s", exc)

    if not spatial_result:
        return {"spatial": None, "llm": None}

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
