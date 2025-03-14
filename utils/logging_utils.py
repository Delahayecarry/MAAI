"""
日志记录工具
"""
import json
import os
from datetime import datetime
import time
import sys
import random

def save_conversation(messages, filename):
    """
    保存对话到JSON文件
    
    参数:
        messages (list): 消息列表
        filename (str): 输出文件名
    """
    # 确保输出目录存在
    os.makedirs("conversations_log", exist_ok=True)
    
    # 格式化消息以便于阅读
    formatted_messages = []
    for msg in messages:
        formatted_messages.append({
            "sender": msg.get("name", "Unknown"),
            "content": msg.get("content", ""),
            "timestamp": datetime.now().isoformat()
        })
    
    # 保存到文件
    output_file = os.path.join("conversations_log", filename)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(formatted_messages, f, ensure_ascii=False, indent=2)
    
    print(f"对话已保存到: {output_file}")

def load_conversation(filename):
    """
    从JSON文件加载对话
    
    参数:
        filename (str): 输入文件名
    
    返回:
        list: 消息列表
    """
    input_file = os.path.join("conversations_log", filename)
    
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"文件未找到: {input_file}")
        return []

def fake_stream_output(text, min_delay=0.01, max_delay=0.05, end_delay=0.5):
    """
    模拟流式输出效果
    
    参数:
        text (str): 要输出的文本
        min_delay (float): 字符间最小延迟时间（秒）
        max_delay (float): 字符间最大延迟时间（秒）
        end_delay (float): 段落结束后的延迟时间（秒）
    """
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        
        # 根据字符类型调整延迟
        if char in ['.', '!', '?', '。', '！', '？']:
            time.sleep(end_delay)  # 句子结束后稍长的停顿
        elif char in [',', ';', '，', '；', '、']:
            time.sleep(max_delay)  # 逗号等标点后中等停顿
        elif char in ['\n', '\r']:
            time.sleep(end_delay * 1.5)  # 换行后较长停顿
        else:
            time.sleep(random.uniform(min_delay, max_delay))  # 普通字符随机延迟

def format_agent_message(agent_name, display_name, message, stream=True):
    """
    格式化代理消息并输出
    
    参数:
        agent_name (str): 代理的英文名称
        display_name (str): 代理的显示名称（中文）
        message (str): 消息内容
        stream (bool): 是否使用伪流式输出
    """
    header = f"\n{display_name} ({agent_name}):\n"
    separator = "-" * 80
    
    print(header)
    print(separator)
    
    if stream:
        fake_stream_output(message)
    else:
        print(message)
    
    print(f"\n{separator}\n") 