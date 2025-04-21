# Auto-MD

Auto-MD是一个基于CLI的工具，用于自动化获取Jira任务信息、管理Git分支和生成任务文档。

## 系统要求

- Python 3.8+
- Git
- 网络连接（用于访问Jira API）

## 从零开始安装

### 1. 克隆仓库

```bash
git clone https://github.com/yourusername/auto-md.git
cd auto-md
```

### 2. 创建并激活虚拟环境

#### 使用venv（标准方式）
```bash
# 创建虚拟环境
python -m venv .venv

# 激活虚拟环境（Windows）
.venv\Scripts\activate

# 激活虚拟环境（macOS/Linux）
source .venv/bin/activate
```

#### 使用uv（推荐，更快）
```bash
# 安装uv工具（如果尚未安装）
pip install uv

# 创建虚拟环境
uv venv

# 激活虚拟环境（与venv相同方式）
```

### 3. 安装项目

```bash
# 使用标准pip
pip install -e .

# 或使用uv（推荐）
uv pip install -e .
```

## 配置

首次使用前，需要初始化配置，提供Git和Jira的相关信息：

```bash
auto-md init
```

此命令将引导您输入以下信息：
- Git仓库地址
- Git用户名
- Git密码
- Jira用户名
- Jira密码

您也可以通过命令行参数直接提供这些信息：

```bash
auto-md init --git-url=https://bitbucket.org/example/example.git --git-username=username --git-password=password --jira-username=username --jira-password=password
```

## 使用指南

### 查看帮助信息

```bash
auto-md --help
```

### 执行完整的任务流程

此命令会从Jira获取任务信息，管理Git分支，生成文档并提交到仓库：

```bash
auto-md run DTS-6038
```

执行过程包括：
1. 从Jira获取问题信息
2. 查找或创建相关Git分支
3. 生成任务文档
4. 提交并推送文档

### 仅在当前目录生成任务文档

如果只想生成任务文档，不需要Git操作：

```bash
auto-md ai-doc DTS-6038
```

### 生成任务文档并保存到特定目录

生成文档并保存到项目的`docs/.tasks`目录：

```bash
auto-md generate-doc DTS-6038
```

## 文档生成功能

所有文档生成命令都会：
1. 从Jira获取任务信息（包括父任务，如果存在）
2. 使用AI生成格式规范的Markdown文档
3. 允许您提供反馈并重新生成文档
4. 保存文档到指定位置

生成的文档包含以下部分：
- 任务描述（任务ID、标题、状态等）
- 背景信息
- 技术要求
- 实现步骤
- 注意事项
- 验收标准
- 相关资源

## 常见问题

### 配置问题

**问题**: "未初始化配置"错误
**解决方案**: 运行`auto-md init`命令初始化配置

**问题**: 配置后无法连接到Jira/Git
**解决方案**: 检查网络连接和凭证信息，重新运行`auto-md init`

### 文档生成问题

**问题**: AI生成文档不符合预期
**解决方案**: 在交互过程中选择"n"并提供具体修改建议

## 高级用法

### 自定义提示词

您可以修改`prompts.text`文件中的提示词模板，自定义文档生成风格和内容。

### 添加示例文档

在`example`目录下添加示例Markdown文件，AI会参考这些示例生成格式和风格一致的文档。

## 贡献指南

欢迎提交Pull Request或Issue来改进此项目。

## 许可证

[MIT License](LICENSE)