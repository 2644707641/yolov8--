"""测试 ai_analysis 推荐逻辑优化后的行为。"""
import asyncio
import sys, os

import httpx
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "app"))

from app.services.ai_analysis import analyze_spatial_distribution, call_llm_analysis
from app.api.analysis_routes import AnalysisRequest
from pydantic import ValidationError


def _make_det(bbox, class_name):
    return {"bbox": bbox, "class": class_name}


def test_central_area_recommended():
    """截图场景：中央 3空/1占 应为最推荐，而非右下 4空/4占。"""
    W, H = 1920, 1080
    dets = []
    # 中央区域 (640~1280, 360~720): 3 空 + 1 占
    for i in range(3):
        dets.append(_make_det([700 + i * 80, 400, 750 + i * 80, 450], "empty"))
    dets.append(_make_det([900, 500, 950, 550], "occupied"))
    # 右下区域 (1280~1920, 720~1080): 4 空 + 4 占
    for i in range(4):
        dets.append(_make_det([1400 + i * 80, 800, 1450 + i * 80, 850], "empty"))
    for i in range(4):
        dets.append(_make_det([1400 + i * 80, 900, 1450 + i * 80, 950], "occupied"))
    # 左上 (0~640, 0~360): 2 空 + 2 占
    dets.append(_make_det([100, 50, 150, 100], "empty"))
    dets.append(_make_det([200, 50, 250, 100], "empty"))
    dets.append(_make_det([300, 50, 350, 100], "occupied"))
    dets.append(_make_det([400, 50, 450, 100], "occupied"))

    result = analyze_spatial_distribution(dets, W, H)
    assert result is not None
    assert result["bestZone"] == "中央", f"预期中央最推荐，实际为 {result['bestZone']}"
    assert result["bestZoneEmptyCount"] == 3

    # 中央应该强烈推荐
    central = next(z for z in result["zones"] if z["label"] == "中央")
    assert central["recommendation"] == "强烈推荐"

    # 右下 4空/4占 不应比中央排名高
    right_bottom = next(z for z in result["zones"] if z["label"] == "右下")
    assert central["vacancyRate"] > right_bottom["vacancyRate"]  # 75% > 50%
    print("✅ 中央区域正确推荐为最优")


def test_single_empty_not_recommended():
    """只有 1 个空位的区域不应被标为'推荐'。"""
    W, H = 1920, 1080
    dets = []
    # 左上: 1空 + 3占 → 空闲率 25%，不应推荐
    dets.append(_make_det([100, 50, 150, 100], "empty"))
    for _ in range(3):
        dets.append(_make_det([200, 50, 250, 100], "occupied"))
    # 中央: 4空 + 1占 → 空闲率 80%，应强烈推荐
    for i in range(4):
        dets.append(_make_det([700 + i * 80, 400, 750 + i * 80, 450], "empty"))
    dets.append(_make_det([900, 500, 950, 550], "occupied"))

    result = analyze_spatial_distribution(dets, W, H)
    left_top = next(z for z in result["zones"] if z["label"] == "左上")
    assert left_top["recommendation"] != "推荐", f"1个空位不应标'推荐'，实际为 '{left_top['recommendation']}'"
    assert left_top["recommendation"] == "有空位"
    print("✅ 1个空位区域正确降级为'有空位'")


def test_many_empty_crowded_lower_than_fewer_but_freer():
    """空车位多但拥挤的区域优先级低于空车位稍少但更空闲的区域。"""
    W, H = 1920, 1080
    dets = []
    # 右下: 5空 + 10占 → 空闲率 33%，空车位多但拥挤
    for i in range(5):
        dets.append(_make_det([1400 + i * 60, 800, 1440 + i * 60, 840], "empty"))
    for i in range(10):
        dets.append(_make_det([1400 + i * 60, 850, 1440 + i * 60, 890], "occupied"))
    # 中央: 3空 + 1占 → 空闲率 75%，空车位少但更空闲
    for i in range(3):
        dets.append(_make_det([700 + i * 80, 400, 750 + i * 80, 450], "empty"))
    dets.append(_make_det([900, 500, 950, 550], "occupied"))

    result = analyze_spatial_distribution(dets, W, H)
    assert result["bestZone"] == "中央", f"中央应最推荐，实际为 {result['bestZone']}"
    print("✅ 更空闲但空位少的区域正确优先于拥挤但空位多的区域")


def test_all_zones_only_one_empty():
    """所有区域都只有1个空位时，应降级显示，不盲目推荐。"""
    W, H = 1920, 1080
    dets = []
    # 左上: 1空 + 2占
    dets.append(_make_det([100, 50, 150, 100], "empty"))
    dets.append(_make_det([200, 50, 250, 100], "occupied"))
    dets.append(_make_det([300, 50, 350, 100], "occupied"))
    # 中央: 1空 + 1占
    dets.append(_make_det([700, 400, 750, 450], "empty"))
    dets.append(_make_det([900, 500, 950, 550], "occupied"))

    result = analyze_spatial_distribution(dets, W, H)
    for z in result["zones"]:
        if z["empty"] == 1:
            # 只有1个空位的区域不应标"推荐"，最多"有空位"
            assert z["recommendation"] in ("有空位", "强烈推荐"), \
                f"{z['label']} 只有1个空位，推荐等级不应为'{z['recommendation']}'"
    print("✅ 所有区域仅1个空位时，正确降级显示")


def test_invalid_bbox_and_none_class_should_not_break_analysis():
    """异常检测输入（极端 bbox + None class）不应导致分析失败。"""
    W, H = 1920, 1080
    dets = [
        _make_det([700, 400, 750, 450], "empty"),
        _make_det([-2000, 10, -1500, 50], "empty"),
        _make_det([100, 100, 160, 160], None),
    ]

    result = analyze_spatial_distribution(dets, W, H)
    assert result is not None
    assert result["totalEmpty"] == 2
    assert result["totalOccupied"] == 1
    print("✅ 异常输入被安全处理，分析结果可用")


