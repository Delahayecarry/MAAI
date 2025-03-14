#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
后端SSE实现检查脚本
用于检查后端的SSE实现是否符合标准，并提供修复建议
"""

import requests
import json
import time
import asyncio
import aiohttp
import sys
import os
import re
from datetime import datetime

# 后端API基础URL
BACKEND_URL = "http://localhost:8000"

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

def check_backend_code():
    """检查后端代码中的SSE实现"""
    print_step(2, "检查后端代码")
    
    main_py_path = "backend/main.py"
    if not os.path.exists(main_py_path):
        print_colored(f"✗ 找不到后端主文件: {main_py_path}", Colors.RED)
        return False
    
    try:
        with open(main_py_path, "r", encoding="utf-8") as f:
            code = f.read()
        
        # 检查SSE相关代码
        issues = []
        
        # 检查Content-Type设置
        if "text/event-stream" not in code:
            issues.append("未找到'text/event-stream'内容类型设置")
        
        # 检查SSE格式
        if "data:" not in code and "event:" not in code:
            issues.append("未找到SSE标准格式(data:或event:)")
        
        # 检查换行符
        if "\n\n" not in code and "\\n\\n" not in code:
            issues.append("未找到SSE消息所需的双换行符")
        
        # 检查yield
        if "yield" not in code:
            issues.append("未找到yield语句，FastAPI的SSE实现通常使用yield")
        
        # 检查StreamingResponse
        if "StreamingResponse" not in code:
            issues.append("未找到StreamingResponse，FastAPI的SSE实现通常使用StreamingResponse")
        
        # 检查事件流路由
        event_route_pattern = r"@app\.get\(['\"]\/api\/events['\"]"
        if not re.search(event_route_pattern, code):
            issues.append("未找到/api/events路由定义")
        
        if issues:
            print_colored("在后端代码中发现以下SSE实现问题:", Colors.YELLOW)
            for i, issue in enumerate(issues, 1):
                print_colored(f"{i}. {issue}", Colors.YELLOW)
            return False
        else:
            print_colored("✓ 后端代码中的SSE实现基本符合标准", Colors.GREEN)
            return True
    
    except Exception as e:
        print_colored(f"✗ 检查后端代码时出错: {e}", Colors.RED)
        return False

async def check_sse_headers():
    """检查SSE响应头"""
    print_step(3, "检查SSE响应头")
    
    try:
        timeout = aiohttp.ClientTimeout(total=5)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            try:
                async with session.get(f"{BACKEND_URL}/api/events") as response:
                    headers = response.headers
                    
                    issues = []
                    
                    # 检查Content-Type
                    content_type = headers.get("Content-Type", "")
                    if "text/event-stream" not in content_type:
                        issues.append(f"Content-Type不正确: {content_type}，应为text/event-stream")
                    
                    # 检查缓存控制
                    cache_control = headers.get("Cache-Control", "")
                    if "no-cache" not in cache_control.lower():
                        issues.append(f"Cache-Control不包含no-cache: {cache_control}")
                    
                    # 检查连接类型
                    connection = headers.get("Connection", "")
                    if "keep-alive" not in connection.lower():
                        issues.append(f"Connection不是keep-alive: {connection}")
                    
                    # 检查CORS头
                    cors_origin = headers.get("Access-Control-Allow-Origin", "")
                    if not cors_origin:
                        issues.append("未设置Access-Control-Allow-Origin头")
                    
                    if issues:
                        print_colored("在SSE响应头中发现以下问题:", Colors.YELLOW)
                        for i, issue in enumerate(issues, 1):
                            print_colored(f"{i}. {issue}", Colors.YELLOW)
                        
                        print_colored("\n正确的SSE响应头应包含:", Colors.BLUE)
                        print_colored("Content-Type: text/event-stream", Colors.BLUE)
                        print_colored("Cache-Control: no-cache", Colors.BLUE)
                        print_colored("Connection: keep-alive", Colors.BLUE)
                        print_colored("Access-Control-Allow-Origin: *（或特定域名）", Colors.BLUE)
                        return False
                    else:
                        print_colored("✓ SSE响应头符合标准", Colors.GREEN)
                        print_colored("响应头:", Colors.GREEN)
                        for key, value in headers.items():
                            print_colored(f"  {key}: {value}", Colors.GREEN)
                        return True
            
            except asyncio.TimeoutError:
                print_colored("✗ 连接SSE事件流超时", Colors.RED)
                return False
            except Exception as e:
                print_colored(f"✗ 连接SSE事件流时出错: {e}", Colors.RED)
                return False
    
    except Exception as e:
        print_colored(f"✗ 检查SSE响应头时出错: {e}", Colors.RED)
        return False

async def check_sse_message_format():
    """检查SSE消息格式"""
    print_step(4, "检查SSE消息格式")
    
    try:
        timeout = aiohttp.ClientTimeout(total=10)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            try:
                async with session.get(f"{BACKEND_URL}/api/events") as response:
                    if response.status == 200:
                        print_colored("连接到SSE事件流，等待接收消息...", Colors.BLUE)
                        
                        # 等待接收消息
                        start_time = time.time()
                        received_messages = []
                        
                        while time.time() - start_time < 5 and len(received_messages) < 5:  # 等待5秒或收到5条消息
                            try:
                                line = await asyncio.wait_for(response.content.readline(), 1.0)
                                if line:
                                    line = line.decode('utf-8').strip()
                                    if line:
                                        received_messages.append(line)
                            except asyncio.TimeoutError:
                                # 超时但继续尝试
                                continue
                        
                        if received_messages:
                            print_colored(f"收到 {len(received_messages)} 条消息", Colors.GREEN)
                            
                            # 分析消息格式
                            valid_format = True
                            issues = []
                            
                            # 将连续的消息行组合成完整消息
                            messages = []
                            current_message = []
                            
                            for line in received_messages:
                                if not line:  # 空行表示消息结束
                                    if current_message:
                                        messages.append("\n".join(current_message))
                                        current_message = []
                                else:
                                    current_message.append(line)
                            
                            if current_message:  # 添加最后一条消息
                                messages.append("\n".join(current_message))
                            
                            # 如果没有成功组合消息，使用原始行
                            if not messages:
                                messages = received_messages
                            
                            # 检查每条消息
                            for i, message in enumerate(messages):
                                print_colored(f"\n消息 {i+1}:", Colors.BLUE)
                                print_colored(message, Colors.BLUE)
                                
                                # 检查是否包含data:前缀
                                if not message.startswith("data:") and "data:" not in message:
                                    issues.append(f"消息 {i+1} 不包含'data:'前缀")
                                    valid_format = False
                                
                                # 检查JSON格式
                                if "data:" in message:
                                    data_part = message.split("data:", 1)[1].strip()
                                    try:
                                        json.loads(data_part)
                                    except json.JSONDecodeError:
                                        issues.append(f"消息 {i+1} 的数据部分不是有效的JSON")
                                        valid_format = False
                            
                            if valid_format:
                                print_colored("✓ SSE消息格式符合标准", Colors.GREEN)
                                return True
                            else:
                                print_colored("✗ SSE消息格式存在问题:", Colors.YELLOW)
                                for issue in issues:
                                    print_colored(f"  - {issue}", Colors.YELLOW)
                                return False
                        else:
                            print_colored("✗ 未收到任何消息", Colors.RED)
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
        print_colored(f"✗ 检查SSE消息格式时出错: {e}", Colors.RED)
        return False

def provide_sse_implementation_example():
    """提供标准的SSE实现示例"""
    print_step(5, "提供SSE实现示例")
    
    print_colored("以下是FastAPI中标准的SSE实现示例:", Colors.BLUE)
    
    example_code = """
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
import asyncio
import json

