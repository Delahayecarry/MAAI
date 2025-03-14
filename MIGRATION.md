# Streamlit到React技术栈迁移文档

本文档记录了将多智能体交互系统从Streamlit迁移到React技术栈的过程和主要变更。

## 迁移概述

我们将原有的基于Streamlit的前端界面迁移到了现代化的React技术栈，同时将后端从直接Python脚本执行改为FastAPI服务。这次迁移带来了更好的用户体验、更强的可扩展性和更高的性能。

## 技术栈变更

### 前端
- **原技术栈**：Streamlit
- **新技术栈**：
  - React 18
  - TypeScript
  - Zustand (状态管理)
  - Vite (构建工具)
  - Tailwind CSS (样式)
  - Headless UI (UI组件)
  - React-Window (虚拟列表)
  - D3 (力导向图)
  - Framer Motion (动画)

### 后端
- **原技术栈**：Python脚本直接执行
- **新技术栈**：FastAPI

### 通信方式
- **原通信方式**：无实时通信，需要刷新页面
- **新通信方式**：SSE (Server-Sent Events) 实现实时双向通信

## 主要改进

1. **实时通信**：使用SSE技术实现了实时消息推送，无需刷新页面即可看到智能体对话更新
2. **响应式设计**：使用Tailwind CSS实现了响应式布局，适配不同屏幕尺寸
3. **性能优化**：
   - 使用React-Window实现虚拟列表，提高长对话的渲染性能
   - 使用Zustand进行状态管理，减少不必要的重渲染
4. **更好的可视化**：
   - 使用D3实现了智能体关系网络的力导向图可视化
   - 使用Framer Motion添加了平滑的动画效果
5. **更好的用户体验**：
   - 使用Headless UI组件提供了更现代的UI交互
   - 添加了更多视觉反馈和状态指示

## 文件结构变更

### 前端结构
```
frontend/
├── src/
│   ├── components/  # UI组件
│   ├── pages/       # 页面组件
│   ├── store/       # Zustand状态管理
│   ├── hooks/       # 自定义Hooks
│   ├── api/         # API服务
│   └── utils/       # 工具函数
├── public/          # 静态资源
└── ...              # 配置文件
```

### 后端结构
```
backend/
├── main.py          # FastAPI主入口
└── requirements.txt # 依赖
```

## 功能对应关系

| Streamlit功能 | React实现 |
|--------------|----------|
| 主页 | HomePage组件 |
| 实时对话 | LiveChatPage组件 + SSE |
| 历史记录 | HistoryPage组件 |
| 智能体卡片 | AgentCard组件 |
| 对话视图 | MessageList + MessageItem组件 |
| 场景选择器 | ScenarioSelector组件 |
| 关系网络 | RelationshipGraph组件 (D3) |

## 状态管理

使用Zustand替代了Streamlit的会话状态管理：

- **agentStore**: 管理智能体信息和选择状态
- **chatStore**: 管理对话消息、场景和模拟状态

## API通信

使用Axios进行HTTP请求，主要API端点：

- `/api/scenarios`: 获取场景列表
- `/api/simulation/start`: 启动模拟
- `/api/simulation/stop`: 停止模拟
- `/api/history`: 获取历史对话列表
- `/api/history/{id}`: 获取特定历史对话
- `/events`: SSE事件流

## 部署变更

原来的部署方式是直接运行Python脚本，现在需要：

1. 安装Node.js和npm
2. 安装前端依赖
3. 安装后端依赖
4. 使用start.py脚本同时启动前端和后端

## AutoGen 0.4 API 迁移

本项目还完成了从旧版 AutoGen 到 AutoGen 0.4 API 的迁移，主要变更包括：

1. **包依赖变更**：
   - 从单一的 `autogen` 包迁移到 `autogen-agentchat`、`autogen-core` 和 `autogen-ext` 三个包
   - 更新了相关的导入语句

2. **智能体创建变更**：
   - 使用 `AssistantAgent` 替代 `ConversableAgent`
   - 使用 `OpenAIChatCompletionClient` 作为模型客户端

3. **群聊管理变更**：
   - 使用 `RoundRobinGroupChat` 替代 `GroupChat`
   - 使用 `members` 参数替代 `agents` 参数
   - 使用 `max_turns` 参数替代 `max_round` 参数

4. **消息处理变更**：
   - 使用 `TextMessage` 类型处理消息
   - 使用 `run_stream` 方法进行流式对话处理
   - 使用 `CancellationToken` 管理对话取消

5. **错误处理改进**：
   - 添加了更完善的错误处理机制
   - 使用 `try-except` 块捕获并处理各种异常
   - 添加了备用对话方案，确保即使 AutoGen 对话失败也能向前端发送消息

6. **消息历史管理**：
   - 添加了消息历史记录功能，便于保存完整对话
   - 改进了消息保存逻辑，确保对话记录完整性

## 未来改进方向

1. 添加用户认证系统
2. 实现更多的可视化图表
3. 添加智能体配置界面
4. 优化移动端体验
5. 添加更多的场景模板
6. 实现对话导出功能
7. 支持自定义智能体属性和关系
8. 添加对话分析功能 