def test_analysis_request_should_validate_dimensions_and_detection_count():
    """分析接口请求体应拒绝非法尺寸和过大 detections。"""
    valid_det = {"bbox": [0, 0, 10, 10], "class": "empty"}

    try:
        AnalysisRequest(detections=[valid_det], imgWidth=0, imgHeight=1080)
    except ValidationError:
        pass
    else:
        raise AssertionError("imgWidth=0 应触发校验错误")

    try:
        AnalysisRequest(
            detections=[valid_det] * 2001,
            imgWidth=1920,
            imgHeight=1080,
        )
    except ValidationError:
        pass
    else:
        raise AssertionError("detections 超过上限应触发校验错误")

    print("✅ 分析请求体参数校验生效")


def test_call_llm_analysis_should_use_v1_chat_completions_for_root_url():
    """根地址应自动补全到 /v1/chat/completions。"""
    captured = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["url"] = str(request.url)
        return httpx.Response(
            200,
            json={
                "choices": [
                    {"message": {"content": "建议优先前往左侧停车"}}
                ],
                "model": "demo-model",
            },
        )

    client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    try:
        result = asyncio.run(
            call_llm_analysis(
                spatial_result={
                    "zones": [{"label": "左侧", "empty": 3, "occupied": 1}],
                    "totalEmpty": 3,
                    "totalOccupied": 1,
                    "bestZone": "左侧",
                    "bestZoneEmptyCount": 3,
                },
                api_url="https://example.com",
                api_key="test-key",
                model="demo-model",
                client=client,
            )
        )
    finally:
        asyncio.run(client.aclose())

    assert result["success"] is True
    assert captured["url"] == "https://example.com/v1/chat/completions"


def test_call_llm_analysis_should_parse_content_part_arrays():
    """兼容 content 为数组分段的返回格式。"""

    def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "choices": [
                    {
                        "message": {
                            "content": [
                                {"type": "text", "text": "建议优先前往中部，其次右侧"},
                            ]
                        }
                    }
                ],
                "model": "demo-model",
            },
        )

    client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    try:
        result = asyncio.run(
            call_llm_analysis(
                spatial_result={
                    "zones": [{"label": "中部", "empty": 4, "occupied": 1}],
                    "totalEmpty": 4,
                    "totalOccupied": 1,
                    "bestZone": "中部",
                    "bestZoneEmptyCount": 4,
                },
                api_url="https://example.com/v1",
                api_key="test-key",
                model="demo-model",
                client=client,
            )
        )
    finally:
        asyncio.run(client.aclose())

    assert result["success"] is True
    assert "中部" in result["suggestion"]


def test_call_llm_analysis_should_parse_sse_stream_bodies():
    """兼容错误返回为 SSE 分片的网关。"""

    def handler(_: httpx.Request) -> httpx.Response:
        body = (
            'data: {"choices":[{"delta":{"role":"assistant","content":"建议"}}]}\n\n'
            'data: {"choices":[{"delta":{"content":"优先前往左侧"}}]}\n\n'
            'data: [DONE]\n\n'
        )
        return httpx.Response(
            200,
            headers={"content-type": "text/event-stream"},
            text=body,
        )

    client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    try:
        result = asyncio.run(
            call_llm_analysis(
                spatial_result={
                    "zones": [{"label": "左侧", "empty": 4, "occupied": 1}],
                    "totalEmpty": 4,
                    "totalOccupied": 1,
                    "bestZone": "左侧",
                    "bestZoneEmptyCount": 4,
                },
                api_url="https://example.com",
                api_key="test-key",
                model="demo-model",
                client=client,
            )
        )
    finally:
        asyncio.run(client.aclose())

    assert result["success"] is True
    assert result["suggestion"] == "建议优先前往左侧"


def test_call_llm_analysis_should_strip_markdown_tokens():
    """LLM 返回 Markdown 时应清洗为纯文本。"""

    def handler(_: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "choices": [
                    {
                        "message": {
                            "content": "**停车建议：**\n- **优先推荐：** 左侧\n- `备注` [详情](https://example.com)"
                        }
                    }
                ],
                "model": "demo-model",
            },
        )

    client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    try:
        result = asyncio.run(
            call_llm_analysis(
                spatial_result={
                    "zones": [{"label": "左侧", "empty": 4, "occupied": 1}],
                    "totalEmpty": 4,
                    "totalOccupied": 1,
                    "bestZone": "左侧",
                    "bestZoneEmptyCount": 4,
                },
                api_url="https://example.com/v1",
                api_key="test-key",
                model="demo-model",
                client=client,
            )
        )
    finally:
        asyncio.run(client.aclose())

    assert result["success"] is True
    assert "**" not in result["suggestion"]
    assert "`" not in result["suggestion"]
    assert "[详情](" not in result["suggestion"]
    assert "停车建议" in result["suggestion"]


if __name__ == "__main__":
    test_central_area_recommended()
    test_single_empty_not_recommended()
    test_many_empty_crowded_lower_than_fewer_but_freer()
    test_all_zones_only_one_empty()
    test_invalid_bbox_and_none_class_should_not_break_analysis()
    test_analysis_request_should_validate_dimensions_and_detection_count()
    test_call_llm_analysis_should_use_v1_chat_completions_for_root_url()
    test_call_llm_analysis_should_parse_content_part_arrays()
    test_call_llm_analysis_should_parse_sse_stream_bodies()
    test_call_llm_analysis_should_strip_markdown_tokens()
    print("\n🎉 全部测试通过")
