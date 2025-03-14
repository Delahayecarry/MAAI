"""
多智能体交互系统后端
使用 AutoGen 0.4 API 实现的多智能体对话系统
"""
import os
import sys
import json
import asyncio
import logging
import traceback
from datetime import datetime
from typing import List, Dict, Any, Optional, Sequence
from fastapi import FastAPI, HTTPException, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import uvicorn
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 导入自定义模块
sys_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if sys_path not in sys.path:
    sys.path.append(sys_path)

# 导入 AutoGen 0.4 组件
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.messages import TextMessage
from autogen_core import CancellationToken
from autogen_core.models import UserMessage, AssistantMessage

# 导入自定义模块
from agents.manager import create_manager_agent
from agents.developer import create_developer_agent
from agents.designer import create_designer_agent
from utils.logging_utils import save_conversation
from conversations.scenarios import get_scenario, list_scenarios

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("simulation.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# 创建FastAPI应用
app = FastAPI(title="多智能体交互系统API")

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该限制为特定域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 数据模型
class ScenarioModel(BaseModel):
    id: str
    name: str
    description: str

class SimulationRequest(BaseModel):
    scenario_id: str

class SimulationResponse(BaseModel):
    success: bool
    message: str

# 全局变量
active_simulation = None
connected_clients = set()
simulation_task = None
message_history = []

# SSE事件队列
event_queue = asyncio.Queue()

# 智能体显示名称映射
AGENT_DISPLAY_NAMES = {
    "Manager": "经理",
    "SeniorDev": "资深开发",
    "JuniorDev": "初级开发",
    "Designer": "设计师",
    "System": "系统"
}

# 获取所有场景
@app.get("/api/scenarios", response_model=List[ScenarioModel])
async def get_scenarios():
    """获取所有可用场景"""
    try:
        logger.info("获取场景列表")
        # 从scenarios模块获取场景列表
        from conversations.scenarios import SCENARIOS
        
        scenarios = []
        
        # 场景名称和描述映射
        scenario_descriptions = {
            "team_meeting": "团队成员讨论项目进展和问题",
            "technical_discussion": "讨论项目技术栈选择",
            "design_review": "团队评审设计方案",
            "conflict_resolution": "解决团队成员之间的冲突",
            "casual_chat": "团队成员的轻松对话"
        }
        
        # 场景显示名称映射
        scenario_display_names = {
            "team_meeting": "团队会议",
            "technical_discussion": "技术讨论",
            "design_review": "设计评审",
            "conflict_resolution": "冲突解决",
            "casual_chat": "休闲聊天"
        }
        
        for scenario_id in SCENARIOS.keys():
            scenarios.append({
                "id": scenario_id,
                "name": scenario_display_names.get(scenario_id, scenario_id),
                "description": scenario_descriptions.get(scenario_id, "")
            })
        
        logger.info(f"返回 {len(scenarios)} 个场景")
        return scenarios
    except Exception as e:
        logger.error(f"获取场景列表时出错: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# 启动模拟
@app.post("/api/simulation/start", response_model=SimulationResponse)
async def start_simulation(request: SimulationRequest, background_tasks: BackgroundTasks):
    """启动模拟对话"""
    global active_simulation, simulation_task, message_history
    
    if active_simulation:
        logger.warning("尝试启动模拟，但已有模拟正在运行")
        return {"success": False, "message": "已有模拟正在运行"}
    
    try:
        # 获取场景
        logger.info(f"获取场景: {request.scenario_id}")
        scenario_text = get_scenario(request.scenario_id)
        if not scenario_text:
            logger.error(f"未找到指定场景: {request.scenario_id}")
            return {"success": False, "message": "未找到指定场景"}
        
        # 清空消息历史
        message_history = []
        
        # 在后台任务中运行模拟
        logger.info(f"启动模拟: {request.scenario_id}")
        background_tasks.add_task(run_simulation, request.scenario_id, scenario_text)
        
        return {"success": True, "message": "模拟已启动"}
    except Exception as e:
        logger.error(f"启动模拟时出错: {e}")
        return {"success": False, "message": f"启动模拟时出错: {str(e)}"}

# 停止模拟
@app.post("/api/simulation/stop", response_model=SimulationResponse)
async def stop_simulation():
    """停止当前运行的模拟"""
    global active_simulation, simulation_task
    
    if not active_simulation:
        logger.info("尝试停止模拟，但当前没有运行中的模拟")
        return {"success": True, "message": "当前没有运行中的模拟"}
    
    try:
        logger.info("停止模拟")
        if simulation_task and not simulation_task.done():
            simulation_task.cancel()
        
        active_simulation = None
        
        # 发送模拟状态更新
        await event_queue.put({
            "event": "simulation_status",
            "data": {"is_running": False}
        })
        
        return {"success": True, "message": "模拟已停止"}
    except Exception as e:
        logger.error(f"停止模拟时出错: {e}")
        return {"success": False, "message": f"停止模拟时出错: {str(e)}"}

# 获取历史对话列表
@app.get("/api/history")
async def get_history_list():
    """获取历史对话列表"""
    try:
        logger.info("获取历史对话列表")
        history_list = []
        conversations_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "conversations_log")
        
        if os.path.exists(conversations_dir):
            for file in os.listdir(conversations_dir):
                if file.endswith(".json"):
                    file_path = os.path.join(conversations_dir, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            
                            # 提取场景信息
                            scenario = "未知场景"
                            if data and len(data) > 0 and "content" in data[0]:
                                first_message = data[0]["content"]
                                if "团队会议" in first_message:
                                    scenario = "团队会议"
                                elif "技术讨论" in first_message:
                                    scenario = "技术讨论"
                                elif "设计评审" in first_message:
                                    scenario = "设计评审"
                                elif "冲突解决" in first_message:
                                    scenario = "冲突解决"
                                elif "休闲聊天" in first_message:
                                    scenario = "休闲聊天"
                            
                            # 提取时间戳
                            timestamp = datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat()
                            
                            history_list.append({
                                "id": file.replace(".json", ""),
                                "timestamp": timestamp,
                                "scenario": scenario
                            })
                    except Exception as e:
                        logger.error(f"读取历史对话文件 {file} 时出错: {e}")
        
        # 按时间戳降序排序
        history_list.sort(key=lambda x: x["timestamp"], reverse=True)
        
        logger.info(f"返回 {len(history_list)} 条历史记录")
        return history_list
    except Exception as e:
        logger.error(f"获取历史对话列表时出错: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# 获取特定历史对话
@app.get("/api/history/{history_id}")
async def get_history_by_id(history_id: str):
    """获取特定历史对话的详细内容"""
    try:
        logger.info(f"获取历史对话: {history_id}")
        file_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "conversations_log",
            f"{history_id}.json"
        )
        
        if not os.path.exists(file_path):
            logger.error(f"未找到历史对话: {history_id}")
            raise HTTPException(status_code=404, detail="未找到指定的历史对话")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
            # 转换为前端格式
            messages = []
            for msg in data:
                if "sender" in msg and "content" in msg:
                    messages.append({
                        "id": msg.get("id", str(len(messages))),
                        "sender": msg.get("sender", "Unknown"),
                        "sender_display_name": msg.get("sender_display_name", msg.get("sender", "未知")),
                        "content": msg.get("content", ""),
                        "timestamp": msg.get("timestamp", datetime.now().isoformat())
                    })
            
            logger.info(f"返回 {len(messages)} 条消息")
            return messages
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取历史对话 {history_id} 时出错: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# 手动发送智能体消息到前端
async def send_agent_message(agent_name: str, content: str) -> bool:
    """
    手动发送智能体消息到前端
    
    参数:
        agent_name: 智能体名称
        content: 消息内容
        
    返回:
        bool: 是否发送成功
    """
    try:
        # 获取显示名称
        display_name = AGENT_DISPLAY_NAMES.get(agent_name, agent_name)
        
        # 构造消息对象
        message_id = str(datetime.now().timestamp())
        timestamp = datetime.now().isoformat()
        
        sse_message = {
            "id": message_id,
            "sender": agent_name,
            "sender_display_name": display_name,
            "content": content,
            "timestamp": timestamp
        }
        
        # 添加到消息历史
        message_history.append(sse_message)
        
        # 发送到SSE事件队列
        logger.info(f"发送消息: {agent_name} ({display_name}): {content[:50]}...")
        await event_queue.put({
            "event": "agent_message",
            "data": sse_message
        })
        logger.info(f"消息已发送到SSE队列: {message_id}")
        return True
    except Exception as e:
        logger.error(f"发送消息失败: {e}")
        return False

# SSE事件流
@app.get("/api/events")
async def event_stream(request: Request):
    """SSE事件流，用于向前端推送实时消息"""
    async def generate():
        client_id = id(asyncio.current_task())
        connected_clients.add(client_id)
        logger.info(f"客户端连接: {client_id}")
        
        try:
            # 发送初始连接成功消息
            connection_message = f"data: {{\"event\": \"connected\", \"data\": {{\"client_id\": \"{client_id}\"}}}}\n\n"
            logger.info(f"发送连接消息: {client_id}")
            yield connection_message
            
            # 发送当前模拟状态
            status_message = f"event: simulation_status\ndata: {{\"is_running\": {json.dumps(active_simulation is not None)}}}\n\n"
            logger.info(f"发送状态消息: is_running={active_simulation is not None}")
            yield status_message
            
            # 发送测试消息
            test_message = {
                "id": str(datetime.now().timestamp()),
                "sender": "System",
                "sender_display_name": "系统",
                "content": "SSE连接已建立，等待智能体消息...",
                "timestamp": datetime.now().isoformat()
            }
            test_message_str = f"event: agent_message\ndata: {json.dumps(test_message)}\n\n"
            logger.info(f"发送测试消息")
            yield test_message_str
            
            # 持续监听事件队列
            while True:
                # 检查客户端是否断开连接
                if await request.is_disconnected():
                    logger.info(f"客户端断开连接: {client_id}")
                    break
                    
                try:
                    # 使用超时，以便可以检查客户端是否断开连接
                    event = await asyncio.wait_for(event_queue.get(), timeout=1.0)
                    
                    if "event" in event and "data" in event:
                        event_type = event["event"]
                        event_data = json.dumps(event["data"])
                        event_message = f"event: {event_type}\ndata: {event_data}\n\n"
                        logger.info(f"发送事件: {event_type}")
                        yield event_message
                except asyncio.TimeoutError:
                    # 发送心跳以保持连接
                    yield ":\n\n"
                except Exception as e:
                    logger.error(f"处理事件时出错: {e}")
                    error_message = f"event: error\ndata: {{\"message\": \"{str(e)}\"}}\n\n"
                    yield error_message
        finally:
            if client_id in connected_clients:
                connected_clients.remove(client_id)
                logger.info(f"客户端断开连接: {client_id}")
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "X-Accel-Buffering": "no"
        }
    )

