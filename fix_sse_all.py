#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
SSE全面修复脚本
用于检测和修复前后端的SSE实现问题，确保前后端能够正确通信
"""

import os
import sys
import re
import shutil
import json
import time
import asyncio
import aiohttp
import subprocess
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

def run_command(command, cwd=None):
    """运行命令"""
    try:
        print_colored(f"执行命令: {command}", Colors.BLUE)
        result = subprocess.run(
            command,
            shell=True,
            cwd=cwd,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print_colored("命令执行成功", Colors.GREEN)
            if result.stdout:
                print_colored("输出:", Colors.GREEN)
                print(result.stdout)
            return True
        else:
            print_colored(f"命令执行失败，返回码: {result.returncode}", Colors.RED)
            if result.stderr:
                print_colored("错误输出:", Colors.RED)
                print(result.stderr)
            return False
    except Exception as e:
        print_colored(f"执行命令时出错: {e}", Colors.RED)
        return False

async def check_backend_running():
    """检查后端是否运行"""
    print_step(1, "检查后端服务")
    try:
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get("http://localhost:8000/api/scenarios", timeout=2) as response:
                    if response.status == 200:
                        print_colored("✓ 后端服务正常运行", Colors.GREEN)
                        return True
                    else:
                        print_colored(f"✗ 后端服务返回异常状态码: {response.status}", Colors.RED)
                        return False
            except asyncio.TimeoutError:
                print_colored("✗ 连接后端服务超时", Colors.RED)
                return False
            except Exception as e:
                print_colored(f"✗ 连接后端服务时出错: {e}", Colors.RED)
                return False
    except Exception as e:
        print_colored(f"✗ 检查后端服务时出错: {e}", Colors.RED)
        return False

async def check_frontend_running():
    """检查前端是否运行"""
    print_step(2, "检查前端服务")
    try:
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get("http://localhost:3000", timeout=2) as response:
                    if response.status == 200:
                        print_colored("✓ 前端服务正常运行", Colors.GREEN)
                        return True
                    else:
                        print_colored(f"✗ 前端服务返回异常状态码: {response.status}", Colors.RED)
                        return False
            except asyncio.TimeoutError:
                print_colored("✗ 连接前端服务超时", Colors.RED)
                return False
            except Exception as e:
                print_colored(f"✗ 连接前端服务时出错: {e}", Colors.RED)
                return False
    except Exception as e:
        print_colored(f"✗ 检查前端服务时出错: {e}", Colors.RED)
        return False

def fix_backend_sse():
    """修复后端SSE实现"""
    print_header("后端SSE实现修复")
    
    main_py_path = "backend/main.py"
    
    # 检查文件是否存在
    if not os.path.exists(main_py_path):
        print_colored(f"错误: 找不到后端主文件: {main_py_path}", Colors.RED)
        return False
    
    # 备份文件
    print_step(3, "备份后端文件")
    if not backup_file(main_py_path):
        print_colored("错误: 无法备份文件，中止修复", Colors.RED)
        return False
    
    try:
        # 读取文件内容
        with open(main_py_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # 修复导入语句
        if 'from fastapi import FastAPI, HTTPException, BackgroundTasks' in content and 'Request' not in content:
            print_colored("发现问题: 缺少Request导入", Colors.YELLOW)
            content = content.replace(
                'from fastapi import FastAPI, HTTPException, BackgroundTasks',
                'from fastapi import FastAPI, HTTPException, BackgroundTasks, Request'
            )
            print_colored("已修复: 添加Request导入", Colors.GREEN)
        
        # 修复SSE路由
        if '@app.get("/events")' in content:
            print_colored("发现问题: SSE路由路径不符合API规范", Colors.YELLOW)
            content = content.replace('@app.get("/events")', '@app.get("/api/events")')
            print_colored("已修复: 将路由路径从 /events 修改为 /api/events", Colors.GREEN)
        
        # 修复event_stream函数
        event_stream_pattern = r'async def event_stream\(\):.*?return StreamingResponse\('
        event_stream_match = re.search(event_stream_pattern, content, re.DOTALL)
        
        if event_stream_match:
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
        
        # 修复StreamingResponse配置
        response_pattern = r'return StreamingResponse\(\s*generate\(\),\s*media_type="text/event-stream",\s*headers={.*?}\s*\)'
        response_match = re.search(response_pattern, content, re.DOTALL)
        
        if response_match:
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
        
        # 修复客户端断开连接检查
        event_loop_pattern = r'while True:.*?try:.*?event = await asyncio\.wait_for\(event_queue\.get\(\), timeout=1\.0\)'
        event_loop_match = re.search(event_loop_pattern, content, re.DOTALL)
        
        if event_loop_match:
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
        
        # 写入修复后的内容
        print_step(4, "保存修复后的后端文件")
        with open(main_py_path, "w", encoding="utf-8") as f:
            f.write(content)
        
        print_colored("✓ 成功修复后端SSE实现", Colors.GREEN)
        return True
    
    except Exception as e:
        print_colored(f"修复后端SSE时出错: {e}", Colors.RED)
        return False

def fix_frontend_sse():
    """修复前端SSE实现"""
    print_header("前端SSE实现修复")
    
    sse_service_path = "frontend/src/api/sseService.ts"
    
    # 检查文件是否存在
    if not os.path.exists(sse_service_path):
        print_colored(f"错误: 找不到前端SSE服务文件: {sse_service_path}", Colors.RED)
        return False
    
    # 备份文件
    print_step(5, "备份前端文件")
    if not backup_file(sse_service_path):
        print_colored("错误: 无法备份文件，中止修复", Colors.RED)
        return False
    
    try:
        # 读取文件内容
        with open(sse_service_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # 修复SSE端点URL
        if "this.eventSource = new EventSource('/events')" in content:
            print_colored("发现问题: SSE端点URL不正确", Colors.YELLOW)
            content = content.replace(
                "this.eventSource = new EventSource('/events')",
                "this.eventSource = new EventSource('/api/events')"
            )
            print_colored("已修复: 将SSE端点URL从 /events 修改为 /api/events", Colors.GREEN)
        
        # 增强错误处理
        if "this.eventSource.onerror = (error) => {" in content and "this.reconnect()" in content:
            original_error_handler = """this.eventSource.onerror = (error) => {
      console.error('SSE连接错误:', error)
      this.reconnect()
    }"""
            
            if original_error_handler in content:
                print_colored("发现问题: 错误处理不够健壮", Colors.YELLOW)
                
                new_error_handler = """this.eventSource.onerror = (error) => {
      console.error('SSE连接错误:', error)
      
      // 检查错误类型
      if (this.eventSource && this.eventSource.readyState === EventSource.CLOSED) {
        console.log('SSE连接已关闭，尝试重新连接')
        this.reconnect()
      } else if (this.eventSource && this.eventSource.readyState === EventSource.CONNECTING) {
        console.log('SSE正在尝试连接，等待连接结果')
        // 等待连接结果，不立即重连
      } else {
        console.log('SSE连接出现未知错误，尝试重新连接')
        this.reconnect()
      }
    }"""
                
                content = content.replace(original_error_handler, new_error_handler)
                print_colored("已修复: 增强错误处理逻辑", Colors.GREEN)
        
        # 改进重连逻辑
        reconnect_pattern = r'private reconnect\(\): void {\s*setTimeout\(\(\) => {\s*console\.log\(.*\)\s*this\.connect\(\)\s*}, \d+\)\s*}'
        reconnect_match = re.search(reconnect_pattern, content, re.DOTALL)
        
        if reconnect_match:
            original_reconnect = reconnect_match.group(0)
            print_colored("发现问题: 重连逻辑可以改进", Colors.YELLOW)
            
            new_reconnect = """private reconnect(): void {
    // 如果已经有连接，先断开
    if (this.eventSource) {
      this.disconnect()
    }
    
    // 使用指数退避策略进行重连
    const backoffTime = Math.min(3000 * Math.pow(2, this.reconnectAttempts), 30000)
    this.reconnectAttempts++
    
    console.log(`尝试第 ${this.reconnectAttempts} 次重新连接SSE，等待 ${backoffTime/1000} 秒...`)
    
    setTimeout(() => {
      console.log('正在重新连接SSE...')
      this.connect()
    }, backoffTime)
  }
  
  // 重置重连尝试次数
  private resetReconnectAttempts(): void {
    this.reconnectAttempts = 0
  }"""
            
            content = content.replace(original_reconnect, new_reconnect)
            
            # 添加重连尝试次数属性
            class_declaration = "export class SSEService {"
            class_with_property = "export class SSEService {\n  private reconnectAttempts = 0"
            
            content = content.replace(class_declaration, class_with_property)
            
            # 在连接成功时重置重连尝试次数
            if "this.eventSource.onopen = () => {" in content:
                original_onopen = """this.eventSource.onopen = () => {
      console.log('SSE连接已建立')
    }"""
                
                new_onopen = """this.eventSource.onopen = () => {
      console.log('SSE连接已建立')
      this.resetReconnectAttempts()
    }"""
                
                content = content.replace(original_onopen, new_onopen)
            
            print_colored("已修复: 改进重连逻辑，添加指数退避策略", Colors.GREEN)
        
        # 写入修复后的内容
        print_step(6, "保存修复后的前端文件")
        with open(sse_service_path, "w", encoding="utf-8") as f:
            f.write(content)
        
        print_colored("✓ 成功修复前端SSE实现", Colors.GREEN)
        return True
    
    except Exception as e:
        print_colored(f"修复前端SSE时出错: {e}", Colors.RED)
        return False

def check_vite_config():
    """检查Vite配置"""
    print_header("检查Vite配置")
    
    vite_config_path = "frontend/vite.config.ts"
    
    if not os.path.exists(vite_config_path):
        print_colored(f"警告: 找不到Vite配置文件: {vite_config_path}", Colors.YELLOW)
        print_colored("请确保前端代理配置正确，以便将/api请求转发到后端", Colors.YELLOW)
        return False
    
    try:
        # 备份文件
        print_step(7, "备份Vite配置文件")
        if not backup_file(vite_config_path):
            print_colored("错误: 无法备份文件，中止修复", Colors.RED)
            return False
        
        # 读取文件内容
        with open(vite_config_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # 检查是否有代理配置
        if "'/api/': {" in content or "'/api': {" in content:
            print_colored("✓ 已找到API代理配置", Colors.GREEN)
            
            # 检查是否有SSE代理配置
            if "'/api/events': {" in content:
                print_colored("✓ 已找到SSE事件代理配置", Colors.GREEN)
                return True
            else:
                print_colored("警告: 未找到专门的SSE事件代理配置", Colors.YELLOW)
                
                # 尝试添加SSE代理配置
                proxy_pattern = r'server:\s*{\s*proxy:\s*{.*?}'
                proxy_match = re.search(proxy_pattern, content, re.DOTALL)
                
                if proxy_match:
                    original_proxy = proxy_match.group(0)
                    
                    # 检查是否以}结尾
                    if original_proxy.strip().endswith('}'):
                        # 在最后一个}前添加SSE代理配置
                        new_proxy = original_proxy.replace(
                            '}',
                            """
    '/api/events': {
      target: 'http://localhost:8000',
      changeOrigin: true,
      rewrite: (path) => path.replace(/^\\/api/, ''),
      // 对SSE连接的特殊处理
      configure: (proxy, _options) => {
        proxy.on('error', (err, _req, _res) => {
          console.log('代理错误', err);
        });
      }
    }
  }"""
                        )
                        
                        content = content.replace(original_proxy, new_proxy)
                        
                        # 写入修复后的内容
                        print_step(8, "保存修复后的Vite配置文件")
                        with open(vite_config_path, "w", encoding="utf-8") as f:
                            f.write(content)
                        
                        print_colored("✓ 成功添加SSE代理配置", Colors.GREEN)
                        return True
                    else:
                        print_colored("无法自动添加SSE代理配置，请手动添加", Colors.YELLOW)
                        return False
                else:
                    print_colored("无法找到代理配置部分，请手动添加SSE代理配置", Colors.YELLOW)
                    return False
        else:
            print_colored("警告: 未找到API代理配置", Colors.YELLOW)
            print_colored("请手动添加以下代理配置:", Colors.YELLOW)
            print_colored("""
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true,
      rewrite: (path) => path.replace(/^\\/api/, '')
    },
    '/api/events': {
      target: 'http://localhost:8000',
      changeOrigin: true,
      rewrite: (path) => path.replace(/^\\/api/, '')
    }
  }
}
""", Colors.BLUE)
            return False
    
    except Exception as e:
        print_colored(f"检查Vite配置时出错: {e}", Colors.RED)
        return False

async def test_sse_connection():
    """测试SSE连接"""
    print_header("测试SSE连接")
    
    print_step(9, "测试SSE连接")
    try:
        timeout = aiohttp.ClientTimeout(total=5)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            try:
                print_colored("尝试连接到SSE事件流...", Colors.BLUE)
                async with session.get("http://localhost:8000/api/events") as response:
                    if response.status == 200:
                        print_colored("✓ 成功连接到SSE事件流", Colors.GREEN)
                        print_colored("等待接收事件...", Colors.BLUE)
                        
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
                                        print_colored(f"接收到事件: {line}", Colors.GREEN)
                            except asyncio.TimeoutError:
                                # 超时但继续尝试
                                continue
                        
                        if received_messages:
                            print_colored(f"✓ 成功接收到 {len(received_messages)} 条事件", Colors.GREEN)
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

def restart_services():
    """重启服务"""
    print_header("重启服务")
    
    # 检查是否有运行中的服务
    print_step(10, "检查运行中的服务")
    
    # 在Windows上使用tasklist，在Linux/Mac上使用ps
    if sys.platform == "win32":
        backend_cmd = "tasklist | findstr python"
        frontend_cmd = "tasklist | findstr node"
    else:
        backend_cmd = "ps aux | grep python | grep -v grep"
        frontend_cmd = "ps aux | grep node | grep -v grep"
    
    run_command(backend_cmd)
    run_command(frontend_cmd)
    
    print_colored("\n请手动重启服务以应用更改:", Colors.YELLOW)
    print_colored("1. 重启后端服务: python backend/main.py", Colors.YELLOW)
    print_colored("2. 重启前端服务: cd frontend && npm run dev", Colors.YELLOW)
    
    return True

async def main():
    """主函数"""
    print_header("SSE全面修复")
    
    # 检查服务状态
    backend_running = await check_backend_running()
    frontend_running = await check_frontend_running()
    
    # 修复后端SSE
    backend_fixed = fix_backend_sse()
    
    # 修复前端SSE
    frontend_fixed = fix_frontend_sse()
    
    # 检查Vite配置
    vite_config_fixed = check_vite_config()
    
    # 重启服务
    if backend_fixed or frontend_fixed or vite_config_fixed:
        restart_services()
        
        print_colored("\n请在重启服务后运行以下命令测试SSE连接:", Colors.YELLOW)
        print_colored("python test_sse.py", Colors.YELLOW)
    else:
        print_colored("\n未进行任何修复，无需重启服务", Colors.YELLOW)
    
    print_header("修复完成")
    print_colored("如果您在重启服务后仍然遇到问题，请尝试以下操作:", Colors.YELLOW)
    print_colored("1. 检查浏览器控制台中的错误信息", Colors.YELLOW)
    print_colored("2. 检查后端日志文件: backend/simulation.log", Colors.YELLOW)
    print_colored("3. 使用测试脚本验证SSE连接: python test_sse.py", Colors.YELLOW)
    print_colored("4. 使用测试脚本验证前后端通信: python test_frontend_backend.py", Colors.YELLOW)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n用户取消修复")
    except Exception as e:
        print(f"\n程序出错: {e}") 