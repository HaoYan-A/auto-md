"""CLI命令入口模块。"""

import os
import click
from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from rich.markdown import Markdown
import time
import subprocess
from pathlib import Path
from .config import save_config, load_config, CONFIG_FILE, is_initialized
from .jira_api import get_issue, get_parent_issue
from .git_utils import (
    create_temp_dir, clone_repo, find_branch_for_issue, checkout_branch, 
    cleanup_temp_dir, create_branch_for_issue, get_default_branch
)
from .ai_utils import (
    generate_task_document, display_markdown, save_markdown_to_file
)

console = Console()

@click.group()
@click.version_option()
def cli():
    """Auto-MD CLI工具。"""
    pass

@cli.command()
@click.argument("name", default="世界")
def hello(name):
    """向指定用户问好。"""
    console.print(f"[bold green]你好，{name}！[/bold green]")

@cli.command()
@click.option("--git-url", prompt="Git仓库地址", help="Git仓库地址，例如：https://bitbucket.org/example/example.git")
@click.option("--git-username", prompt="Git用户名", help="Git用户名")
@click.option("--git-password", prompt="Git密码", hide_input=True, help="Git密码")
@click.option("--jira-username", prompt="Jira用户名", help="Jira用户名")
@click.option("--jira-password", prompt="Jira密码", hide_input=True, help="Jira密码")
def init(git_url, git_username, git_password, jira_username, jira_password):
    """初始化配置，收集Git和Jira信息。"""
    # 加载现有配置（如果有的话）
    config = load_config()
    
    # 更新Git配置
    config["git"] = {
        "url": git_url,
        "username": git_username,
        "password": git_password
    }
    
    # 更新Jira配置
    config["jira"] = {
        "username": jira_username,
        "password": jira_password
    }
    
    # 保存配置
    save_config(config)
    console.print("[bold green]配置已成功保存！[/bold green]")
    console.print(f"配置文件位置: [cyan]{CONFIG_FILE}[/cyan]")
    
    # 显示当前配置信息
    console.print("\n[bold]当前Git配置信息：[/bold]")
    console.print(f"  仓库地址: [cyan]{git_url}[/cyan]")
    console.print(f"  用户名: [cyan]{git_username}[/cyan]")
    console.print(f"  密码: [cyan]{'*' * len(git_password)}[/cyan]")
    
    console.print("\n[bold]当前Jira配置信息：[/bold]")
    console.print(f"  用户名: [cyan]{jira_username}[/cyan]")
    console.print(f"  密码: [cyan]{'*' * len(jira_password)}[/cyan]")

