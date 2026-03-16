import logging
import os
import sys
from functools import lru_cache

import torch
import torch.nn as nn

logger = logging.getLogger("yolov8.pytorch")


@lru_cache(maxsize=1)
def ensure_torch_patch() -> None:
    """
    确保在导入Ultralytics前应用兼容性补丁。
    """
    logger.info("初始化 PyTorch 兼容性补丁")
    os.environ.setdefault("TORCH_FORCE_WEIGHTS_ONLY_LOAD", "0")

    original_load = torch.load

    def _patched_torch_load(*args, **kwargs):
        kwargs["weights_only"] = False
        return original_load(*args, **kwargs)

    def _patched_fuse_conv_and_bn(conv, bn):
        """兼容非连续权重张量的 Conv + BN 融合实现。"""
        w_conv = conv.weight.contiguous().reshape(conv.out_channels, -1)
        w_bn = torch.diag(bn.weight.div(torch.sqrt(bn.eps + bn.running_var)))
        conv.weight.data = torch.mm(w_bn, w_conv).reshape(conv.weight.shape).contiguous()

        b_conv = torch.zeros(conv.out_channels, device=conv.weight.device) if conv.bias is None else conv.bias
        b_bn = bn.bias - bn.weight.mul(bn.running_mean).div(torch.sqrt(bn.running_var + bn.eps))
        fused_bias = torch.mm(w_bn, b_conv.reshape(-1, 1)).reshape(-1) + b_bn

        if conv.bias is None:
            conv.register_parameter("bias", nn.Parameter(fused_bias))
        else:
            conv.bias.data = fused_bias

        return conv.requires_grad_(False)

    def _patched_fuse_deconv_and_bn(deconv, bn):
        """兼容非连续权重张量的 ConvTranspose + BN 融合实现。"""
        w_deconv = deconv.weight.contiguous().reshape(deconv.out_channels, -1)
        w_bn = torch.diag(bn.weight.div(torch.sqrt(bn.eps + bn.running_var)))
        deconv.weight.data = torch.mm(w_bn, w_deconv).reshape(deconv.weight.shape).contiguous()

        b_deconv = (
            torch.zeros(deconv.out_channels, device=deconv.weight.device)
            if deconv.bias is None
            else deconv.bias
        )
        b_bn = bn.bias - bn.weight.mul(bn.running_mean).div(torch.sqrt(bn.running_var + bn.eps))
        fused_bias = torch.mm(w_bn, b_deconv.reshape(-1, 1)).reshape(-1) + b_bn

        if deconv.bias is None:
            deconv.register_parameter("bias", nn.Parameter(fused_bias))
        else:
            deconv.bias.data = fused_bias

        return deconv.requires_grad_(False)

    torch.load = _patched_torch_load  # type: ignore[assignment]
    logger.info("已应用 torch.load weights_only=False 补丁")

    try:
        import ultralytics.utils.torch_utils as ultralytics_torch_utils
        import ultralytics.nn.tasks  # noqa: F401

        ultralytics_torch_utils.fuse_conv_and_bn = _patched_fuse_conv_and_bn  # type: ignore[assignment]
        ultralytics_torch_utils.fuse_deconv_and_bn = _patched_fuse_deconv_and_bn  # type: ignore[assignment]

        ultralytics.nn.tasks.fuse_conv_and_bn = _patched_fuse_conv_and_bn  # type: ignore[attr-defined]
        ultralytics.nn.tasks.fuse_deconv_and_bn = _patched_fuse_deconv_and_bn  # type: ignore[attr-defined]

        ultralytics_block = sys.modules.get("ultralytics.nn.modules.block")
        if ultralytics_block is not None:
            ultralytics_block.fuse_conv_and_bn = _patched_fuse_conv_and_bn

        ultralytics_head = sys.modules.get("ultralytics.nn.modules.head")
        if ultralytics_head is not None:
            ultralytics_head.fuse_conv_and_bn = _patched_fuse_conv_and_bn

        torch.serialization.add_safe_globals([ultralytics.nn.tasks.DetectionModel])  # type: ignore[attr-defined]
        logger.info("已将 Ultralytics DetectionModel 加入 PyTorch 安全列表")
        logger.info("已应用 Ultralytics 非连续权重融合补丁")
    except Exception as exc:
        logger.warning("添加 Ultralytics 安全列表失败: %s", exc)
