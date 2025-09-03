# 🚀 Auto-MD

[![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://python.org)
[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

Auto-MD 是一个强大的 CLI 自动化工具，专为开发团队量身打造，旨在简化 Jira 任务管理、Git 工作流和技术文档生成的整个流程。通过智能化的 AI 辅助，让项目管理变得更加高效和规范。

## ✨ 核心特性

🎯 **一键式工作流** - 从 Jira 任务到完整文档，一个命令搞定
📝 **AI 驱动的文档生成** - 智能解析任务信息，生成结构化技术文档
🔄 **无缝 Git 集成** - 自动分支管理和提交推送
📋 **灵活的使用场景** - 支持完整流程或独立功能使用
🎨 **高度可定制** - 自定义提示词模板和文档风格

## 🛠️ 系统要求

| 组件 | 版本要求 | 说明 |
|------|----------|------|
| Python | 3.8+ | 核心运行环境 |
| Git | 任意版本 | 代码版本管理 |
| 网络连接 | - | 用于访问 Jira API |

## 📦 快速开始

### 🏁 三步上手

```bash
# 1️⃣ 获取代码
git clone https://github.com/yourusername/auto-md.git && cd auto-md

# 2️⃣ 安装依赖（推荐使用 uv ⚡）
pip install uv && uv pip install -e .

# 3️⃣ 初始化配置
auto-md init
```

### 🔧 详细安装步骤

<details>
<summary><strong>展开查看详细安装说明</strong></summary>

#### 1️⃣ 获取代码

```bash
git clone https://github.com/yourusername/auto-md.git
cd auto-md
```

#### 2️⃣ 环境配置

**方式一：使用 venv（标准方式）**
```bash
# 创建并激活虚拟环境
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate
```

**方式二：使用 uv（⚡ 推荐）**
```bash
# 安装 uv
pip install uv

# 一键创建环境
uv venv && source .venv/bin/activate  # macOS/Linux
uv venv && .venv\Scripts\activate     # Windows
```

#### 3️⃣ 安装依赖

```bash
# 标准方式
pip install -e .

# 极速方式 ⚡
uv pip install -e .
```

</details>

> 💡 **性能提示**: 使用 `uv` 可将安装速度提升 10-100 倍

## ⚙️ 初始配置

首次使用前，需要配置 Git 和 Jira 的连接信息。Auto-MD 提供了两种配置方式：

### 🎯 交互式配置（推荐）

```bash
auto-md init
```

命令将引导您逐步输入以下信息：

| 配置项 | 说明 | 示例 |
|--------|------|------|
| Git 仓库地址 | 项目代码仓库 URL | `https://github.com/org/repo.git` |
| Git 用户名/密码 | 代码提交凭证 | - |
| Jira 用户名/密码 | API 访问凭证 | - |

### 🚀 快速配置

如果您已知所有配置信息，可以使用命令行参数一次性完成：

```bash
auto-md init \
  --git-url=https://bitbucket.org/example/example.git \
  --git-username=yourname \
  --git-password=yourtoken \
  --jira-username=yourname \
  --jira-password=yourtoken
```

> 🔐 **安全提示**: 建议使用 Personal Access Token 替代明文密码

## 🎮 使用指南

### 💡 获取帮助

```bash
auto-md --help
```

### 🏃‍♂️ 一键式完整流程

执行从 Jira 到 Git 的完整自动化工作流：

```bash
auto-md run DTS-6038
```

**🔄 自动化流程包括：**

```
📥 获取 Jira 任务信息
    ⬇
🌿 智能分支管理
    ⬇
🤖 AI 生成技术文档
    ⬇
📤 提交并推送到远程仓库
```

### 📝 文档生成模式

#### 本地文档生成
仅在当前目录生成任务文档，无 Git 操作：

```bash
auto-md ai-doc DTS-6038
```

#### 项目文档归档
生成文档并自动保存到 `docs/.tasks` 目录：

```bash
auto-md generate-doc DTS-6038
```

> 📍 **使用场景**: 
> - `run`: 完整的团队协作流程
> - `ai-doc`: 快速生成个人参考文档
> - `generate-doc`: 项目文档管理和归档

## 💼 使用案例

### 🎯 典型工作流示例

假设您接到了一个新的 Jira 任务 `DTS-6038`：

```bash
# 完整自动化流程
$ auto-md run DTS-6038

🔍 正在从 Jira 获取任务信息...
✅ 任务信息获取成功: [DTS-6038] 实现用户权限管理模块

🌿 正在处理 Git 分支...
✅ 切换到分支: feature/DTS-6038-user-permission

🤖 正在生成技术文档...
📝 文档生成完成，是否满意当前内容？(y/n): y

📤 正在提交文档...
✅ 文档已成功提交并推送到远程仓库

🎉 任务 DTS-6038 的完整流程已完成！
```

### 📊 生成效果对比

| 原始 Jira 任务 | Auto-MD 生成文档 |
|----------------|------------------|
| 简单的需求描述 | 📋 完整的技术规格说明 |
| 零散的信息点 | 🎯 结构化的实现方案 |
| 缺少技术细节 | 🔧 详细的技术设计文档 |
| 无实施指导 | 📋 清晰的步骤和时间规划 |

## 🤖 AI 文档生成引擎

Auto-MD 的核心优势在于其强大的 AI 文档生成能力，为每个 Jira 任务创建专业的技术文档。

### 🔍 智能信息提取

Auto-MD 会自动：

- 📋 **深度解析** Jira 任务内容（包括父子任务关系）
- 🔗 **关联分析** 相关任务和依赖关系
- 📊 **上下文理解** 项目背景和技术环境

### 🎨 文档生成流程

```
🔍 任务信息分析 → 🤖 AI 内容生成 → 👀 用户审阅 → ✅ 确认保存
```

### 📄 标准文档结构

生成的技术文档包含以下完整章节：

| 章节 | 内容说明 |
|------|----------|
| 📝 **任务概述** | ID、标题、状态、优先级等基础信息 |
| 🎯 **背景分析** | 需求来源、业务价值、解决问题 |
| 🔧 **技术方案** | 实现思路、技术选型、架构设计 |
| 📋 **实施计划** | 详细步骤、时间安排、里程碑 |
| ⚠️  **风险控制** | 潜在问题、预防措施、应急方案 |
| ✅ **验收标准** | 功能要求、性能指标、测试用例 |
| 🔗 **参考资源** | 相关文档、API、工具链接 |

### 🔄 交互式优化

生成文档后，您可以：
- ✏️ 提供修改建议，AI 实时调整
- 🔁 重新生成特定章节
- 📐 自定义文档风格和模板

## ❓ 常见问题

<details>
<summary><strong>🔧 配置相关问题</strong></summary>

**Q: 提示"未初始化配置"错误？**
A: 首次使用需要运行 `auto-md init` 进行配置初始化

**Q: 配置完成后仍无法连接 Jira/Git？**
A: 请检查以下几点：
- 网络连接是否正常
- 用户名密码是否正确
- 是否使用了正确的 API Token
- 重新运行 `auto-md init` 更新配置

**Q: 如何更新已有配置？**
A: 直接重新运行 `auto-md init` 即可覆盖现有配置

</details>

<details>
<summary><strong>📝 文档生成问题</strong></summary>

**Q: AI 生成的文档不符合预期？**
A: 在交互确认环节选择 "n"，然后：
- 提供具体的修改建议
- 描述期望的文档风格
- 指出需要补充的内容

**Q: 如何自定义文档模板？**
A: 编辑 `prompts.text` 文件，修改提示词模板以调整生成风格

**Q: 生成文档缺少某些信息？**
A: 确保 Jira 任务中包含完整信息，或在生成过程中手动补充

</details>

## 🔮 高级定制

### 🎨 自定义提示词模板

编辑 `prompts.text` 文件来个性化文档生成：

```bash
# 查看当前模板
cat prompts.text

# 使用您喜欢的编辑器修改
vim prompts.text
```

### 📚 示例文档库

在 `example/` 目录中添加参考文档，AI 将学习并保持一致的：
- ✨ 文档风格和格式
- 📝 内容组织结构  
- 🎯 技术描述深度

```bash
# 查看现有示例
ls example/
```

## 🤝 参与贡献

我们欢迎各种形式的贡献！

### 🐛 报告问题
- 使用 [GitHub Issues](https://github.com/yourusername/auto-md/issues) 报告 bug
- 提供详细的错误信息和复现步骤

### 💡 功能建议
- 在 Issues 中提交功能请求
- 描述使用场景和期望的行为

### 🔧 代码贡献
- Fork 项目并创建功能分支
- 提交 Pull Request 前请确保代码质量
- 遵循项目的代码风格和规范

## 📄 开源许可

本项目采用 [MIT 许可证](LICENSE)，您可以自由使用、修改和分发。

---

<div align="center">

**⭐ 如果这个项目对您有帮助，请给我们一个 Star！**

[🐛 报告问题](https://github.com/yourusername/auto-md/issues) · [💡 功能建议](https://github.com/yourusername/auto-md/issues) · [📖 文档](https://github.com/yourusername/auto-md)

</div>