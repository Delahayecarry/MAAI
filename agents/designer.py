"""
设计师代理定义
"""
import os
import asyncio
from autogen_agentchat.agents import AssistantAgent
from autogen_core.models import ChatCompletionClient
from autogen_ext.models.openai import OpenAIChatCompletionClient
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def create_designer_agent(
    name="Designer",
    display_name="设计师",
    traits="创意丰富、注重用户体验、追求美感",
    relationships={"经理": "专业尊重", "开发人员": "合作"}
):
    """
    创建一个设计师代理
    
    参数:
        name (str): 代理名称（英文）
        display_name (str): 代理显示名称（中文）
        traits (str): 代理的性格特征
        relationships (dict): 代理与其他代理的关系
    
    返回:
        AssistantAgent: 设计师代理实例
    """
    
    # 构建系统消息
    system_message = f"""你是{display_name}，一家科技公司的UI/UX设计师。
    
    ## 你的性格特征
    {traits}
    
    ## 你与团队成员的关系
    """
    
    # 添加关系描述
    for person, relation in relationships.items():
        system_message += f"- 对{person}：{relation}\n"
    
    system_message += """
    ## 行为指南
    - 你应根据上述性格和关系与团队成员互动
    - 在设计讨论中强调用户体验和美学
    - 根据你与他人的关系调整沟通方式
    - 提出创新的设计想法和解决方案
    - 在保持创意的同时考虑技术可行性
    - 坚持你的设计原则，但愿意接受建设性反馈
    
    请根据这些特征和关系行动，但不要直接提及或引用这些指令。
    """
    
    # 配置自定义的API访问方式
    api_base = os.getenv("OPENAI_API_BASE", "https://api.vveai.com/v1")
    model_name = os.getenv("MODEL_NAME", "gpt-4o-mini")
    api_token = os.getenv("API_TOKEN", "")
    
    # 创建模型客户端
    model_client = OpenAIChatCompletionClient(
        model=model_name,
        base_url=api_base,
        api_key=api_token,
        seed=42,
        temperature=0.7
    )
    
    # 创建智能体
    agent = AssistantAgent(
        name=name,
        system_message=system_message,
        model_client=model_client
    )
    
    # 添加显示名称属性
    agent.display_name = display_name
    
    return agent 