"""Git操作工具模块。"""

import os
import shutil
import tempfile
import subprocess
import urllib.parse
from pathlib import Path
from rich.console import Console
from .config import get_git_config

console = Console()

def create_temp_dir():
    """创建临时目录。
    
    Returns:
        临时目录路径。
    """
    temp_dir = Path(tempfile.mkdtemp(prefix="auto-md-"))
    return temp_dir

def clone_repo(temp_dir):
    """克隆Git仓库到临时目录。
    
    Args:
        temp_dir: 临时目录路径。
        
    Returns:
        成功返回True，失败返回False。
    """
    git_config = get_git_config()
    repo_url = git_config.get("url")
    username = git_config.get("username")
    password = git_config.get("password")
    
    if not repo_url or not username or not password:
        raise ValueError("未配置Git仓库信息，请先运行 'auto-md init' 命令")
    
    try:
        console.print(f"[bold]克隆仓库到临时目录: {temp_dir}[/bold]")
        
        # 方法一：使用URL编码的认证信息
        # 例如: https://username:password@bitbucket.org/path/repo.git
        try:
            url_parts = repo_url.split("://")
            if len(url_parts) != 2:
                console.print(f"[bold red]Git仓库URL格式不正确: {repo_url}[/bold red]")
                return False
            
            # 对用户名和密码进行URL编码，确保特殊字符能够正确处理
            encoded_username = urllib.parse.quote(username, safe='')
            encoded_password = urllib.parse.quote(password, safe='')
            auth_url = f"{url_parts[0]}://{encoded_username}:{encoded_password}@{url_parts[1]}"
            
            result = subprocess.run(
                ["git", "clone", auth_url, str(temp_dir)],
                capture_output=True,
                text=True,
                check=True
            )
            return True
        except subprocess.CalledProcessError as e:
            console.print(f"[bold yellow]URL认证方式克隆失败，尝试使用凭据参数方式...[/bold yellow]")
            
            # 方法二：使用命令行参数指定凭据
            result = subprocess.run(
                [
                    "git", "clone", 
                    repo_url, str(temp_dir),
                    "--config", f"credential.username={username}",
                    "--config", f"credential.helper=!echo password={password}; echo"
                ],
                capture_output=True,
                text=True,
                check=True
            )
            return True
    except subprocess.CalledProcessError as e:
        console.print(f"[bold red]克隆仓库失败: {e.stderr}[/bold red]")
        return False

def find_branch_for_issue(temp_dir, issue_key):
    """寻找与问题关联的分支。
    
    Args:
        temp_dir: 仓库临时目录路径。
        issue_key: 问题键，例如 'DTS-6038'。
        
    Returns:
        相关分支名称列表。
    """
    try:
        # 切换到仓库目录
        os.chdir(temp_dir)
        
        # 获取远程分支列表
        result = subprocess.run(
            ["git", "branch", "-r"],
            capture_output=True,
            text=True,
            check=True
        )
        
        branches = result.stdout.strip().split("\n")
        matching_branches = [
            branch.strip() for branch in branches
            if issue_key.lower() in branch.lower()
        ]
        
        return matching_branches
    except subprocess.CalledProcessError as e:
        console.print(f"[bold red]查找分支失败: {e.stderr}[/bold red]")
        return []

def checkout_branch(branch_name):
    """检出指定分支。
    
    Args:
        branch_name: 分支名称。
        
    Returns:
        成功返回True，失败返回False。
    """
    # 如果分支名包含 'origin/'，需要创建本地分支
    if branch_name.startswith("origin/"):
        local_branch = branch_name.replace("origin/", "")
        try:
            subprocess.run(
                ["git", "checkout", "-b", local_branch, branch_name],
                capture_output=True,
                text=True,
                check=True
            )
            return True
        except subprocess.CalledProcessError as e:
            console.print(f"[bold red]检出分支失败: {e.stderr}[/bold red]")
            return False
    else:
        try:
            subprocess.run(
                ["git", "checkout", branch_name],
                capture_output=True,
                text=True,
                check=True
            )
            return True
        except subprocess.CalledProcessError as e:
            console.print(f"[bold red]检出分支失败: {e.stderr}[/bold red]")
            return False

def create_branch_for_issue(issue_key, base_branch="release"):
    """为Jira问题创建新的分支。
    
    Args:
        issue_key: Jira问题键，例如 'DTS-6038'。
        base_branch: 基础分支，默认为release。
        
    Returns:
        成功返回(True, 新分支名)，失败返回(False, None)。
    """
    try:
        # 先确保基础分支是最新的
        console.print(f"[bold]更新基础分支 {base_branch}...[/bold]")
        subprocess.run(
            ["git", "checkout", base_branch],
            capture_output=True,
            text=True,
            check=True
        )
        
        subprocess.run(
            ["git", "pull"],
            capture_output=True,
            text=True,
            check=True
        )
        
        # 创建新分支，直接使用问题键作为分支名
        new_branch = f"{issue_key}"
        console.print(f"[bold]创建新分支: {new_branch}[/bold]")
        
        subprocess.run(
            ["git", "checkout", "-b", new_branch],
            capture_output=True,
            text=True,
            check=True
        )
        
        return True, new_branch
    except subprocess.CalledProcessError as e:
        console.print(f"[bold red]创建分支失败: {e.stderr}[/bold red]")
        return False, None

def get_default_branch():
    """获取仓库的默认分支（通常是master或main）。
    
    Returns:
        默认分支名称，如果无法确定则返回'master'。
    """
    try:
        # 获取远程默认分支
        result = subprocess.run(
            ["git", "remote", "show", "origin"],
            capture_output=True,
            text=True,
            check=True
        )
        
        # 解析输出找到HEAD分支
        lines = result.stdout.strip().split("\n")
        for line in lines:
            if "HEAD branch" in line:
                return line.split(":")[-1].strip()
        
        # 如果无法确定，尝试常见的分支名
        for branch in ["main", "master", "develop"]:
            try:
                result = subprocess.run(
                    ["git", "rev-parse", "--verify", f"origin/{branch}"],
                    capture_output=True,
                    text=True,
                    check=True
                )
                return branch
            except subprocess.CalledProcessError:
                continue
                
        # 兜底返回master
        return "master"
    except subprocess.CalledProcessError:
        return "master"

def cleanup_temp_dir(temp_dir):
    """清理临时目录。
    
    Args:
        temp_dir: 临时目录路径。
    """
    try:
        shutil.rmtree(temp_dir)
        console.print(f"[bold]已删除临时目录: {temp_dir}[/bold]")
    except Exception as e:
        console.print(f"[bold red]删除临时目录失败: {e}[/bold red]") 