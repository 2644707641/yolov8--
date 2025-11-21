# Repository Guidelines

## 项目结构与模块
- 源码：请根据仓库实际结构补充（示例：src/ 保存模型与推理脚本，notebooks/ 存放实验记录）。
- 数据与资产：data/ 或 assets/ 用于数据、权重与可视化资源；检查大文件是否受 .gitignore 管理。
- 测试：tests/（或同级 *_test.py）集中单元/集成测试；scripts/ 存放辅助工具。

## 构建、运行与测试
- 安装依赖：pip install -r requirements.txt（若有 GPU 需求，确认 CUDA 对应版本）。
- 训练/推理示例：python main.py --config configs/example.yaml（根据仓库实际命令调整）。
- 运行测试：pytest 或 pytest tests/；如有 lint，执行 uff check 或 lake8。
- 格式化：lack .（若使用）；提交前建议 lack . && pytest。

## 代码风格与命名
- Python：4 空格缩进，行宽 88-100；遵循 PEP8。模块/文件用 snake_case，类用 PascalCase，常量全大写。
- 函数/变量使用描述性 snake_case，避免缩写；临时脚本放入 scripts/ 并添加 README 注释用法。
- 导入顺序：标准库 | 第三方 | 本地模块，保持分类空行；删除未使用导入。

## 测试规范
- 优先编写单元测试，关键路径需有覆盖；对模型推理提供小样本或 mock 数据。
- 测试命名：文件 	est_*.py，函数 	est_<行为>；使用 fixtures 复用测试资源。
- 覆盖率：如有阈值（示例 80%），在 CI 中验证；本地可运行 pytest --cov。

## 提交与合并
- 提交信息：建议遵循 <type>(scope): subject（常见 type 如 feat/fix/docs/refactor/test）。
- 每个 PR：描述变更、动机与结果；链接相关 issue，若涉及可视化/界面请附截图或日志。
- 确保 CI/Lint/Test 通过；包含复现步骤和配置（如模型权重、设备信息）。

## 安全与配置提示
- 不要提交私有数据、API 密钥或大模型权重；使用 .env 并在 README 指出所需变量。
- 确认 .gitignore 覆盖中间产物（logs、checkpoints、__pycache__ 等）。
