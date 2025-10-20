# 贡献指南

感谢您对YOLOv8智能识别系统的关注！我们欢迎各种形式的贡献。

## 如何贡献

### 报告Bug

如果您发现了Bug，请：

1. 检查 [Issues](../../issues) 确保bug未被报告
2. 创建新Issue，包含：
   - 清晰的标题和描述
   - 复现步骤
   - 预期行为和实际行为
   - 截图（如果适用）
   - 环境信息（浏览器版本、操作系统等）

### 提出新功能

如果您有新功能建议：

1. 在Issues中创建Feature Request
2. 清楚地描述功能和用例
3. 等待维护者反馈

### 提交代码

#### 准备工作

1. Fork本仓库
2. 克隆到本地：
   ```bash
   git clone https://github.com/your-username/repo-name.git
   cd repo-name
   ```
3. 创建新分支：
   ```bash
   git checkout -b feature/your-feature-name
   ```

#### 开发

1. 进行代码修改
2. 遵循代码风格指南
3. 添加必要的注释
4. 测试您的更改

#### 提交

1. 提交更改：
   ```bash
   git add .
   git commit -m "feat: 添加XXX功能"
   ```

2. 推送到您的Fork：
   ```bash
   git push origin feature/your-feature-name
   ```

3. 创建Pull Request

## 代码风格

### JavaScript/Vue

- 使用2个空格缩进
- 使用单引号
- 组件名使用PascalCase
- 文件名使用kebab-case

### Python

- 遵循PEP 8
- 使用4个空格缩进
- 函数和变量名使用snake_case
- 类名使用PascalCase

## Commit信息格式

使用语义化提交信息：

```
<type>: <subject>

<body>
```

类型包括：
- `feat`: 新功能
- `fix`: Bug修复
- `docs`: 文档更新
- `style`: 代码格式（不影响功能）
- `refactor`: 重构
- `test`: 测试相关
- `chore`: 构建过程或辅助工具的变动

示例：
```
feat: 添加批量检测功能

- 支持同时上传多个文件
- 显示批量处理进度
- 导出批量结果为ZIP
```

## 开发流程

1. 选择或创建Issue
2. 在Issue下评论表明您要处理此问题
3. Fork并创建分支
4. 开发和测试
5. 提交Pull Request
6. 等待代码审查
7. 根据反馈进行修改
8. 合并

## 测试

在提交PR之前，请确保：

- [ ] 前端可以正常启动
- [ ] 后端API正常工作
- [ ] 所有功能按预期运行
- [ ] 没有控制台错误
- [ ] 代码已格式化

## Pull Request检查清单

- [ ] 代码遵循项目风格
- [ ] 已添加/更新必要的注释
- [ ] 已更新相关文档
- [ ] 已测试新功能/修复
- [ ] Commit信息清晰
- [ ] 没有合并冲突

## 文档

如果您的更改涉及：
- 新功能：更新README.md
- API修改：更新后端文档
- 部署变更：更新DEPLOYMENT.md
- 配置变更：更新相关配置文档

## 获得帮助

如有疑问：
- 查看现有Issues和PRs
- 在Issue中提问
- 查看项目文档

## 行为准则

请保持：
- 尊重和包容
- 建设性的反馈
- 专业的态度

## 许可证

贡献的代码将采用与项目相同的MIT许可证。

再次感谢您的贡献！🎉
