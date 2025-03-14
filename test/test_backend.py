#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
后端功能测试脚本
用于测试后端API和SSE事件流
"""

import requests
import json
import time
import asyncio
import aiohttp
import sys
import os
from datetime import datetime

# 后端API基础URL
BASE_URL = "http://localhost:8000"

# 测试颜色输出
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(message):
    """打印带颜色的标题"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{message.center(80)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.ENDC}\n")

def print_success(message):
    """打印成功消息"""
    print(f"{Colors.OKGREEN}✓ {message}{Colors.ENDC}")

def print_error(message):
    """打印错误消息"""
    print(f"{Colors.FAIL}✗ {message}{Colors.ENDC}")

def print_warning(message):
    """打印警告消息"""
    print(f"{Colors.WARNING}! {message}{Colors.ENDC}")

def print_info(message):
    """打印信息消息"""
    print(f"{Colors.OKBLUE}ℹ {message}{Colors.ENDC}")

def test_api_endpoint(endpoint, method="GET", data=None):
    """测试API端点"""
    url = f"{BASE_URL}{endpoint}"
    print_info(f"测试 {method} {url}")
    
    try:
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data)
        else:
            print_error(f"不支持的HTTP方法: {method}")
            return None
        
        if response.status_code == 200:
            print_success(f"状态码: {response.status_code}")
            try:
                result = response.json()
                print_info(f"响应: {json.dumps(result, ensure_ascii=False, indent=2)}")
                return result
            except json.JSONDecodeError:
                print_warning(f"响应不是有效的JSON: {response.text}")
                return response.text
        else:
            print_error(f"状态码: {response.status_code}")
            print_error(f"响应: {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        print_error(f"请求异常: {e}")
        return None

async def test_sse_events():
    """测试SSE事件流"""
    url = f"{BASE_URL}/events"
    print_info(f"连接SSE事件流: {url}")
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    print_error(f"SSE连接失败，状态码: {response.status}")
                    return
                
                print_success("SSE连接成功")
                print_info("等待事件...")
                
                # 设置超时时间（秒）
                timeout = 30
                start_time = time.time()
                
                # 计数器
                event_count = 0
                message_count = 0
                
                # 读取事件流
                while True:
                    if time.time() - start_time > timeout:
                        print_warning(f"超过 {timeout} 秒未收到新事件，退出监听")
                        break
                    
                    try:
                        line = await asyncio.wait_for(response.content.readline(), timeout=1.0)
                        if not line:
                            continue
                        
                        line = line.decode('utf-8').strip()
                        if not line:
                            continue
                        
                        # 心跳消息
                        if line == ":":
                            print_info("收到心跳消息")
                            continue
                        
                        # 事件类型
                        if line.startswith("event:"):
                            event_type = line.replace("event:", "").strip()
                            print_info(f"事件类型: {event_type}")
                            continue
                        
                        # 事件数据
                        if line.startswith("data:"):
                            event_count += 1
                            data_str = line.replace("data:", "").strip()
                            try:
                                data = json.loads(data_str)
                                if "sender" in data and "content" in data:
                                    message_count += 1
                                    print_success(f"收到消息 #{message_count}: {data['sender']} - {data['content'][:50]}...")
                                else:
                                    print_info(f"收到事件数据: {json.dumps(data, ensure_ascii=False)}")
                            except json.JSONDecodeError:
                                print_warning(f"无法解析事件数据: {data_str}")
                            
                            # 重置超时计时器
                            start_time = time.time()
                            continue
                    except asyncio.TimeoutError:
                        # 超时只是意味着没有新数据，继续等待
                        continue
                    except Exception as e:
                        print_error(f"读取事件流时出错: {e}")
                        break
    except aiohttp.ClientError as e:
        print_error(f"SSE连接异常: {e}")

async def run_tests():
    """运行所有测试"""
    print_header("后端功能测试")
    
    # 测试获取场景列表
    print_header("测试获取场景列表")
    scenarios = test_api_endpoint("/api/scenarios")
    
    if not scenarios:
        print_error("获取场景列表失败，无法继续测试")
        return
    
    # 测试启动模拟
    print_header("测试启动模拟")
    if scenarios and len(scenarios) > 0:
        scenario_id = scenarios[0]["id"]
        print_info(f"使用场景: {scenario_id}")
        
        start_result = test_api_endpoint(
            "/api/simulation/start", 
            method="POST", 
            data={"scenario_id": scenario_id}
        )
        
        if start_result and start_result.get("success"):
            print_success("模拟启动成功")
            
            # 测试SSE事件流
            print_header("测试SSE事件流")
            await test_sse_events()
            
            # 测试停止模拟
            print_header("测试停止模拟")
            stop_result = test_api_endpoint("/api/simulation/stop", method="POST")
            
            if stop_result and stop_result.get("success"):
                print_success("模拟停止成功")
            else:
                print_error("模拟停止失败")
        else:
            print_error("模拟启动失败")
    else:
        print_error("没有可用的场景")
    
    # 测试获取历史记录
    print_header("测试获取历史记录")
    history_list = test_api_endpoint("/api/history")
    
    if history_list and len(history_list) > 0:
        print_success(f"获取到 {len(history_list)} 条历史记录")
        
        # 测试获取特定历史记录
        print_header("测试获取特定历史记录")
        history_id = history_list[0]["id"]
        print_info(f"获取历史记录: {history_id}")
        
        history_detail = test_api_endpoint(f"/api/history/{history_id}")
        
        if history_detail:
            print_success(f"获取到历史记录详情，包含 {len(history_detail)} 条消息")
        else:
            print_error("获取历史记录详情失败")
    else:
        print_warning("没有历史记录或获取失败")
    
    print_header("测试完成")

if __name__ == "__main__":
    # 检查后端是否运行
    try:
        response = requests.get(f"{BASE_URL}/api/scenarios")
        if response.status_code != 200:
            print_error(f"后端服务可能未运行，状态码: {response.status_code}")
            sys.exit(1)
    except requests.exceptions.ConnectionError:
        print_error(f"无法连接到后端服务: {BASE_URL}")
        print_info("请确保后端服务已启动，然后再运行此测试脚本")
        sys.exit(1)
    
    # 运行测试
    asyncio.run(run_tests()) 