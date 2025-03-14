# 更新日志

## v1.0.2 (2023-03-16)

### 改进
- 优化 Docker 构建过程，跳过 TypeScript 类型检查以提高构建速度
- 添加 .env 文件配置，支持条件编译

### 修复
- 修复 Docker 构建过程中的 TypeScript 错误

## v1.0.1 (2023-03-15)

### 改进
- 将 Python 版本要求从 3.9+ 升级到 3.10+，以支持 AutoGen 0.4.0
- 更新 Dockerfile 使用 Python 3.10 镜像

## v1.0.0 (2023-03-14)

### 新特性
- 初始版本发布
- 多智能体交互系统基础功能
- 实时对话展示
- 关系网络可视化
- 历史记录查看

### 改进
- 从 Streamlit 迁移到 React 技术栈
- 使用 FastAPI 构建后端 API
- 使用 SSE 实现实时通信
- 使用 D3.js 实现关系网络可视化
- 使用 Zustand 进行状态管理

### 修复
- 修复关系网络可视化中的文本显示问题
- 修复 SSE 连接断开后的重连问题
- 修复消息排序问题

## 未来计划
- 添加用户认证系统
- 实现更多的可视化图表
- 添加智能体配置界面
- 优化移动端体验
- 添加更多的场景模板
- 实现对话导出功能
- 支持自定义智能体属性和关系
- 添加对话分析功能 