"""AI工具模块，用于生成任务相关的Markdown文档。"""

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from pydantic import BaseModel, Field
from rich.markdown import Markdown
from rich.console import Console
from typing import List, Optional, Dict
import os
import glob
import re
from pathlib import Path

console = Console()

def load_prompts_from_file(file_path="prompts.text"):
    """从文件加载提示词。
    
    Args:
        file_path: 提示词文件路径。
        
    Returns:
        包含各类提示词的字典。
    """
    if not os.path.exists(file_path):
        console.print(f"[bold red]警告: 找不到提示词文件: {file_path}[/bold red]")
        return {}
    
    prompts = {}
    current_section = None
    current_content = []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.rstrip()
            # 检查是否是新的提示词部分
            if line.startswith('## '):
                # 保存前一个部分
                if current_section:
                    prompts[current_section] = '\n'.join(current_content)
                # 开始新的部分
                current_section = line[3:].strip()
                current_content = []
            elif line.startswith('# '):
                # 忽略顶级标题
                continue
            elif current_section:
                current_content.append(line)
    
    # 保存最后一个部分
    if current_section and current_content:
        prompts[current_section] = '\n'.join(current_content)
    
    return prompts

def load_examples_from_dir(dir_path="example"):
    """从目录加载示例文档。
    
    Args:
        dir_path: 示例文档目录路径。
        
    Returns:
        示例文档内容列表。
    """
    examples = []
    if not os.path.exists(dir_path):
        console.print(f"[bold red]警告: 找不到示例目录: {dir_path}[/bold red]")
        return examples
    
    # 获取所有Markdown文件
    md_files = glob.glob(os.path.join(dir_path, "*.md"))
    for file_path in md_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                examples.append({
                    "file_name": os.path.basename(file_path),
                    "content": content
                })
        except Exception as e:
            console.print(f"[bold red]读取示例文件 {file_path} 时出错: {e}[/bold red]")
    
    return examples

# 加载提示词和示例
PROMPTS = load_prompts_from_file()
EXAMPLES = load_examples_from_dir()

def get_examples_text():
    """获取示例文本，避免在f-string中直接使用可能包含反斜杠的内容。"""
    examples_text = ""
    for i, ex in enumerate(EXAMPLES):
        examples_text += f"示例 {i+1}:\n```\n{ex['content']}\n```\n\n"
    return examples_text

