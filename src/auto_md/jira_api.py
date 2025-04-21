"""Jira API交互模块。"""

import requests
import base64
from rich.console import Console
from .config import get_jira_config

console = Console()

# Jira API基础URL
JIRA_API_BASE_URL = "https://jira.logisticsteam.com/rest/api/2"

def get_auth_header():
    """获取带有Basic认证的HTTP头。"""
    jira_config = get_jira_config()
    username = jira_config.get("username")
    password = jira_config.get("password")
    
    if not username or not password:
        raise ValueError("未配置Jira凭据，请先运行 'auto-md init' 命令")
    
    auth_str = f"{username}:{password}"
    auth_bytes = auth_str.encode("ascii")
    base64_bytes = base64.b64encode(auth_bytes)
    base64_auth = base64_bytes.decode("ascii")
    
    return {"Authorization": f"Basic {base64_auth}"}

def get_issue(issue_key):
    """获取Jira问题的详细信息。
    
    Args:
        issue_key: Jira问题的键，例如 'DTS-6038'。
        
    Returns:
        包含问题详细信息的字典。
    """
    url = f"{JIRA_API_BASE_URL}/issue/{issue_key}?expand=fields"
    headers = get_auth_header()
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        console.print(f"[bold red]获取Jira问题信息失败: {e}[/bold red]")
        return None

def get_parent_issue(issue):
    """获取父问题的详细信息。
    
    Args:
        issue: 子问题的详细信息。
        
    Returns:
        父问题的详细信息，如果没有父问题则返回None。
    """
    if "fields" not in issue or "parent" not in issue["fields"]:
        return None
    
    parent_key = issue["fields"]["parent"]["key"]
    return get_issue(parent_key) 