# 运行模拟的后台任务
async def run_simulation(scenario_id: str, scenario_text: str):
    """
    运行模拟对话
    
    参数:
        scenario_id: 场景ID
        scenario_text: 场景文本
    """
    global active_simulation, simulation_task, message_history
    
    try:
        # 设置活动模拟
        active_simulation = scenario_id
        logger.info(f"开始模拟: {scenario_id}")
        
        # 发送模拟状态更新
        await event_queue.put({
            "event": "simulation_status",
            "data": {"is_running": True}
        })
        
        # 发送初始系统消息
        await send_agent_message("System", f"开始模拟场景: {scenario_id}")
        
        # 创建各种代理
        logger.info("创建智能体")
        manager = create_manager_agent(name="Manager", display_name="经理")
        senior_dev = create_developer_agent(
            name="SeniorDev",
            display_name="资深开发",
            traits="经验丰富、效率高、技术精湛",
            relationships={"经理": "受到赏识", "初级开发": "有些不耐烦"}
        )
        junior_dev = create_developer_agent(
            name="JuniorDev",
            display_name="初级开发",
            traits="有创意但经验不足、工作效率低",
            relationships={"经理": "感到压力", "资深开发": "有些敬畏"}
        )
        designer = create_designer_agent(
            name="Designer",
            display_name="设计师",
            traits="创意丰富、注重细节、有时固执己见",
            relationships={"经理": "关系中立", "资深开发": "配合良好", "初级开发": "友好"}
        )
        
        # 手动发送一些初始消息，确保前端能够接收到
        logger.info("发送初始消息")
        await send_agent_message("Manager", "大家好，我们今天讨论一下这个新项目。")
        await send_agent_message("SeniorDev", "好的，我已经看过需求文档了，这个项目需要在3个月内完成。")
        await send_agent_message("JuniorDev", "我对这个项目很感兴趣，希望能学到新技术。")
        await send_agent_message("Designer", "我已经准备了一些初步的设计方案，等会可以分享给大家。")
        
        # 创建消息处理函数
        async def process_message(message):
            """处理从AutoGen接收到的消息"""
            try:
                # 获取发送者信息
                source = message.source
                content = message.content
                
                if not content:
                    logger.warning(f"收到空消息: {source}")
                    return
                
                logger.info(f"处理消息: {source}: {content[:50]}...")
                
                # 获取显示名称
                display_name = AGENT_DISPLAY_NAMES.get(source, source)
                
                # 构造消息对象
                message_id = str(datetime.now().timestamp())
                timestamp = datetime.now().isoformat()
                
                sse_message = {
                    "id": message_id,
                    "sender": source,
                    "sender_display_name": display_name,
                    "content": content,
                    "timestamp": timestamp
                }
                
                # 添加到消息历史
                message_history.append(sse_message)
                
                # 发送到SSE事件队列
                await event_queue.put({
                    "event": "agent_message",
                    "data": sse_message
                })
                logger.info(f"消息已发送: {message_id}")
            except Exception as e:
                logger.error(f"处理消息时出错: {e}")
                # 尝试发送错误消息
                await send_agent_message("System", f"处理消息时出错: {str(e)}")
        
        try:
            # 创建智能体列表
            agents = [manager, senior_dev, junior_dev, designer]
            
            # 创建群聊 - 使用 AutoGen 0.4 API
            logger.info("创建群聊")
            group_chat = RoundRobinGroupChat(participants=agents, max_turns=20)
            
            # 创建取消令牌
            cancellation_token = CancellationToken()
            
            # 创建初始消息
            initial_message = TextMessage(content=scenario_text, source="System")
            
            # 处理初始消息
            await process_message(initial_message)
            
            # 启动群聊 - 使用 AutoGen 0.4 API 的流式接口
            logger.info("启动群聊")
            async for message in group_chat.run_stream(
                task=[initial_message],
                cancellation_token=cancellation_token
            ):
                # 处理每条消息
                await process_message(message)
                
            logger.info("群聊正常结束")
        except asyncio.CancelledError:
            logger.warning("群聊被取消")
            if 'cancellation_token' in locals():
                cancellation_token.cancel()
        except Exception as chat_error:
            logger.error(f"群聊出错: {chat_error}")
            # 发送错误消息
            await send_agent_message("System", f"群聊过程中出错: {str(chat_error)}")
            
            # 备用方案：如果AutoGen对话失败，手动发送一些消息
            logger.info("启动备用对话")
            await send_agent_message("Manager", "看起来我们的系统遇到了一些技术问题。")
            await send_agent_message("SeniorDev", "我们可以先讨论一下项目的基本需求。根据我的理解，我们需要开发一个多智能体交互系统。")
            await send_agent_message("JuniorDev", "我对这个项目很感兴趣，特别是前端的实时通信部分。")
            await send_agent_message("Designer", "我已经准备了一些UI设计草图，主要采用了简洁的界面风格。")
            await send_agent_message("Manager", "很好，我们可以先从基础功能开始，然后逐步添加更复杂的特性。")
            await send_agent_message("SeniorDev", "我建议我们使用React和FastAPI作为技术栈，这样可以快速开发出原型。")
            await send_agent_message("Designer", "我会准备更详细的设计稿，包括颜色方案和组件库。")
            await send_agent_message("JuniorDev", "我可以负责前端的基础组件开发，需要大约一周时间。")
            await send_agent_message("Manager", "好的，那我们下周再开会讨论进展。")
        
        # 保存对话结果
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"conversation_{timestamp}.json"
            
            # 确保目录存在
            os.makedirs("conversations_log", exist_ok=True)
            
            # 保存消息历史
            if message_history:
                save_conversation(message_history, filename)
                logger.info(f"对话已保存: {filename}")
            else:
                logger.warning("没有消息可保存")
        except Exception as save_error:
            logger.error(f"保存对话失败: {save_error}")
        
        # 发送结束消息
        await send_agent_message("System", "对话已结束，感谢所有参与者的贡献。")
        
        logger.info("模拟结束")
        
        # 发送模拟状态更新
        await event_queue.put({
            "event": "simulation_status",
            "data": {"is_running": False}
        })
    except asyncio.CancelledError:
        logger.info("模拟被取消")
        await send_agent_message("System", "模拟已被用户取消。")
    except Exception as e:
        logger.error(f"模拟出错: {e}")
        error_traceback = traceback.format_exc()
        logger.error(error_traceback)
        
        # 发送错误消息到前端
        await send_agent_message("System", f"模拟运行出错: {str(e)}\n请检查后端日志获取详细信息。")
    finally:
        active_simulation = None
        logger.info("模拟完全结束")

# 启动应用
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 