@cli.command()
@click.argument("issue_key")
def run(issue_key):
    """执行完整的任务流程。
    
    包括：
    1. 从Jira获取问题信息
    2. 管理Git分支（查找或创建）
    3. 在代码目录中生成任务文档
    4. 提交文档到Git仓库
    
    Args:
        issue_key: Jira问题键，例如 'DTS-6038'。
    """
    # 检查是否已初始化
    if not is_initialized():
        console.print("[bold red]错误: 未初始化配置，请先运行 'auto-md init' 命令[/bold red]")
        return
    
    console.print(f"[bold]开始处理Jira问题: {issue_key}[/bold]")
    
    # 步骤1: 从Jira获取问题信息
    with console.status(f"[bold blue]正在获取Jira问题信息: {issue_key}...[/bold blue]"):
        issue = get_issue(issue_key)
    
    if not issue:
        console.print(f"[bold red]错误: 无法获取Jira问题 {issue_key} 的信息[/bold red]")
        return
    
    # 显示问题信息
    display_issue_info(issue)
    
    # 步骤2: 如果有父问题，获取父问题信息
    parent_issue = None
    parent_info = ""
    if "fields" in issue and "parent" in issue["fields"]:
        parent_key = issue["fields"]["parent"]["key"]
        with console.status(f"[bold blue]正在获取父问题信息: {parent_key}...[/bold blue]"):
            parent_issue = get_parent_issue(issue)
        
        if parent_issue:
            console.print(f"\n[bold]父问题信息:[/bold]")
            display_issue_info(parent_issue)
            
            # 准备父任务信息文本
            parent_fields = parent_issue["fields"]
            parent_summary = parent_fields.get("summary", "无标题")
            parent_description = parent_fields.get("description", "无描述")
            parent_info = f"""父任务信息:
父任务ID: {parent_issue.get('key')}
父任务标题: {parent_summary}
父任务描述: {parent_description}
"""
    
    # 步骤3: 克隆Git仓库
    with console.status("[bold blue]正在准备Git仓库...[/bold blue]"):
        temp_dir = create_temp_dir()
        clone_success = clone_repo(temp_dir)
    
    if not clone_success:
        console.print("[bold red]错误: 克隆Git仓库失败[/bold red]")
        cleanup_temp_dir(temp_dir)
        return
    
    # 步骤4: 查找与问题关联的分支
    with console.status(f"[bold blue]正在查找与问题 {issue_key} 相关的分支...[/bold blue]"):
        branches = find_branch_for_issue(temp_dir, issue_key)
    
    branch_used = None
    parent_key = None
    if not branches:
        console.print(f"[bold yellow]未找到与问题 {issue_key} 相关的分支[/bold yellow]")
        # 尝试使用父问题查找
        if parent_issue:
            parent_key = parent_issue["key"]
            with console.status(f"[bold blue]正在查找与父问题 {parent_key} 相关的分支...[/bold blue]"):
                branches = find_branch_for_issue(temp_dir, parent_key)
            
            if branches:
                console.print(f"[bold green]找到与父问题 {parent_key} 相关的分支:[/bold green]")
                for branch in branches:
                    console.print(f"  - [cyan]{branch}[/cyan]")
            else:
                console.print(f"[bold yellow]未找到与父问题 {parent_key} 相关的分支[/bold yellow]")
    else:
        console.print(f"[bold green]找到与问题 {issue_key} 相关的分支:[/bold green]")
        for branch in branches:
            console.print(f"  - [cyan]{branch}[/cyan]")
    
    # 如果找到了分支，询问用户是否需要检出
    if branches:
        if len(branches) == 1:
            branch = branches[0]
            if click.confirm(f"是否检出分支 {branch}？", default=True):
                if checkout_branch(branch):
                    console.print(f"[bold green]成功检出分支: {branch}[/bold green]")
                    branch_used = branch.replace("origin/", "")
                else:
                    console.print(f"[bold red]检出分支失败: {branch}[/bold red]")
        else:
            # 如果找到多个分支，让用户选择
            branch_options = "\n".join([f"{i+1}. {b}" for i, b in enumerate(branches)])
            console.print(f"找到多个相关分支:\n{branch_options}")
            branch_idx = click.prompt("请选择要检出的分支编号", type=int, default=1)
            if 1 <= branch_idx <= len(branches):
                branch = branches[branch_idx - 1]
                if checkout_branch(branch):
                    console.print(f"[bold green]成功检出分支: {branch}[/bold green]")
                    branch_used = branch.replace("origin/", "")
                else:
                    console.print(f"[bold red]检出分支失败: {branch}[/bold red]")
            else:
                console.print("[bold red]无效的分支编号[/bold red]")
    else:
        # 未找到分支，询问是否创建新分支
        create_new = click.confirm(f"未找到相关分支，是否为问题 {issue_key} 创建新分支？", default=True)
        if create_new:
            # 固定使用release作为基础分支
            base_branch = "release"
            console.print(f"[bold blue]将使用 {base_branch} 作为基础分支创建新分支...[/bold blue]")
            
            # 创建新分支
            success, new_branch = create_branch_for_issue(issue_key, base_branch)
            if success:
                console.print(f"[bold green]已成功从 {base_branch} 创建并检出新分支: {new_branch}[/bold green]")
                branch_used = new_branch
            else:
                console.print(f"[bold red]创建分支失败[/bold red]")
    
    # 步骤5: 在代码目录中查找或创建docs/.tasks目录
    if branch_used:
        tasks_dir = Path(temp_dir) / "docs" / ".tasks"
        if not tasks_dir.exists():
            os.makedirs(tasks_dir, exist_ok=True)
            console.print(f"[bold green]已创建目录: docs/.tasks[/bold green]")
        
        # 步骤6: 生成AI文档
        fields = issue["fields"]
        summary = fields.get("summary", "无标题")
        description = fields.get("description", "无描述")
        status_name = fields.get("status", {}).get("name", "未知状态")
        assignee = fields.get("assignee", {}).get("displayName", "未分配")
        
        console.print("\n[bold]开始生成任务文档...[/bold]")
        
        chat_history = []
        doc_file_path = None
        while True:
            with console.status("[bold blue]AI正在生成任务文档...[/bold blue]"):
                result = generate_task_document(
                    issue_key, 
                    summary, 
                    description, 
                    status_name, 
                    assignee,
                    parent_info,
                    chat_history
                )
            
            console.print("\n[bold]AI生成的任务文档：[/bold]")
            display_markdown(result.content)
            
            # 询问用户是否满意
            satisfied = click.prompt(
                "\n您对生成的文档满意吗？ (y/n)",
                type=str,
                default="y"
            ).lower() == "y"
            
            if satisfied:
                # 保存文档到git目录中的docs/.tasks
                doc_file_path = tasks_dir / f"{issue_key}.md"
                with open(doc_file_path, "w", encoding="utf-8") as f:
                    f.write(result.content)
                console.print(f"[bold green]文档已保存至: {doc_file_path}[/bold green]")
                break
            else:
                # 收集用户反馈
                feedback = click.prompt("请提供您的修改建议", type=str)
                chat_history.append(("human", f"我对生成的文档有以下修改建议：{feedback}"))
                chat_history.append(("assistant", "我会根据您的反馈重新生成文档。"))
                console.print("[bold blue]正在根据反馈重新生成...[/bold blue]")
        
        # 步骤7: 询问是否提交并推送
        if doc_file_path and click.confirm("是否提交并推送文档到远程仓库？", default=True):
            try:
                # 切换到git目录
                os.chdir(temp_dir)
                
                # 添加文件
                subprocess.run(
                    ["git", "add", str(doc_file_path.relative_to(temp_dir))],
                    capture_output=True,
                    text=True,
                    check=True
                )
                
                # 提交更改
                commit_message = f"docs: 添加{issue_key}任务文档"
                subprocess.run(
                    ["git", "commit", "-m", commit_message],
                    capture_output=True,
                    text=True,
                    check=True
                )
                
                # 推送到远程
                subprocess.run(
                    ["git", "push", "-u", "origin", branch_used],
                    capture_output=True,
                    text=True,
                    check=True
                )
                
                console.print(f"[bold green]文档已成功提交并推送到分支: {branch_used}[/bold green]")
            except subprocess.CalledProcessError as e:
                console.print(f"[bold red]提交或推送失败: {e.stderr}[/bold red]")
    
    # 询问是否清理临时目录
    if click.confirm("是否清理临时目录？", default=True):
        cleanup_temp_dir(temp_dir)
    else:
        console.print(f"[bold]临时目录位置: {temp_dir}[/bold]")
        console.print("[yellow]注意: 请在完成工作后手动删除此目录[/yellow]")

