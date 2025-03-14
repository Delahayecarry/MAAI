# 多智能体交互系统

基于AutoGen 0.4框架的多智能体交互系统，用于模拟团队协作场景。系统支持多种预定义场景，实时显示智能体对话，并提供可视化功能。

## 技术栈

### 前端
- React 18
- TypeScript
- Zustand (状态管理)
- Vite (构建工具)
- Tailwind CSS (样式)
- Headless UI (UI组件)
- React-Window (虚拟列表)
- D3 (力导向图)
- Framer Motion (动画)
- SSE (Server-Sent Events，实时通信)

### 后端
- FastAPI
- AutoGen 0.4
- Python 3.10+

## 功能特点

- 多种预定义场景：支持团队会议、技术讨论、设计评审等多种场景
- 实时对话展示：通过SSE技术实时展示智能体之间的对话内容
- 历史记录查看：保存并查看历史对话记录
- 关系网络可视化：使用D3力导向图可视化智能体之间的关系网络
- 响应式设计：适配不同屏幕尺寸

## 系统架构

```
├── frontend/            # React前端
│   ├── src/
│   │   ├── components/  # UI组件
│   │   ├── pages/       # 页面组件
│   │   ├── store/       # Zustand状态管理
│   │   ├── hooks/       # 自定义Hooks
│   │   ├── api/         # API服务
│   │   └── utils/       # 工具函数
│   ├── public/          # 静态资源
│   └── ...              # 配置文件
├── backend/             # FastAPI后端
│   ├── main.py          # 主入口
│   └── requirements.txt # 依赖
├── agents/              # 智能体定义
│   ├── manager.py       # 经理智能体
│   ├── developer.py     # 开发者智能体
│   └── designer.py      # 设计师智能体
├── conversations/       # 对话场景定义
│   └── scenarios.py     # 预定义场景
├── utils/               # 工具函数
│   └── logging_utils.py # 日志工具
└── start.py             # 启动脚本
```

## 安装与运行

### 环境要求
- Python 3.10+
- Node.js 16+
- npm 8+

### 安装步骤

1. 克隆仓库
```bash
git clone https://github.com/yourusername/multi-agent-interaction.git
cd multi-agent-interaction
```

2. 安装后端依赖
```bash
pip install -r requirements.txt
```

3. 安装前端依赖
```bash
cd frontend
npm install
cd ..
```

4. 配置环境变量
复制`.env.example`为`.env`，并填写相应的API密钥：
```bash
cp .env.example .env
```

### 运行应用

使用启动脚本同时启动前端和后端：
```bash
python start.py
```

或者分别启动：

1. 启动后端
```bash
cd backend
uvicorn main:app --reload --port 8000
```

2. 启动前端
```bash
cd frontend
npm run dev
```

然后在浏览器中访问：http://localhost:3000

### 使用 Docker 部署

本项目支持使用 Docker 进行部署，提供了 Dockerfile 和 docker-compose.yml 文件。

#### 使用 Docker Compose 部署

1. 确保已安装 Docker 和 Docker Compose
2. 复制环境变量文件
```bash
cp .env.example .env
```
3. 编辑 `.env` 文件，填写必要的配置
4. 启动容器
```bash
docker-compose up -d
```
5. 访问应用：http://localhost:8000

#### 使用 Docker Hub 镜像

你也可以直接使用我们发布在 Docker Hub 上的镜像：

```bash
docker pull yourusername/maai:latest
docker run -d -p 8000:8000 -v $(pwd)/.env:/app/.env -v $(pwd)/conversations_log:/app/conversations_log --name maai-app yourusername/maai:latest
```

#### 构建自己的 Docker 镜像

如果你想构建自己的 Docker 镜像，可以使用以下命令：

```bash
docker build -t maai:latest .
docker run -d -p 8000:8000 -v $(pwd)/.env:/app/.env -v $(pwd)/conversations_log:/app/conversations_log --name maai-app maai:latest
```

## 使用方法

1. 在"实时对话"页面中选择一个场景
2. 点击"启动对话"按钮开始模拟
3. 观察智能体之间的交互过程
4. 可以随时停止对话
5. 在"历史记录"页面查看保存的对话

## 智能体介绍

- **经理**：团队领导，负责协调和决策
- **资深开发**：经验丰富的开发人员
- **初级开发**：新加入的开发人员
- **设计师**：负责用户界面和体验设计

## 技术实现

本项目使用了 AutoGen 0.4 API，主要特点包括：

- 使用 `AssistantAgent` 创建智能体
- 使用 `RoundRobinGroupChat` 进行轮流对话
- 使用 `TextMessage` 处理消息
- 使用 SSE (Server-Sent Events) 实现实时通信
- 使用 FastAPI 构建后端 API

## 持续集成/持续部署

本项目使用 GitHub Actions 进行 CI/CD，每次推送到主分支或创建标签时，会自动构建 Docker 镜像并推送到 DockerHub。

## 许可证

本项目采用 MIT 许可证 - 详情请参阅 [LICENSE](LICENSE) 文件 