#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
启动多智能体交互系统（React + FastAPI版本）
"""

import os
import sys
import subprocess
import socket
import time
import webbrowser
import shutil
import locale
import codecs

def find_free_port(start_port=8000, max_port=8099):
    """查找可用端口"""
    for port in range(start_port, max_port + 1):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(('localhost', port)) != 0:
                return port
    return None

def check_file_exists(file_path):
    """检查文件是否存在"""
    exists = os.path.exists(file_path)
    print(f"检查文件 {file_path}: {'存在' if exists else '不存在'}")
    return exists

def check_command_exists(command):
    """检查命令是否存在"""
    cmd_path = shutil.which(command)
    print(f"检查命令 {command}: {'存在，路径为 ' + cmd_path if cmd_path else '不存在'}")
    return cmd_path is not None

def run_command(cmd, cwd=None, check=True):
    """运行命令并返回结果"""
    print(f"运行命令: {' '.join(cmd)}")
    try:
        result = subprocess.run(cmd, cwd=cwd, check=check, capture_output=True, text=True, encoding='utf-8')
        return result
    except subprocess.CalledProcessError as e:
        print(f"命令执行失败: {e}")
        print(f"错误输出: {e.stderr}")
        if check:
            raise
        return e

def ensure_env_file(current_dir):
    """确保.env文件存在"""
    env_file = os.path.join(current_dir, ".env")
    env_example_file = os.path.join(current_dir, ".env.example")
    
    if check_file_exists(env_file):
        print(".env文件已存在")
        return True
    
    if check_file_exists(env_example_file):
        print("正在从.env.example创建.env文件...")
        try:
            with open(env_example_file, 'r', encoding='utf-8') as example_file:
                example_content = example_file.read()
            
            with open(env_file, 'w', encoding='utf-8') as env_file_obj:
                env_file_obj.write(example_content)
            
            print(".env文件已创建，请检查并填写正确的API密钥")
            return True
        except Exception as e:
            print(f"创建.env文件失败: {e}")
            return False
    else:
        print("错误: 未找到.env或.env.example文件")
        return False

# 安全的读取行函数，处理各种编码问题
def safe_readline(stream):
    """安全地读取一行，处理各种编码问题"""
    try:
        line = stream.readline()
        return line
    except UnicodeDecodeError:
        # 尝试使用不同的编码
        try:
            # 获取原始字节
            raw_line = stream._buffer.readline()
            # 尝试用不同的编码解码
            for encoding in ['utf-8', 'gbk', 'latin1', 'cp1252']:
                try:
                    return raw_line.decode(encoding)
                except UnicodeDecodeError:
                    continue
            # 如果所有编码都失败，使用replace模式
            return raw_line.decode('utf-8', errors='replace')
        except Exception as e:
            return f"[无法解码的输出: {str(e)}]\n"

def main():
    """启动应用"""
    print("正在启动多智能体交互系统...")
    print(f"系统默认编码: {locale.getpreferredencoding()}")
    
    # 设置环境变量，强制使用UTF-8
    os.environ["PYTHONIOENCODING"] = "utf-8"
    
    # 获取当前脚本所在目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    print(f"当前工作目录: {current_dir}")
    
    # 清除旧的日志文件
    log_file = os.path.join(current_dir, "simulation.log")
    if os.path.exists(log_file):
        print(f"清除旧的日志文件: {log_file}")
        try:
            with open(log_file, 'w') as f:
                f.write("")
            print("日志文件已清除")
        except Exception as e:
            print(f"清除日志文件失败: {e}")
    
    # 确保.env文件存在
    if not ensure_env_file(current_dir):
        print("无法继续，请手动创建.env文件")
        return
    
    # 检查目录结构
    backend_dir = os.path.join(current_dir, "backend")
    frontend_dir = os.path.join(current_dir, "frontend")
    
    print(f"后端目录: {backend_dir}")
    print(f"前端目录: {frontend_dir}")
    
    if not os.path.isdir(backend_dir):
        print(f"错误: 后端目录不存在: {backend_dir}")
        return
    
    if not os.path.isdir(frontend_dir):
        print(f"错误: 前端目录不存在: {frontend_dir}")
        return
    
    # 检查关键文件
    backend_main = os.path.join(backend_dir, "main.py")
    frontend_package = os.path.join(frontend_dir, "package.json")
    
    if not check_file_exists(backend_main):
        print(f"错误: 后端主文件不存在: {backend_main}")
        return
    
    if not check_file_exists(frontend_package):
        print(f"错误: 前端package.json不存在: {frontend_package}")
        return
    
    # 检查命令
    if not check_command_exists("npm"):
        print("错误: npm命令不存在，请确保已安装Node.js")
        return
    
    # 检查后端依赖
    backend_requirements = os.path.join(backend_dir, "requirements.txt")
    if check_file_exists(backend_requirements):
        print("安装后端依赖...")
        try:
            run_command([sys.executable, "-m", "pip", "install", "-r", backend_requirements])
        except Exception as e:
            print(f"安装后端依赖失败: {e}")
            return
    
    # 检查前端依赖
    frontend_node_modules = os.path.join(frontend_dir, "node_modules")
    if not os.path.isdir(frontend_node_modules):
        print("前端依赖未安装，正在安装...")
        try:
            run_command(["npm", "install"], cwd=frontend_dir)
        except Exception as e:
            print(f"安装前端依赖失败: {e}")
            return
    else:
        print("前端依赖已安装")
    
    # 查找可用端口
    backend_port = find_free_port(8000, 8099)
    frontend_port = find_free_port(3000, 3099)
    
    if not backend_port or not frontend_port:
        print("无法找到可用端口，请手动关闭占用端口的应用后重试")
        return
    
    print(f"后端使用端口: {backend_port}")
    print(f"前端使用端口: {frontend_port}")
    
    # 启动后端
    backend_cmd = [sys.executable, backend_main]
    print(f"后端启动命令: {' '.join(backend_cmd)}")
    
    # 启动前端
    if os.name == 'nt':  # Windows
        frontend_cmd = ["npm", "run", "dev", "--", "--port", str(frontend_port)]
    else:  # Linux/Mac
        frontend_cmd = ["npm", "run", "dev", "--", "--port", str(frontend_port)]
    
    print(f"前端启动命令: {' '.join(frontend_cmd)}")
    
    try:
        print("正在启动后端服务...")
        # 设置编码为UTF-8
        backend_process = subprocess.Popen(
            backend_cmd,
            cwd=backend_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            encoding='utf-8'  # 明确指定UTF-8编码
        )
        
        # 等待后端启动
        time.sleep(2)
        
        # 检查后端进程是否正常
        if backend_process.poll() is not None:
            print(f"错误: 后端进程启动失败，退出码: {backend_process.poll()}")
            output, _ = backend_process.communicate()
            print(f"后端输出: {output}")
            return
        
        print("正在启动前端服务...")
        # 修改前端启动方式，在Windows上使用shell=True
        if os.name == 'nt':  # Windows
            # 设置环境变量，确保子进程使用UTF-8编码
            env = os.environ.copy()
            env["PYTHONIOENCODING"] = "utf-8"
            
            frontend_cmd_str = f"npm run dev -- --port {frontend_port}"
            frontend_process = subprocess.Popen(
                frontend_cmd_str,
                cwd=frontend_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                shell=True,
                encoding='utf-8',  # 明确指定UTF-8编码
                env=env  # 传递修改后的环境变量
            )
        else:  # Linux/Mac
            frontend_process = subprocess.Popen(
                frontend_cmd,
                cwd=frontend_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                encoding='utf-8'  # 明确指定UTF-8编码
            )
        
        # 检查前端进程是否正常
        time.sleep(2)
        if frontend_process.poll() is not None:
            print(f"错误: 前端进程启动失败，退出码: {frontend_process.poll()}")
            output, _ = frontend_process.communicate()
            print(f"前端输出: {output}")
            return
        
        # 等待前端启动
        time.sleep(3)
        
        # 打开浏览器
        webbrowser.open(f"http://localhost:{frontend_port}")
        
        print(f"应用已启动，请访问: http://localhost:{frontend_port}")
        print("按Ctrl+C停止服务...")
        
        # 输出进程日志
        while True:
            try:
                backend_line = safe_readline(backend_process.stdout)
                if backend_line:
                    print(f"[后端] {backend_line.strip()}")
                
                frontend_line = safe_readline(frontend_process.stdout)
                if frontend_line:
                    print(f"[前端] {frontend_line.strip()}")
                
                if not backend_line and not frontend_line:
                    if backend_process.poll() is not None and frontend_process.poll() is not None:
                        break
                    time.sleep(0.1)
            except Exception as e:
                print(f"处理进程输出时出错: {e}")
                time.sleep(0.1)
                continue
    
    except KeyboardInterrupt:
        print("\n正在停止服务...")
    except Exception as e:
        print(f"启动应用时出错: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # 停止进程
        try:
            if 'backend_process' in locals():
                backend_process.terminate()
            if 'frontend_process' in locals():
                frontend_process.terminate()
        except Exception as e:
            print(f"停止服务时出错: {e}")
        
        print("应用已停止")

if __name__ == "__main__":
    main() 