@cli.command()
@click.argument("issue_key")
def ai_doc(issue_key):
    """在当前目录生成任务文档。
    
    该命令会：
    1. 从Jira获取问题信息（包括父任务）
    2. 使用AI生成任务文档
    3. 将文档保存在当前工作目录
    
    Args:
        issue_key: Jira问题键，例如 'DTS-6038'。
    """
    # 检查是否已初始化
    if not is_initialized():
        console.print("[bold red]错误: 未初始化配置，请先运行 'auto-md init' 命令[/bold red]")
        return
    
    console.print(f"[bold]开始处理Jira问题: {issue_key}[/bold]")
    
    # 从Jira获取问题信息
    with console.status(f"[bold blue]正在获取Jira问题信息: {issue_key}...[/bold blue]"):
        issue = get_issue(issue_key)
    
    if not issue:
        console.print(f"[bold red]错误: 无法获取Jira问题 {issue_key} 的信息[/bold red]")
        return
    
    # 显示问题信息
    display_issue_info(issue)
    
    # 获取父问题信息
    parent_issue = None
    parent_info = ""
    if "fields" in issue and "parent" in issue["fields"]:
        parent_key = issue["fields"]["parent"]["key"]
        with console.status(f"[bold blue]正在获取父问题信息: {parent_key}...[/bold blue]"):
            parent_issue = get_parent_issue(issue)
        
        if parent_issue:
            console.print(f"\n[bold]父问题信息:[/bold]")
            display_issue_info(parent_issue)
            
            # 准备父任务信息文本
            parent_fields = parent_issue["fields"]
            parent_summary = parent_fields.get("summary", "无标题")
            parent_description = parent_fields.get("description", "无描述")
            parent_info = f"""父任务信息:
父任务ID: {parent_issue.get('key')}
父任务标题: {parent_summary}
父任务描述: {parent_description}
"""
    
    # 提取问题信息
    fields = issue["fields"]
    summary = fields.get("summary", "无标题")
    description = fields.get("description", "无描述")
    status_name = fields.get("status", {}).get("name", "未知状态")
    assignee = fields.get("assignee", {}).get("displayName", "未分配")
    
    console.print("\n[bold]开始生成AI任务文档...[/bold]")
    
    chat_history = []
    while True:
        with console.status("[bold blue]AI正在生成任务文档...[/bold blue]"):
            result = generate_task_document(
                issue_key, 
                summary, 
                description, 
                status_name, 
                assignee,
                parent_info,
                chat_history
            )
        
        console.print("\n[bold]AI生成的任务文档：[/bold]")
        display_markdown(result.content)
        
        # 询问用户是否满意
        satisfied = click.prompt(
            "\n您对生成的文档满意吗？ (y/n)",
            type=str,
            default="y"
        ).lower() == "y"
        
        if satisfied:
            # 保存文档到当前目录
            file_path = Path(f"{issue_key}.md")
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(result.content)
            console.print(f"[bold green]文档已保存至当前目录: {file_path.absolute()}[/bold green]")
            break
        else:
            # 收集用户反馈
            feedback = click.prompt("请提供您的修改建议", type=str)
            chat_history.append(("human", f"我对生成的文档有以下修改建议：{feedback}"))
            chat_history.append(("assistant", "我会根据您的反馈重新生成文档。"))
            console.print("[bold blue]正在根据反馈重新生成...[/bold blue]")

