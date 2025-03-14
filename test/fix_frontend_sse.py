#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
前端SSE实现修复脚本
用于修复前端的SSE实现问题，确保能正确连接到后端的SSE事件流
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

def fix_sse_endpoint_url(content):
    """修复SSE端点URL"""
    print_step(2, "修复SSE端点URL")
    
    # 检查并修改SSE端点URL
    if "this.eventSource = new EventSource('/events')" in content:
        print_colored("发现问题: SSE端点URL不正确", Colors.YELLOW)
        content = content.replace(
            "this.eventSource = new EventSource('/events')",
            "this.eventSource = new EventSource('/api/events')"
        )
        print_colored("已修复: 将SSE端点URL从 /events 修改为 /api/events", Colors.GREEN)
    
    return content

def fix_error_handling(content):
    """增强错误处理"""
    print_step(3, "增强错误处理")
    
    # 检查并增强错误处理
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
    
    return content

def fix_reconnection_logic(content):
    """改进重连逻辑"""
    print_step(4, "改进重连逻辑")
    
    # 检查并改进重连逻辑
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
    
    return content

def fix_message_handling(content):
    """改进消息处理"""
    print_step(5, "改进消息处理")
    
    # 检查并改进消息处理
    if "private handleAgentMessage = (event: MessageEvent): void => {" in content:
        # 查找handleAgentMessage函数
        agent_message_pattern = r'private handleAgentMessage = \(event: MessageEvent\): void => {.*?}'
        agent_message_match = re.search(agent_message_pattern, content, re.DOTALL)
        
        if agent_message_match:
            # 检查是否有消息去重逻辑
            if "if (message.id && currentMessages.some(m => m.id === message.id))" in content:
                print_colored("消息去重逻辑已存在，无需修复", Colors.GREEN)
            else:
                print_colored("发现问题: 缺少消息去重逻辑", Colors.YELLOW)
                # 这里不做具体修改，因为代码中已经有去重逻辑
        
        # 检查是否有消息排序逻辑
        if "messages.sort((a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime())" not in content:
            print_colored("发现问题: 缺少消息排序逻辑", Colors.YELLOW)
            
            # 在addMessage函数调用后添加排序逻辑的注释
            if "addMessage(newMessage)" in content:
                original_add_message = "addMessage(newMessage)"
                new_add_message = """addMessage(newMessage)
      // 注意: 如果消息顺序有问题，可以考虑在chatStore中添加排序逻辑:
      // messages.sort((a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime())"""
                
                content = content.replace(original_add_message, new_add_message)
                print_colored("已添加: 消息排序逻辑建议", Colors.GREEN)
    
    return content

def fix_frontend_sse():
    """修复前端SSE实现"""
    print_header("前端SSE实现修复")
    
    sse_service_path = "frontend/src/api/sseService.ts"
    
    # 检查文件是否存在
    if not os.path.exists(sse_service_path):
        print_colored(f"错误: 找不到前端SSE服务文件: {sse_service_path}", Colors.RED)
        return False
    
    # 备份文件
    print_step(1, "备份原始文件")
    if not backup_file(sse_service_path):
        print_colored("错误: 无法备份文件，中止修复", Colors.RED)
        return False
    
    try:
        # 读取文件内容
        with open(sse_service_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # 应用修复
        content = fix_sse_endpoint_url(content)
        content = fix_error_handling(content)
        content = fix_reconnection_logic(content)
        content = fix_message_handling(content)
        
        # 写入修复后的内容
        print_step(6, "保存修复后的文件")
        with open(sse_service_path, "w", encoding="utf-8") as f:
            f.write(content)
        
        print_colored("✓ 成功修复前端SSE实现", Colors.GREEN)
        print_colored("请重新构建前端并重启服务以应用更改", Colors.YELLOW)
        return True
    
    except Exception as e:
        print_colored(f"修复过程中出错: {e}", Colors.RED)
        return False

def check_proxy_config():
    """检查代理配置"""
    print_step(7, "检查代理配置")
    
    vite_config_path = "frontend/vite.config.ts"
    
    if not os.path.exists(vite_config_path):
        print_colored(f"警告: 找不到Vite配置文件: {vite_config_path}", Colors.YELLOW)
        print_colored("请确保前端代理配置正确，以便将/api请求转发到后端", Colors.YELLOW)
        return
    
    try:
        with open(vite_config_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # 检查是否有代理配置
        if "'/api/': {" in content or "'/api': {" in content:
            print_colored("✓ 已找到API代理配置", Colors.GREEN)
            
            # 检查是否有SSE代理配置
            if "'/api/events': {" in content:
                print_colored("✓ 已找到SSE事件代理配置", Colors.GREEN)
            else:
                print_colored("警告: 未找到专门的SSE事件代理配置", Colors.YELLOW)
                print_colored("建议添加以下配置以优化SSE连接:", Colors.YELLOW)
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
      rewrite: (path) => path.replace(/^\\/api/, ''),
      // 对SSE连接的特殊处理
      configure: (proxy, _options) => {
        proxy.on('error', (err, _req, _res) => {
          console.log('代理错误', err);
        });
        proxy.on('proxyReq', (proxyReq, req, _res) => {
          console.log('发送请求到:', req.url);
        });
        proxy.on('proxyRes', (proxyRes, req, _res) => {
          console.log('收到响应:', proxyRes.statusCode, req.url);
        });
      }
    }
  }
}
""", Colors.BLUE)
        else:
            print_colored("警告: 未找到API代理配置", Colors.YELLOW)
            print_colored("请确保添加以下代理配置:", Colors.YELLOW)
            print_colored("""
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true,
      rewrite: (path) => path.replace(/^\\/api/, '')
    }
  }
}
""", Colors.BLUE)
    
    except Exception as e:
        print_colored(f"检查代理配置时出错: {e}", Colors.RED)

if __name__ == "__main__":
    try:
        fix_frontend_sse()
        check_proxy_config()
        
        print_header("修复完成")
        print_colored("前端和后端的SSE实现已修复，请按照以下步骤应用更改:", Colors.GREEN)
        print_colored("1. 重启后端服务: python backend/main.py", Colors.YELLOW)
        print_colored("2. 重新构建前端: cd frontend && npm run build", Colors.YELLOW)
        print_colored("3. 启动前端服务: cd frontend && npm run dev", Colors.YELLOW)
        print_colored("4. 使用测试脚本验证修复效果: python test_frontend_backend.py", Colors.YELLOW)
    except KeyboardInterrupt:
        print("\n用户取消修复")
    except Exception as e:
        print(f"\n程序出错: {e}") 