app = FastAPI()

@app.get("/api/events")
async def event_stream(request: Request):
    async def generate():
        # 设置初始连接消息
        yield "data: {\"type\": \"connection\", \"message\": \"Connected to SSE stream\"}\n\n"
        
        # 发送心跳消息以保持连接
        while True:
            # 检查客户端是否断开连接
            if await request.is_disconnected():
                break
                
            # 创建消息
            message = {
                "type": "heartbeat",
                "timestamp": time.time()
            }
            
            # 发送消息
            yield f"data: {json.dumps(message)}\n\n"
            
            # 等待一段时间
            await asyncio.sleep(5)
    
    # 返回流式响应
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*"
        }
    )
"""
    
    print_colored(example_code, Colors.GREEN)
    
    print_colored("\n关键点说明:", Colors.YELLOW)
    print_colored("1. 使用StreamingResponse返回事件流", Colors.YELLOW)
    print_colored("2. 设置正确的媒体类型: text/event-stream", Colors.YELLOW)
    print_colored("3. 设置必要的响应头", Colors.YELLOW)
    print_colored("4. 每条消息以'data:'开头", Colors.YELLOW)
    print_colored("5. 每条消息以两个换行符结束: \\n\\n", Colors.YELLOW)
    print_colored("6. 检查客户端是否断开连接", Colors.YELLOW)
    print_colored("7. 定期发送心跳消息以保持连接", Colors.YELLOW)

def check_backend_logs():
    """检查后端日志中是否有SSE相关信息"""
    print_step(6, "分析后端日志")
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
            print_colored("建议在后端代码中添加更多SSE相关的日志记录", Colors.YELLOW)
    except Exception as e:
        print_colored(f"✗ 读取后端日志时出错: {e}", Colors.RED)

def provide_fix_suggestions():
    """提供修复建议"""
    print_header("修复建议")
    
    print_colored("根据检查结果，以下是可能的修复建议:", Colors.YELLOW)
    
    print_colored("\n1. 确保正确设置响应头", Colors.BOLD + Colors.BLUE)
    print_colored("""
