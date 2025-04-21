"""配置管理模块。"""

import json
import os
from pathlib import Path

# 配置文件路径
CONFIG_DIR = Path.home() / ".auto-md"
CONFIG_FILE = CONFIG_DIR / "config.json"

def save_config(config):
    """保存配置到配置文件。"""
    # 确保配置目录存在
    os.makedirs(CONFIG_DIR, exist_ok=True)
    
    # 保存配置
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4, ensure_ascii=False)

def load_config():
    """从配置文件加载配置。"""
    if not CONFIG_FILE.exists():
        return {}
    
    try:
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        # 如果配置文件损坏，返回空配置
        return {}

def get_git_config():
    """获取Git配置信息。"""
    config = load_config()
    return config.get("git", {})

def get_jira_config():
    """获取Jira配置信息。"""
    config = load_config()
    return config.get("jira", {})

def is_initialized():
    """检查配置是否已初始化。"""
    config = load_config()
    git_config = config.get("git", {})
    jira_config = config.get("jira", {})
    
    git_initialized = all(key in git_config for key in ["url", "username", "password"])
    jira_initialized = all(key in jira_config for key in ["username", "password"])
    
    return git_initialized and jira_initialized 