# 创建一个基本的任务提示模板，使用加载的提示词
task_prompt_template = ChatPromptTemplate.from_messages([
    ("system", f"""你是一个专业的任务分析助手，可以根据Jira任务信息生成详细的任务说明文档。
{PROMPTS.get('任务分析提示词', '')}

以下是一些示例文档格式供你参考:
{get_examples_text()}

返回的格式必须包括:
- title: 文档标题
- sections: 包含多个章节的数组，每个章节有title和content字段
- content: 完整的Markdown文档内容字符串
"""),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", """任务信息：
任务ID: {issue_key}
任务标题: {summary}
任务描述: {description}
任务状态: {status}
任务分配: {assignee}

{parent_info}

请根据上述信息，生成一个清晰、详细的Markdown格式任务文档。"""),
])

class Section(BaseModel):
    """表示文档中的一个章节。"""
    title: str = Field(description="章节标题")
    content: str = Field(description="章节内容")

class MarkdownDocument(BaseModel):
    """用于表示Markdown文档的结构化输出。"""
    title: str = Field(description="文档的标题")
    sections: List[Section] = Field(description="文档的各个章节，每个章节包含标题和内容")
    content: str = Field(description="完整的Markdown文档内容")

def create_ai_client():
    """创建AI客户端。"""
    return ChatOpenAI(
        model="gpt-4.1-mini",
        base_url="https://aihubmix.com/v1",
        api_key="sk-WukkvRTb68Al3Ap46618E82305734043AfAf7aDc14A184Cc"
    )

def generate_task_document(issue_key, summary, description, status, assignee, parent_info="", chat_history=None):
    """生成任务文档。

    Args:
        issue_key: Jira问题键。
        summary: 问题摘要。
        description: 问题描述。
        status: 问题状态。
        assignee: 任务分配者。
        parent_info: 父任务信息（如果有）。
        chat_history: 聊天历史记录（用于再生成时传递用户反馈）。

    Returns:
        生成的Markdown格式文档。
    """
    chat_history = chat_history or []
    
    # 更新提示词，明确强调需要纯Markdown格式
    updated_task_prompt = ChatPromptTemplate.from_messages([
        ("system", f"""你是一个专业的任务分析助手，可以根据Jira任务信息生成详细的任务说明文档。
{PROMPTS.get('任务分析提示词', '')}

以下是一些示例文档格式供你参考:
{get_examples_text()}

重要：请直接输出纯Markdown格式文档，不要输出JSON或其他结构化数据。
请遵循以下章节结构：
1. 使用一级标题(#)作为文档标题
2. 使用二级标题(##)作为各节标题，如"任务描述"、"背景信息"、"技术要求"等
3. 确保格式与示例一致
"""),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", """任务信息：
任务ID: {issue_key}
任务标题: {summary}
任务描述: {description}
任务状态: {status}
任务分配: {assignee}

{parent_info}

请根据上述信息，生成一个清晰、详细的Markdown格式任务文档。记住，请直接输出纯Markdown格式，不要包含任何JSON或其他结构。"""),
    ])
    
    # 创建LLM链
    llm = create_ai_client()
    
    # 使用普通输出解析器
    output_parser = StrOutputParser()
    
    # 构建文本生成流程
    text_chain = updated_task_prompt | llm | output_parser
    
    # 生成结果 - 纯Markdown文本
    markdown_content = text_chain.invoke({
        "issue_key": issue_key,
        "summary": summary,
        "description": description,
        "status": status,
        "assignee": assignee,
        "parent_info": parent_info,
        "chat_history": chat_history
    })
    
    # 为了保持接口兼容性，仍然创建MarkdownDocument对象
    # 但确保里面存储的是纯Markdown文本
    sections = []
    
    # 从Markdown文本中提取章节
    lines = markdown_content.split('\n')
    current_section = None
    current_content = []
    
    for line in lines:
        # 检测一级和二级标题
        if line.startswith('# '):
            # 如果有正在处理的章节，保存它
            if current_section:
                sections.append(Section(
                    title=current_section,
                    content='\n'.join(current_content)
                ))
            # 记录新章节标题，去掉"# "前缀
            current_section = line[2:].strip()
            current_content = []
        elif line.startswith('## '):
            # 如果有正在处理的章节，保存它
            if current_section:
                sections.append(Section(
                    title=current_section,
                    content='\n'.join(current_content)
                ))
            # 记录新章节标题，去掉"## "前缀
            current_section = line[3:].strip()
            current_content = []
        else:
            # 将行添加到当前章节内容中
            current_content.append(line)
    
    # 保存最后一个章节
    if current_section:
        sections.append(Section(
            title=current_section,
            content='\n'.join(current_content)
        ))
    
    # 如果没有提取到章节，创建一个默认章节
    if not sections:
        sections.append(Section(
            title="任务详情",
            content=markdown_content
        ))
    
    # 从第一个章节标题或任务摘要中提取文档标题
    doc_title = sections[0].title if sections else f"{issue_key} - {summary}"
    
    # 创建MarkdownDocument对象
    document = MarkdownDocument(
        title=doc_title,
        sections=sections,
        content=markdown_content  # 这里存储的是纯Markdown文本
    )
    
    return document

def display_markdown(markdown_content):
    """在终端中显示Markdown内容。

    Args:
        markdown_content: Markdown格式的文本。
    """
    md = Markdown(markdown_content)
    console.print(md)

def save_markdown_to_file(issue_key, markdown_content):
    """将Markdown内容保存到文件。

    Args:
        issue_key: Jira问题键，用作文件名。
        markdown_content: 要保存的Markdown内容。

    Returns:
        保存的文件路径。
    """
    # 确保目录存在
    tasks_dir = Path("docs/.tasks")
    os.makedirs(tasks_dir, exist_ok=True)
    
    # 创建文件路径
    file_path = tasks_dir / f"{issue_key}.md"
    
    # 写入文件
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(markdown_content)
    
    return file_path 