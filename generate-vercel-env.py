#!/usr/bin/env python3
"""
Vercel 环境变量生成器
帮助生成安全的环境变量配置
"""

import secrets
import string
import json
from datetime import datetime

def generate_api_key(length=32):
    """生成安全的 API 密钥"""
    return secrets.token_hex(length)

def generate_env_config():
    """生成 Vercel 环境变量配置"""
    api_key = generate_api_key()
    
    env_vars = {
        "API_KEY": {
            "value": api_key,
            "description": "API 认证密钥（自动生成）"
        },
        "APP_ENV": {
            "value": "production",
            "description": "应用环境"
        },
        "USE_PADDLE_OCR": {
            "value": "false",
            "description": "是否启用 OCR（需要额外配置）"
        },
        "STAGING_BINS": {
            "value": "S-01,S-02,S-03,S-04",
            "description": "暂存区编号列表"
        },
        "STAGING_THRESHOLD_HOURS": {
            "value": "12",
            "description": "暂存区超时警告时间（小时）"
        },
        "TZ": {
            "value": "America/Los_Angeles",
            "description": "时区设置"
        },
        "STORAGE_BACKEND": {
            "value": "local",
            "description": "存储后端（Vercel 只支持临时存储）"
        },
        "STORAGE_LOCAL_DIR": {
            "value": "/tmp/storage",
            "description": "本地存储目录"
        },
        "DB_URL": {
            "value": "sqlite:////tmp/inventory.db",
            "description": "数据库连接（建议使用外部数据库）"
        }
    }
    
    return env_vars, api_key

def save_env_file(env_vars):
    """保存为 .env.vercel 文件"""
    with open('.env.vercel', 'w') as f:
        f.write("# Vercel 环境变量配置\n")
        f.write(f"# 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("# ⚠️  请勿提交此文件到 Git！\n\n")
        
        for key, config in env_vars.items():
            f.write(f"# {config['description']}\n")
            f.write(f"{key}={config['value']}\n\n")

def print_vercel_cli_commands(env_vars):
    """打印 Vercel CLI 命令"""
    print("\n📋 Vercel CLI 命令（如果使用 CLI 部署）:")
    print("```bash")
    for key, config in env_vars.items():
        print(f"vercel env add {key} production")
        print(f"# 输入值: {config['value']}")
    print("```")

def main():
    print("🔐 Vercel 环境变量生成器")
    print("=" * 50)
    
    env_vars, api_key = generate_env_config()
    
    # 保存文件
    save_env_file(env_vars)
    print("\n✅ 已生成 .env.vercel 文件")
    
    # 打印重要信息
    print("\n🔑 重要信息（请妥善保存）:")
    print(f"API_KEY: {api_key}")
    print("\n⚠️  安全提醒:")
    print("1. 请将 API_KEY 保存在安全的地方")
    print("2. 不要将 .env.vercel 提交到 Git")
    print("3. 在 Vercel Dashboard 中设置这些环境变量")
    
    # 打印表格格式
    print("\n📊 环境变量列表:")
    print("-" * 70)
    print(f"{'变量名':<25} {'值':<30} {'说明'}")
    print("-" * 70)
    for key, config in env_vars.items():
        value = config['value']
        if key == 'API_KEY':
            value = value[:10] + '...' + value[-10:]  # 部分隐藏
        print(f"{key:<25} {value:<30} {config['description']}")
    
    # 打印 CLI 命令
    print_vercel_cli_commands(env_vars)
    
    # 打印 JSON 格式（用于批量导入）
    print("\n📄 JSON 格式（可用于批量导入）:")
    json_env = {k: v['value'] for k, v in env_vars.items()}
    print(json.dumps(json_env, indent=2))

if __name__ == "__main__":
    main()