@cli.command()
@click.argument("issue_key")
def generate_doc(issue_key):
    """生成任务文档并保存到docs/.tasks目录。
    
    该命令会：
    1. 从Jira获取问题信息（包括父任务） 
    2. 使用AI生成任务文档
    3. 将文档保存到docs/.tasks目录
    
    Args:
        issue_key: Jira问题键，例如 'DTS-6038'。
    """
    # 检查是否已初始化
    if not is_initialized():
        console.print("[bold red]错误: 未初始化配置，请先运行 'auto-md init' 命令[/bold red]")
        return
    
    console.print(f"[bold]开始处理Jira问题: {issue_key}[/bold]")
    
    # 从Jira获取问题信息
    with console.status(f"[bold blue]正在获取Jira问题信息: {issue_key}...[/bold blue]"):
        issue = get_issue(issue_key)
    
    if not issue:
        console.print(f"[bold red]错误: 无法获取Jira问题 {issue_key} 的信息[/bold red]")
        return
    
    # 显示问题信息
    display_issue_info(issue)
    
    # 获取父问题信息
    parent_issue = None
    parent_info = ""
    if "fields" in issue and "parent" in issue["fields"]:
        parent_key = issue["fields"]["parent"]["key"]
        with console.status(f"[bold blue]正在获取父问题信息: {parent_key}...[/bold blue]"):
            parent_issue = get_parent_issue(issue)
        
        if parent_issue:
            console.print(f"\n[bold]父问题信息:[/bold]")
            display_issue_info(parent_issue)
            
            # 准备父任务信息文本
            parent_fields = parent_issue["fields"]
            parent_summary = parent_fields.get("summary", "无标题")
            parent_description = parent_fields.get("description", "无描述")
            parent_info = f"""父任务信息:
父任务ID: {parent_issue.get('key')}
父任务标题: {parent_summary}
父任务描述: {parent_description}
"""
    
    # 提取问题信息
    fields = issue["fields"]
    summary = fields.get("summary", "无标题")
    description = fields.get("description", "无描述")
    status_name = fields.get("status", {}).get("name", "未知状态")
    assignee = fields.get("assignee", {}).get("displayName", "未分配")
    
    console.print("\n[bold]开始生成AI任务文档...[/bold]")
    
    chat_history = []
    while True:
        with console.status("[bold blue]AI正在生成任务文档...[/bold blue]"):
            result = generate_task_document(
                issue_key, 
                summary, 
                description, 
                status_name, 
                assignee,
                parent_info,
                chat_history
            )
        
        console.print("\n[bold]AI生成的任务文档：[/bold]")
        display_markdown(result.content)
        
        # 询问用户是否满意
        satisfied = click.prompt(
            "\n您对生成的文档满意吗？ (y/n)",
            type=str,
            default="y"
        ).lower() == "y"
        
        if satisfied:
            # 保存文档 - 确保保存的是纯Markdown内容而不是对象
            file_path = save_markdown_to_file(issue_key, result.content)
            console.print(f"[bold green]文档已保存至: {file_path}[/bold green]")
            break
        else:
            # 收集用户反馈
            feedback = click.prompt("请提供您的修改建议", type=str)
            chat_history.append(("human", f"我对生成的文档有以下修改建议：{feedback}"))
            chat_history.append(("assistant", "我会根据您的反馈重新生成文档。"))
            console.print("[bold blue]正在根据反馈重新生成...[/bold blue]")

def display_issue_info(issue):
    """显示Jira问题信息。"""
    if not issue or "fields" not in issue:
        return
    
    fields = issue["fields"]
    summary = fields.get("summary", "无标题")
    description = fields.get("description", "无描述")
    status_name = fields.get("status", {}).get("name", "未知状态")
    assignee = fields.get("assignee", {}).get("displayName", "未分配")
    
    console.print(Panel(
        f"[bold cyan]Key:[/bold cyan] {issue.get('key')}\n"
        f"[bold cyan]标题:[/bold cyan] {summary}\n"
        f"[bold cyan]状态:[/bold cyan] {status_name}\n"
        f"[bold cyan]分配给:[/bold cyan] {assignee}\n\n"
        f"[bold cyan]描述:[/bold cyan]\n{Markdown(description) if description else '无描述'}",
        title=f"Jira问题: {issue.get('key')}",
        expand=False
    ))

def main():
    """CLI入口点。"""
    cli() 