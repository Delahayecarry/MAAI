#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
前后端通信测试脚本
用于测试前端和后端之间的通信，特别是检查前端是否能够正确接收和显示消息
"""

import requests
import json
import time
import asyncio
import aiohttp
import sys
import os
import webbrowser
from datetime import datetime

# 后端API基础URL
BACKEND_URL = "http://localhost:8000"
# 前端URL
FRONTEND_URL = "http://localhost:3000"

# 颜色输出
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_colored(message, color=Colors.BLUE):
    """打印带颜色的文本"""
    print(f"{color}{message}{Colors.ENDC}")

def print_header(message):
    """打印标题"""
    print(f"\n{Colors.BOLD}{Colors.PURPLE}{'='*80}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.PURPLE}{message.center(80)}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.PURPLE}{'='*80}{Colors.ENDC}\n")

def print_step(step_number, message):
    """打印步骤"""
    print(f"{Colors.BOLD}{Colors.CYAN}步骤 {step_number}: {message}{Colors.ENDC}")

def check_backend():
    """检查后端是否运行"""
    print_step(1, "检查后端服务")
    try:
        response = requests.get(f"{BACKEND_URL}/api/scenarios")
        if response.status_code == 200:
            print_colored("✓ 后端服务正常运行", Colors.GREEN)
            return True
        else:
            print_colored(f"✗ 后端服务返回异常状态码: {response.status_code}", Colors.RED)
            return False
    except requests.exceptions.ConnectionError:
        print_colored(f"✗ 无法连接到后端服务: {BACKEND_URL}", Colors.RED)
        print_colored("请确保后端服务已启动", Colors.YELLOW)
        return False

def check_frontend():
    """检查前端是否运行"""
    print_step(2, "检查前端服务")
    try:
        response = requests.get(FRONTEND_URL)
        if response.status_code == 200:
            print_colored("✓ 前端服务正常运行", Colors.GREEN)
            return True
        else:
            print_colored(f"✗ 前端服务返回异常状态码: {response.status_code}", Colors.RED)
            return False
    except requests.exceptions.ConnectionError:
        print_colored(f"✗ 无法连接到前端服务: {FRONTEND_URL}", Colors.RED)
        print_colored("请确保前端服务已启动", Colors.YELLOW)
        return False

def get_scenarios():
    """获取场景列表"""
    print_step(3, "获取场景列表")
    try:
        response = requests.get(f"{BACKEND_URL}/api/scenarios")
        if response.status_code == 200:
            scenarios = response.json()
            if scenarios and len(scenarios) > 0:
                print_colored(f"✓ 获取到 {len(scenarios)} 个场景", Colors.GREEN)
                for i, scenario in enumerate(scenarios, 1):
                    print_colored(f"  {i}. {scenario['name']}: {scenario['description']}", Colors.GREEN)
                return scenarios
            else:
                print_colored("✗ 没有可用的场景", Colors.RED)
                return None
        else:
            print_colored(f"✗ 获取场景列表失败，状态码: {response.status_code}", Colors.RED)
            return None
    except Exception as e:
        print_colored(f"✗ 获取场景列表时出错: {e}", Colors.RED)
        return None

def start_simulation(scenario_id):
    """启动模拟"""
    print_step(4, f"启动模拟 (场景ID: {scenario_id})")
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/simulation/start", 
            json={"scenario_id": scenario_id}
        )
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print_colored("✓ 模拟启动成功", Colors.GREEN)
                return True
            else:
                print_colored(f"✗ 模拟启动失败: {result.get('message', '未知错误')}", Colors.RED)
                return False
        else:
            print_colored(f"✗ 模拟启动失败，状态码: {response.status_code}", Colors.RED)
            return False
    except Exception as e:
        print_colored(f"✗ 启动模拟时出错: {e}", Colors.RED)
        return False

def stop_simulation():
    """停止模拟"""
    print_step(6, "停止模拟")
    try:
        response = requests.post(f"{BACKEND_URL}/api/simulation/stop")
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                print_colored("✓ 模拟停止成功", Colors.GREEN)
                return True
            else:
                print_colored(f"✗ 模拟停止失败: {result.get('message', '未知错误')}", Colors.RED)
                return False
        else:
            print_colored(f"✗ 模拟停止失败，状态码: {response.status_code}", Colors.RED)
            return False
    except Exception as e:
        print_colored(f"✗ 停止模拟时出错: {e}", Colors.RED)
        return False

def open_frontend():
    """打开前端页面"""
    print_step(5, "打开前端页面")
    try:
        # 打开实时对话页面
        url = f"{FRONTEND_URL}/live-chat"
        print_colored(f"正在打开浏览器: {url}", Colors.BLUE)
        webbrowser.open(url)
        print_colored("✓ 已打开浏览器", Colors.GREEN)
        print_colored("请在浏览器中观察消息是否正确显示", Colors.YELLOW)
        return True
    except Exception as e:
        print_colored(f"✗ 打开浏览器时出错: {e}", Colors.RED)
        return False

def main():
    """主函数"""
    print_header("前后端通信测试")
    
    # 检查后端
    if not check_backend():
        print_colored("测试终止: 后端服务未运行", Colors.RED)
        return
    
    # 检查前端
    if not check_frontend():
        print_colored("测试终止: 前端服务未运行", Colors.RED)
        return
    
    # 获取场景列表
    scenarios = get_scenarios()
    if not scenarios:
        print_colored("测试终止: 无法获取场景列表", Colors.RED)
        return
    
    # 选择第一个场景
    scenario_id = scenarios[0]["id"]
    
    # 启动模拟
    if not start_simulation(scenario_id):
        print_colored("测试终止: 无法启动模拟", Colors.RED)
        return
    
    # 打开前端页面
    open_frontend()
    
    # 等待用户观察
    print_colored("\n请在浏览器中观察消息是否正确显示", Colors.YELLOW)
    print_colored("测试将在30秒后自动停止模拟", Colors.YELLOW)
    print_colored("按Ctrl+C可以立即停止测试", Colors.YELLOW)
    
    try:
        # 等待30秒
        for i in range(30, 0, -1):
            print(f"\r倒计时: {i} 秒", end="")
            time.sleep(1)
        print("\r测试完成                ")
    except KeyboardInterrupt:
        print("\r用户取消测试            ")
    
    # 停止模拟
    stop_simulation()
    
    print_header("测试完成")
    print_colored("如果您在浏览器中看到了消息，则表示前后端通信正常", Colors.GREEN)
    print_colored("如果没有看到消息，请检查浏览器控制台和后端日志以查找问题", Colors.YELLOW)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n用户取消测试")
        # 尝试停止模拟
        try:
            stop_simulation()
        except:
            pass
    except Exception as e:
        print(f"\n程序出错: {e}")
        # 尝试停止模拟
        try:
            stop_simulation()
        except:
            pass 