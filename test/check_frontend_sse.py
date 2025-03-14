#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
前端SSE连接检查脚本
用于检查前端是否正确连接到后端的SSE事件流
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
import subprocess
import re

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

def check_backend_sse_endpoint():
    """检查后端SSE端点是否可用"""
    print_step(3, "检查后端SSE端点")
    try:
        # 只发送HEAD请求检查端点是否存在
        response = requests.head(f"{BACKEND_URL}/api/events")
        if response.status_code < 400:  # 任何非4xx或5xx状态码都认为端点存在
            print_colored("✓ 后端SSE端点可用", Colors.GREEN)
            return True
        else:
            print_colored(f"✗ 后端SSE端点返回异常状态码: {response.status_code}", Colors.RED)
            return False
    except requests.exceptions.ConnectionError:
        print_colored(f"✗ 无法连接到后端SSE端点", Colors.RED)
        return False

async def test_sse_connection():
    """测试SSE连接"""
    print_step(4, "测试SSE连接")
    try:
        timeout = aiohttp.ClientTimeout(total=10)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            print_colored("尝试连接到SSE事件流...", Colors.BLUE)
            try:
                async with session.get(f"{BACKEND_URL}/api/events") as response:
                    if response.status == 200:
                        print_colored("✓ 成功连接到SSE事件流", Colors.GREEN)
                        print_colored("等待接收事件...", Colors.BLUE)
                        
                        # 只等待几秒钟接收事件
                        start_time = time.time()
                        event_count = 0
                        
                        while time.time() - start_time < 5:  # 等待5秒
                            try:
                                line = await asyncio.wait_for(response.content.readline(), 1.0)
                                if line:
                                    line = line.decode('utf-8').strip()
                                    if line:
                                        event_count += 1
                                        print_colored(f"接收到事件: {line}", Colors.GREEN)
                            except asyncio.TimeoutError:
                                # 超时但继续尝试
                                continue
                        
                        if event_count > 0:
                            print_colored(f"✓ 成功接收到 {event_count} 个事件", Colors.GREEN)
                            return True
                        else:
                            print_colored("✗ 连接成功但未接收到任何事件", Colors.YELLOW)
                            return False
                    else:
                        print_colored(f"✗ SSE连接失败，状态码: {response.status}", Colors.RED)
                        return False
            except asyncio.TimeoutError:
                print_colored("✗ 连接SSE事件流超时", Colors.RED)
                return False
            except Exception as e:
                print_colored(f"✗ 连接SSE事件流时出错: {e}", Colors.RED)
                return False
    except Exception as e:
        print_colored(f"✗ 测试SSE连接时出错: {e}", Colors.RED)
        return False

def check_browser_console():
    """提示用户检查浏览器控制台"""
    print_step(5, "检查浏览器控制台")
    print_colored("请按照以下步骤检查浏览器中的SSE连接:", Colors.YELLOW)
    print_colored("1. 打开浏览器并访问前端页面", Colors.YELLOW)
    print_colored("2. 按F12打开开发者工具", Colors.YELLOW)
    print_colored("3. 切换到'网络'或'Network'标签", Colors.YELLOW)
    print_colored("4. 在过滤器中输入'events'", Colors.YELLOW)
    print_colored("5. 刷新页面，查看是否有'/api/events'请求", Colors.YELLOW)
    print_colored("6. 点击该请求，查看'响应'或'Response'标签中是否有数据流", Colors.YELLOW)
    
    # 尝试自动打开浏览器
    try:
        url = f"{FRONTEND_URL}/live-chat"
        print_colored(f"正在打开浏览器: {url}", Colors.BLUE)
        webbrowser.open(url)
    except Exception as e:
        print_colored(f"无法自动打开浏览器: {e}", Colors.RED)
        print_colored(f"请手动访问: {FRONTEND_URL}/live-chat", Colors.YELLOW)

def check_frontend_logs():
    """检查前端日志中是否有SSE相关信息"""
    print_step(6, "分析前端日志")
    print_colored("请在前端控制台中查找以下信息:", Colors.YELLOW)
    print_colored("1. 'SSE连接已建立'或'SSE connection established'", Colors.YELLOW)
    print_colored("2. 'EventSource'相关的日志", Colors.YELLOW)
    print_colored("3. 任何与'events'或'message'相关的错误", Colors.YELLOW)
    
    print_colored("\n前端SSE服务通常会在控制台输出连接状态和接收到的消息", Colors.BLUE)
    print_colored("如果没有看到相关日志，可能是前端的SSE服务未正确初始化或连接", Colors.BLUE)

