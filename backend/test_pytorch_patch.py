import torch
import torch.nn as nn

from app.core.pytorch_patch import ensure_torch_patch


def test_ensure_torch_patch_allows_fusing_non_contiguous_conv_weights():
    import ultralytics.utils.torch_utils as torch_utils

    ensure_torch_patch()

    conv = nn.Conv2d(3, 4, kernel_size=3, bias=False)
    bn = nn.BatchNorm2d(4)
    conv.weight.data = conv.weight.data.permute(0, 1, 3, 2)
    assert conv.weight.is_contiguous() is False

    fused = torch_utils.fuse_conv_and_bn(conv, bn)

    assert fused is conv
    assert fused.weight.is_contiguous() is True


def test_ensure_torch_patch_updates_ultralytics_tasks_fuse_reference():
    import ultralytics.nn.tasks as ultralytics_tasks
    import ultralytics.utils.torch_utils as torch_utils

    ensure_torch_patch()

    assert ultralytics_tasks.fuse_conv_and_bn is torch_utils.fuse_conv_and_bn
