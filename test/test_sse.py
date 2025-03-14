#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
SSE事件流测试脚本
专门用于测试SSE连接和消息接收
"""

import requests
import json
import asyncio
import aiohttp
import sys
import time
from datetime import datetime

# 后端API基础URL
BASE_URL = "http://localhost:8000"
# SSE事件流URL
SSE_URL = f"{BASE_URL}/api/events"

# 颜色输出
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def log(message, color=Colors.BLUE):
    """打印带颜色的日志"""
    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    print(f"{color}[{timestamp}] {message}{Colors.ENDC}")

def log_error(message):
    """打印错误日志"""
    log(f"错误: {message}", Colors.RED)

def log_success(message):
    """打印成功日志"""
    log(f"成功: {message}", Colors.GREEN)

def log_warning(message):
    """打印警告日志"""
    log(f"警告: {message}", Colors.YELLOW)

def log_info(message):
    """打印信息日志"""
    log(f"信息: {message}", Colors.BLUE)

def log_event(message):
    """打印事件日志"""
    log(f"事件: {message}", Colors.PURPLE)

async def listen_sse():
    """监听SSE事件流"""
    log(f"连接SSE事件流: {SSE_URL}")
    
    try:
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(SSE_URL) as response:
                    if response.status == 200:
                        log_success("成功连接到SSE事件流")
                        
                        # 持续读取事件
                        while True:
                            try:
                                line = await response.content.readline()
                                if not line:
                                    log_warning("SSE连接已关闭")
                                    break
                                
                                line = line.decode('utf-8').strip()
                                if line:
                                    log_event(f"收到事件: {line}")
                                    
                                    # 检查是否是心跳消息
                                    if line.startswith(':'):
                                        log_info("收到心跳消息")
                                        continue
                                    
                                    # 解析事件类型和数据
                                    if line.startswith('event:'):
                                        event_type = line.replace('event:', '').strip()
                                        log_info(f"事件类型: {event_type}")
                                    elif line.startswith('data:'):
                                        data = line.replace('data:', '').strip()
                                        try:
                                            json_data = json.loads(data)
                                            log_info(f"事件数据: {json.dumps(json_data, ensure_ascii=False, indent=2)}")
                                        except json.JSONDecodeError:
                                            log_warning(f"无法解析JSON数据: {data}")
                            except asyncio.CancelledError:
                                log_warning("SSE监听被取消")
                                break
                            except Exception as e:
                                log_error(f"处理SSE事件时出错: {e}")
                    else:
                        log_error(f"SSE连接失败，状态码: {response.status}")
            except aiohttp.ClientConnectorError:
                log_error(f"无法连接到SSE服务器: {SSE_URL}")
            except Exception as e:
                log_error(f"SSE连接出错: {e}")
    except Exception as e:
        log_error(f"SSE监听出错: {e}")

async def start_simulation():
    """启动模拟"""
    url = f"{BASE_URL}/api/scenarios"
    log_info(f"获取场景列表: {url}")
    
    try:
        response = requests.get(url)
        if response.status_code != 200:
            log_error(f"获取场景列表失败，状态码: {response.status_code}")
            return False
        
        scenarios = response.json()
        if not scenarios or len(scenarios) == 0:
            log_error("没有可用的场景")
            return False
        
        scenario_id = scenarios[0]["id"]
        log_info(f"使用场景: {scenario_id}")
        
        url = f"{BASE_URL}/api/simulation/start"
        log_info(f"启动模拟: {url}")
        
        response = requests.post(url, json={"scenario_id": scenario_id})
        if response.status_code != 200:
            log_error(f"启动模拟失败，状态码: {response.status_code}")
            return False
        
        result = response.json()
        if not result.get("success"):
            log_error(f"启动模拟失败: {result.get('message', '未知错误')}")
            return False
        
        log_success("模拟启动成功")
        return True
    except Exception as e:
        log_error(f"启动模拟时出错: {e}")
        return False

async def stop_simulation():
    """停止模拟"""
    url = f"{BASE_URL}/api/simulation/stop"
    log_info(f"停止模拟: {url}")
    
    try:
        response = requests.post(url)
        if response.status_code != 200:
            log_error(f"停止模拟失败，状态码: {response.status_code}")
            return False
        
        result = response.json()
        if not result.get("success"):
            log_error(f"停止模拟失败: {result.get('message', '未知错误')}")
            return False
        
        log_success("模拟停止成功")
        return True
    except Exception as e:
        log_error(f"停止模拟时出错: {e}")
        return False

async def main():
    """主函数"""
    print(f"\n{Colors.BOLD}{'='*80}{Colors.ENDC}")
    print(f"{Colors.BOLD}{'SSE事件流测试'.center(80)}{Colors.ENDC}")
    print(f"{Colors.BOLD}{'='*80}{Colors.ENDC}\n")
    
    # 检查后端是否运行
    try:
        response = requests.get(f"{BASE_URL}/api/scenarios")
        if response.status_code != 200:
            log_error(f"后端服务可能未运行，状态码: {response.status_code}")
            return
    except requests.exceptions.ConnectionError:
        log_error(f"无法连接到后端服务: {BASE_URL}")
        log_info("请确保后端服务已启动，然后再运行此测试脚本")
        return
    
    # 创建任务
    sse_task = asyncio.create_task(listen_sse())
    
    # 等待SSE连接建立
    await asyncio.sleep(2)
    
    # 启动模拟
    success = await start_simulation()
    if not success:
        sse_task.cancel()
        return
    
    try:
        # 等待一段时间，观察消息
        log_info("等待接收消息，按Ctrl+C取消...")
        await asyncio.sleep(60)
    except KeyboardInterrupt:
        log_warning("用户取消")
    finally:
        # 停止模拟
        await stop_simulation()
        
        # 取消SSE任务
        sse_task.cancel()
        try:
            await sse_task
        except asyncio.CancelledError:
            pass

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n用户取消")
    except Exception as e:
        print(f"\n程序出错: {e}") 