def check_backend_logs():
    """检查后端日志中是否有SSE相关信息"""
    print_step(7, "分析后端日志")
    log_file = "backend/simulation.log"
    
    if not os.path.exists(log_file):
        print_colored(f"✗ 找不到后端日志文件: {log_file}", Colors.RED)
        return
    
    try:
        # 读取最后100行日志
        with open(log_file, "r", encoding="utf-8") as f:
            lines = f.readlines()
            last_lines = lines[-100:] if len(lines) > 100 else lines
        
        sse_related_lines = []
        for line in last_lines:
            if "SSE" in line or "event" in line or "stream" in line or "client connect" in line:
                sse_related_lines.append(line.strip())
        
        if sse_related_lines:
            print_colored("在后端日志中找到以下SSE相关信息:", Colors.GREEN)
            for i, line in enumerate(sse_related_lines[-10:], 1):  # 只显示最后10条
                print_colored(f"{i}. {line}", Colors.GREEN)
        else:
            print_colored("✗ 在后端日志中未找到SSE相关信息", Colors.RED)
            print_colored("这可能表明后端未正确处理SSE连接或未记录相关日志", Colors.RED)
    except Exception as e:
        print_colored(f"✗ 读取后端日志时出错: {e}", Colors.RED)

def provide_solutions():
    """提供可能的解决方案"""
    print_header("可能的解决方案")
    
    print_colored("如果前端无法接收后端消息，请尝试以下解决方案:", Colors.YELLOW)
    
    print_colored("\n1. 检查CORS配置", Colors.BOLD + Colors.BLUE)
    print_colored("   - 确保后端允许前端域名的跨域请求", Colors.BLUE)
    print_colored("   - 在后端的FastAPI应用中检查CORS中间件配置", Colors.BLUE)
    
    print_colored("\n2. 检查SSE实现", Colors.BOLD + Colors.BLUE)
    print_colored("   - 确保后端正确实现了SSE协议", Colors.BLUE)
    print_colored("   - 检查Content-Type是否设置为'text/event-stream'", Colors.BLUE)
    print_colored("   - 确保每条消息后都有两个换行符", Colors.BLUE)
    
    print_colored("\n3. 检查前端SSE客户端", Colors.BOLD + Colors.BLUE)
    print_colored("   - 确保前端正确初始化了EventSource", Colors.BLUE)
    print_colored("   - 检查事件监听器是否正确设置", Colors.BLUE)
    print_colored("   - 验证前端是否正确处理接收到的消息", Colors.BLUE)
    
    print_colored("\n4. 检查网络和代理", Colors.BOLD + Colors.BLUE)
    print_colored("   - 确保没有代理或防火墙阻止SSE连接", Colors.BLUE)
    print_colored("   - 某些网络设置可能会缓冲流式响应，导致消息延迟", Colors.BLUE)
    
    print_colored("\n5. 检查消息格式", Colors.BOLD + Colors.BLUE)
    print_colored("   - 确保后端发送的消息格式与前端期望的格式一致", Colors.BLUE)
    print_colored("   - 检查JSON序列化和反序列化是否正确", Colors.BLUE)
    
    print_colored("\n6. 调试建议", Colors.BOLD + Colors.BLUE)
    print_colored("   - 在后端添加更多日志记录SSE连接和消息发送", Colors.BLUE)
    print_colored("   - 在前端控制台中添加更多日志记录SSE连接和消息接收", Colors.BLUE)
    print_colored("   - 使用简单的测试消息验证基本连接是否工作", Colors.BLUE)

async def main():
    """主函数"""
    print_header("前端SSE连接检查")
    
    # 检查后端
    if not check_backend():
        print_colored("检查终止: 后端服务未运行", Colors.RED)
        return
    
    # 检查前端
    if not check_frontend():
        print_colored("检查终止: 前端服务未运行", Colors.RED)
        return
    
    # 检查后端SSE端点
    if not check_backend_sse_endpoint():
        print_colored("警告: 后端SSE端点可能不可用", Colors.YELLOW)
        print_colored("继续检查其他方面...", Colors.YELLOW)
    
    # 测试SSE连接
    sse_connection_ok = await test_sse_connection()
    if not sse_connection_ok:
        print_colored("警告: 无法直接连接到SSE事件流", Colors.YELLOW)
        print_colored("这可能表明SSE服务器端实现有问题", Colors.YELLOW)
    
    # 检查浏览器控制台
    check_browser_console()
    
    # 等待用户查看浏览器
    print_colored("\n请在浏览器中检查SSE连接状态", Colors.YELLOW)
    print_colored("按Enter键继续...", Colors.YELLOW)
    input()
    
    # 检查前端日志
    check_frontend_logs()
    
    # 检查后端日志
    check_backend_logs()
    
    # 提供可能的解决方案
    provide_solutions()
    
    print_header("检查完成")
    print_colored("如果您需要更多帮助，请查看项目文档或联系开发团队", Colors.GREEN)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n用户取消检查")
    except Exception as e:
        print(f"\n程序出错: {e}") 