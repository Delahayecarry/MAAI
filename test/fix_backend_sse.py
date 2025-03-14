#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
后端SSE实现修复脚本
用于修复后端的SSE实现问题，确保符合标准并能正确与前端通信
"""

import os
import sys
import re
import shutil
from datetime import datetime

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

def backup_file(file_path):
    """备份文件"""
    if not os.path.exists(file_path):
        print_colored(f"文件不存在: {file_path}", Colors.RED)
        return False
    
    backup_path = f"{file_path}.bak.{datetime.now().strftime('%Y%m%d%H%M%S')}"
    try:
        shutil.copy2(file_path, backup_path)
        print_colored(f"已备份文件: {backup_path}", Colors.GREEN)
        return True
    except Exception as e:
        print_colored(f"备份文件时出错: {e}", Colors.RED)
        return False

def fix_sse_route(content):
    """修复SSE路由"""
    print_step(2, "修复SSE路由")
    
    # 检查并修改路由路径
    if '@app.get("/events")' in content:
        print_colored("发现问题: SSE路由路径不符合API规范", Colors.YELLOW)
        content = content.replace('@app.get("/events")', '@app.get("/api/events")')
        print_colored("已修复: 将路由路径从 /events 修改为 /api/events", Colors.GREEN)
    
    return content

def fix_event_stream_function(content):
    """修复event_stream函数"""
    print_step(3, "修复event_stream函数")
    
    # 查找event_stream函数定义
    event_stream_pattern = r'async def event_stream\(\):.*?return StreamingResponse\('
    event_stream_match = re.search(event_stream_pattern, content, re.DOTALL)
    
    if not event_stream_match:
        print_colored("无法找到event_stream函数", Colors.RED)
        return content
    
    # 获取原始函数定义
    original_function = event_stream_match.group(0)
    
    # 检查是否缺少request参数
    if 'async def event_stream():' in original_function:
        print_colored("发现问题: event_stream函数缺少request参数", Colors.YELLOW)
        new_function = original_function.replace(
            'async def event_stream():',
            'async def event_stream(request: Request):'
        )
        content = content.replace(original_function, new_function)
        print_colored("已修复: 添加request参数", Colors.GREEN)
    
    return content

def fix_streaming_response(content):
    """修复StreamingResponse配置"""
    print_step(4, "修复StreamingResponse配置")
    
    # 查找StreamingResponse配置
    response_pattern = r'return StreamingResponse\(\s*generate\(\),\s*media_type="text/event-stream",\s*headers={.*?}\s*\)'
    response_match = re.search(response_pattern, content, re.DOTALL)
    
    if not response_match:
        print_colored("无法找到StreamingResponse配置", Colors.RED)
        return content
    
    # 获取原始配置
    original_response = response_match.group(0)
    
    # 检查并修复响应头
    headers_issues = []
    
    if '"Cache-Control": "no-cache"' not in original_response:
        headers_issues.append('缺少或不正确的Cache-Control头')
    
    if '"Connection": "keep-alive"' not in original_response:
        headers_issues.append('缺少或不正确的Connection头')
    
    if '"Access-Control-Allow-Origin"' not in original_response:
        headers_issues.append('缺少Access-Control-Allow-Origin头')
    
    if headers_issues:
        print_colored("发现响应头问题:", Colors.YELLOW)
        for issue in headers_issues:
            print_colored(f"  - {issue}", Colors.YELLOW)
        
        # 构建新的响应头
        new_response = """return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "X-Accel-Buffering": "no"
        }
    )"""
        
        content = content.replace(original_response, new_response)
        print_colored("已修复: 更新响应头配置", Colors.GREEN)
    
    return content

def fix_message_format(content):
    """修复消息格式"""
    print_step(5, "修复消息格式")
    
    # 检查并修复消息格式
    issues = []
    
    # 检查连接消息格式
    if 'connection_message = f"data: {{' in content and '\\n\\n"' not in content:
        issues.append('连接消息格式不正确，缺少双换行符')
    
    # 检查状态消息格式
    if 'status_message = f"event: simulation_status\\ndata:' in content and '\\n\\n"' not in content:
        issues.append('状态消息格式不正确，缺少双换行符')
    
    # 检查测试消息格式
    if 'test_message_str = f"event: agent_message\\ndata:' in content and '\\n\\n"' not in content:
        issues.append('测试消息格式不正确，缺少双换行符')
    
    # 检查事件消息格式
    if 'event_message = f"event: {event_type}\\ndata:' in content and '\\n\\n"' not in content:
        issues.append('事件消息格式不正确，缺少双换行符')
    
    if issues:
        print_colored("发现消息格式问题:", Colors.YELLOW)
        for issue in issues:
            print_colored(f"  - {issue}", Colors.YELLOW)
        
        # 修复连接消息格式
        content = re.sub(
            r'connection_message = f"data: (.*?)\\n\\n"',
            r'connection_message = f"data: \1\\n\\n"',
            content
        )
        
        # 修复状态消息格式
        content = re.sub(
            r'status_message = f"event: simulation_status\\ndata: (.*?)\\n\\n"',
            r'status_message = f"event: simulation_status\\ndata: \1\\n\\n"',
            content
        )
        
        # 修复测试消息格式
        content = re.sub(
            r'test_message_str = f"event: agent_message\\ndata: (.*?)\\n\\n"',
            r'test_message_str = f"event: agent_message\\ndata: \1\\n\\n"',
            content
        )
        
        # 修复事件消息格式
        content = re.sub(
            r'event_message = f"event: {event_type}\\ndata: (.*?)\\n\\n"',
            r'event_message = f"event: {event_type}\\ndata: \1\\n\\n"',
            content
        )
        
        print_colored("已修复: 更新消息格式，确保包含双换行符", Colors.GREEN)
    
    return content

def fix_client_disconnection_check(content):
    """修复客户端断开连接检查"""
    print_step(6, "修复客户端断开连接检查")
    
    # 查找事件循环
    event_loop_pattern = r'while True:.*?try:.*?event = await asyncio\.wait_for\(event_queue\.get\(\), timeout=1\.0\)'
    event_loop_match = re.search(event_loop_pattern, content, re.DOTALL)
    
    if not event_loop_match:
        print_colored("无法找到事件循环", Colors.RED)
        return content
    
    # 获取原始循环
    original_loop = event_loop_match.group(0)
    
    # 检查是否缺少断开连接检查
    if 'if await request.is_disconnected():' not in content:
        print_colored("发现问题: 缺少客户端断开连接检查", Colors.YELLOW)
        
        # 构建新的循环，包含断开连接检查
        new_loop = """while True:
                # 检查客户端是否断开连接
                if await request.is_disconnected():
                    logger.info(f"客户端断开连接: {client_id}")
                    break
                    
                try:
                    # 使用超时，以便可以检查客户端是否断开连接
                    event = await asyncio.wait_for(event_queue.get(), timeout=1.0)"""
        
        content = content.replace(original_loop, new_loop)
        print_colored("已修复: 添加客户端断开连接检查", Colors.GREEN)
    
    return content

def fix_imports(content):
    """修复导入语句"""
    print_step(7, "修复导入语句")
    
    # 检查是否缺少Request导入
    if 'from fastapi import FastAPI, HTTPException, BackgroundTasks' in content and 'Request' not in content:
        print_colored("发现问题: 缺少Request导入", Colors.YELLOW)
        content = content.replace(
            'from fastapi import FastAPI, HTTPException, BackgroundTasks',
            'from fastapi import FastAPI, HTTPException, BackgroundTasks, Request'
        )
        print_colored("已修复: 添加Request导入", Colors.GREEN)
    
    return content

def fix_backend_sse():
    """修复后端SSE实现"""
    print_header("后端SSE实现修复")
    
    main_py_path = "backend/main.py"
    
    # 检查文件是否存在
    if not os.path.exists(main_py_path):
        print_colored(f"错误: 找不到后端主文件: {main_py_path}", Colors.RED)
        return False
    
    # 备份文件
    print_step(1, "备份原始文件")
    if not backup_file(main_py_path):
        print_colored("错误: 无法备份文件，中止修复", Colors.RED)
        return False
    
    try:
        # 读取文件内容
        with open(main_py_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # 应用修复
        content = fix_imports(content)
        content = fix_sse_route(content)
        content = fix_event_stream_function(content)
        content = fix_streaming_response(content)
        content = fix_message_format(content)
        content = fix_client_disconnection_check(content)
        
        # 写入修复后的内容
        print_step(8, "保存修复后的文件")
        with open(main_py_path, "w", encoding="utf-8") as f:
            f.write(content)
        
        print_colored("✓ 成功修复后端SSE实现", Colors.GREEN)
        print_colored("请重启后端服务以应用更改", Colors.YELLOW)
        return True
    
    except Exception as e:
        print_colored(f"修复过程中出错: {e}", Colors.RED)
        return False

if __name__ == "__main__":
    try:
        fix_backend_sse()
    except KeyboardInterrupt:
        print("\n用户取消修复")
    except Exception as e:
        print(f"\n程序出错: {e}") 