# 在FastAPI的StreamingResponse中设置正确的响应头
return StreamingResponse(
    generate(),
    media_type="text/event-stream",
    headers={
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "Access-Control-Allow-Origin": "*"  # 或设置为特定域名
    }
)
""", Colors.BLUE)
    
    print_colored("\n2. 确保消息格式正确", Colors.BOLD + Colors.BLUE)
    print_colored("""
# 每条消息必须以'data:'开头，以两个换行符结束
message = {"type": "message", "content": "Hello"}
yield f"data: {json.dumps(message)}\\n\\n"
""", Colors.BLUE)
    
    print_colored("\n3. 添加心跳消息", Colors.BOLD + Colors.BLUE)
    print_colored("""
# 定期发送心跳消息以保持连接
while True:
    if await request.is_disconnected():
        break
    
    message = {"type": "heartbeat", "timestamp": time.time()}
    yield f"data: {json.dumps(message)}\\n\\n"
    
    await asyncio.sleep(5)  # 每5秒发送一次心跳
""", Colors.BLUE)
    
    print_colored("\n4. 检查客户端连接状态", Colors.BOLD + Colors.BLUE)
    print_colored("""
# 检查客户端是否断开连接
if await request.is_disconnected():
    break
""", Colors.BLUE)
    
    print_colored("\n5. 添加错误处理", Colors.BOLD + Colors.BLUE)
    print_colored("""
# 添加try-except块处理异常
try:
    # 发送消息
    yield f"data: {json.dumps(message)}\\n\\n"
except Exception as e:
    logger.error(f"发送SSE消息时出错: {e}")
    break  # 出错时结束流
""", Colors.BLUE)
    
    print_colored("\n6. 添加更多日志记录", Colors.BOLD + Colors.BLUE)
    print_colored("""
# 添加详细的日志记录
logger.info("客户端连接到SSE事件流")
logger.info(f"发送消息: {message}")
logger.info("客户端断开连接")
""", Colors.BLUE)

async def main():
    """主函数"""
    print_header("后端SSE实现检查")
    
    # 检查后端
    if not check_backend():
        print_colored("检查终止: 后端服务未运行", Colors.RED)
        return
    
    # 检查后端代码
    check_backend_code()
    
    # 检查SSE响应头
    await check_sse_headers()
    
    # 检查SSE消息格式
    await check_sse_message_format()
    
    # 检查后端日志
    check_backend_logs()
    
    # 提供SSE实现示例
    provide_sse_implementation_example()
    
    # 提供修复建议
    provide_fix_suggestions()
    
    print_header("检查完成")
    print_colored("请根据上述建议修复后端SSE实现中的问题", Colors.GREEN)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n用户取消检查")
    except Exception as e:
        print(f"\n程序出错: {e}") 