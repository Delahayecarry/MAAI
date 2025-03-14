# 多阶段构建
# 阶段1: 构建前端
FROM node:18-alpine AS frontend-builder
WORKDIR /app/frontend

# 复制前端依赖文件
COPY frontend/package*.json ./
RUN npm install

# 复制前端源代码
COPY frontend/ ./

# 构建前端 (跳过类型检查)
RUN echo "VITE_SKIP_TS_CHECK=true" > .env
RUN npm run build

# 阶段2: 构建后端
FROM python:3.10-slim AS backend-builder
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 复制后端依赖文件
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 阶段3: 最终镜像
FROM python:3.10-slim
WORKDIR /app

# 复制后端依赖
COPY --from=backend-builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=backend-builder /usr/local/bin /usr/local/bin

# 复制前端构建产物
COPY --from=frontend-builder /app/frontend/dist /app/frontend/dist

# 复制应用代码
COPY backend/ /app/backend/
COPY agents/ /app/agents/
COPY conversations/ /app/conversations/
COPY utils/ /app/utils/
COPY start.py /app/

# 创建日志目录
RUN mkdir -p /app/conversations_log

# 设置环境变量
ENV PYTHONPATH=/app
ENV FRONTEND_DIST_PATH=/app/frontend/dist

# 暴露端口
EXPOSE 8000

# 创建启动脚本
RUN echo '#!/bin/bash\n\
if [ ! -f /app/.env ]; then\n\
  echo "警告: 未找到 .env 文件，使用默认配置"\n\
  touch /app/.env\n\
fi\n\
cd /app\n\
python backend/main.py\n\
' > /app/docker-entrypoint.sh && chmod +x /app/docker-entrypoint.sh

# 设置启动命令
ENTRYPOINT ["/app/docker-entrypoint.sh"] 