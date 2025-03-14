#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
日志检查脚本
用于分析后端日志文件，查找错误和问题
"""

import os
import re
import sys
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

def print_section(message):
    """打印小节标题"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{message}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'-'*len(message)}{Colors.ENDC}\n")

def analyze_log_file(log_file):
    """分析日志文件"""
    if not os.path.exists(log_file):
        print_colored(f"日志文件不存在: {log_file}", Colors.RED)
        return
    
    print_colored(f"分析日志文件: {log_file}", Colors.BLUE)
    print_colored(f"文件大小: {os.path.getsize(log_file) / 1024:.2f} KB", Colors.BLUE)
    print_colored(f"最后修改时间: {datetime.fromtimestamp(os.path.getmtime(log_file))}", Colors.BLUE)
    
    # 读取日志文件
    with open(log_file, 'r', encoding='utf-8') as f:
        log_content = f.read()
    
    # 统计信息
    lines = log_content.splitlines()
    print_colored(f"总行数: {len(lines)}", Colors.BLUE)
    
    # 错误和警告计数
    error_count = 0
    warning_count = 0
    info_count = 0
    
    # 错误和警告列表
    errors = []
    warnings = []
    
    # 消息发送统计
    message_sent_count = 0
    message_received_count = 0
    
    # 连接统计
    connection_count = 0
    disconnection_count = 0
    
    # 模拟启动和停止
    simulation_start_count = 0
    simulation_stop_count = 0
    
    # 分析每一行
    for line in lines:
        # 日志级别
        if " - ERROR - " in line:
            error_count += 1
            errors.append(line)
        elif " - WARNING - " in line:
            warning_count += 1
            warnings.append(line)
        elif " - INFO - " in line:
            info_count += 1
        
        # 消息发送
        if "发送消息:" in line or "消息已发送:" in line:
            message_sent_count += 1
        
        # 消息接收
        if "处理消息:" in line:
            message_received_count += 1
        
        # 连接
        if "客户端连接:" in line:
            connection_count += 1
        
        # 断开连接
        if "客户端断开连接:" in line:
            disconnection_count += 1
        
        # 模拟启动
        if "开始模拟:" in line:
            simulation_start_count += 1
        
        # 模拟停止
        if "模拟完全结束" in line:
            simulation_stop_count += 1
    
    # 打印统计信息
    print_section("日志统计")
    print_colored(f"信息日志: {info_count}", Colors.GREEN)
    print_colored(f"警告日志: {warning_count}", Colors.YELLOW)
    print_colored(f"错误日志: {error_count}", Colors.RED)
    
    print_section("消息统计")
    print_colored(f"发送消息: {message_sent_count}", Colors.GREEN)
    print_colored(f"接收消息: {message_received_count}", Colors.GREEN)
    
    print_section("连接统计")
    print_colored(f"客户端连接: {connection_count}", Colors.GREEN)
    print_colored(f"客户端断开: {disconnection_count}", Colors.GREEN)
    
    print_section("模拟统计")
    print_colored(f"模拟启动: {simulation_start_count}", Colors.GREEN)
    print_colored(f"模拟停止: {simulation_stop_count}", Colors.GREEN)
    
    # 打印错误
    if errors:
        print_section("错误日志")
        for i, error in enumerate(errors[-10:], 1):  # 只显示最后10条
            print_colored(f"{i}. {error}", Colors.RED)
        
        if len(errors) > 10:
            print_colored(f"... 还有 {len(errors) - 10} 条错误未显示", Colors.YELLOW)
    
    # 打印警告
    if warnings:
        print_section("警告日志")
        for i, warning in enumerate(warnings[-10:], 1):  # 只显示最后10条
            print_colored(f"{i}. {warning}", Colors.YELLOW)
        
        if len(warnings) > 10:
            print_colored(f"... 还有 {len(warnings) - 10} 条警告未显示", Colors.YELLOW)
    
    # 分析问题
    print_section("问题分析")
    
    if error_count > 0:
        print_colored("发现错误日志，请检查上面的错误详情", Colors.RED)
    
    if message_sent_count == 0:
        print_colored("没有发送任何消息，可能存在消息发送问题", Colors.RED)
    
    if message_received_count == 0:
        print_colored("没有接收任何消息，可能存在消息接收问题", Colors.RED)
    
    if connection_count == 0:
        print_colored("没有客户端连接记录，可能存在SSE连接问题", Colors.RED)
    
    if simulation_start_count > simulation_stop_count:
        print_colored("有模拟未正常结束，可能存在模拟中断问题", Colors.YELLOW)
    
    if error_count == 0 and warning_count == 0 and message_sent_count > 0 and connection_count > 0:
        print_colored("日志分析未发现明显问题", Colors.GREEN)

def main():
    """主函数"""
    print_header("后端日志分析")
    
    # 检查后端日志文件
    backend_log = "backend/simulation.log"
    if os.path.exists(backend_log):
        analyze_log_file(backend_log)
    else:
        print_colored(f"后端日志文件不存在: {backend_log}", Colors.RED)
        
        # 尝试查找其他日志文件
        print_colored("尝试查找其他日志文件...", Colors.YELLOW)
        log_files = []
        
        # 检查当前目录
        for file in os.listdir("."):
            if file.endswith(".log"):
                log_files.append(file)
        
        # 检查backend目录
        if os.path.exists("backend"):
            for file in os.listdir("backend"):
                if file.endswith(".log"):
                    log_files.append(os.path.join("backend", file))
        
        if log_files:
            print_colored(f"找到 {len(log_files)} 个日志文件:", Colors.GREEN)
            for i, log_file in enumerate(log_files, 1):
                print_colored(f"{i}. {log_file}", Colors.GREEN)
            
            # 分析找到的第一个日志文件
            print_colored(f"\n分析第一个日志文件: {log_files[0]}", Colors.BLUE)
            analyze_log_file(log_files[0])
        else:
            print_colored("未找到任何日志文件", Colors.RED)

if __name__ == "__main__":
    main() 