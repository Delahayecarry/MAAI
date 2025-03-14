"""
预定义的对话场景
"""

# 场景字典
SCENARIOS = {
    "team_meeting": """
    团队今天召开项目启动会议，讨论一个新的移动应用开发项目。
    
    项目背景：
    - 这是一款面向健身爱好者的应用
    - 需要在3个月内完成开发
    - 竞争对手已经有类似产品
    
    请讨论项目规划、分工和可能遇到的挑战。每个人都应该根据自己的角色和经验发表意见。
    """,
    
    "technical_discussion": """
    团队需要决定新项目的技术栈。目前有两个选择：
    1. React Native + Firebase
    2. Flutter + AWS
    
    请根据团队经验、项目需求和时间限制讨论最佳选择。考虑性能、开发速度和维护难度等因素。
    """,
    
    "design_review": """
    设计师刚刚完成了应用的初步UI设计，需要团队审核并提供反馈。
    
    设计亮点：
    - 极简风格界面
    - 深色模式支持
    - 创新的健身追踪数据可视化
    
    开发团队需要评估实现难度，经理需要考虑是否符合项目方向，所有人都应该考虑用户体验。
    """,
    
    "conflict_resolution": """
    项目进度落后于计划，团队成员之间出现了一些分歧。
    
    问题点：
    - 初级开发认为任务分配不公平
    - 设计师认为开发团队频繁要求修改设计
    - 资深开发觉得质量正在被时间压力牺牲
    
    经理需要调和这些冲突，找到解决方案让项目回到正轨。
    """,
    
    "casual_chat": """
    团队在周五下午的休闲时间聚在一起，讨论各自的周末计划、兴趣爱好和近期看过的电影或书籍。
    
    这是一个轻松的对话，大家可以分享个人生活，增进彼此了解。
    """
}

def get_scenario(scenario_name):
    """
    获取预定义场景的提示文本
    
    参数:
        scenario_name (str): 场景名称
    
    返回:
        str: 场景提示文本
    """
    if scenario_name in SCENARIOS:
        return SCENARIOS[scenario_name]
    else:
        raise ValueError(f"未找到场景: {scenario_name}. 可用场景: {list(SCENARIOS.keys())}")
        
def list_scenarios():
    """
    列出所有可用场景
    
    返回:
        list: 场景名称列表
    """
    return list(SCENARIOS.keys()) 