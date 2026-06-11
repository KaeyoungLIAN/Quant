#!/bin/bash
# Quant Learning 一键部署脚本
# 用法: ./deploy.sh [--skip-build] [--restart-only]

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PORT=${TEACHER_PORT:-8000}

echo "🔨 Quant Learning 部署开始..."

# 1. Git 拉取最新代码
cd "$SCRIPT_DIR"
if [ -d ".git" ]; then
    echo "📥 拉取最新代码..."
    git pull
fi

# 2. 安装前端依赖（如需）
if [ ! -d "node_modules" ]; then
    echo "📦 安装前端依赖..."
    npm install
fi

# 3. 构建前端
if [ "$1" != "--skip-build" ]; then
    echo "🔨 构建前端..."
    npx vitepress build docs
    echo "✅ 前端构建完成"
fi

# 4. 停止旧进程
if lsof -i :$PORT >/dev/null 2>&1; then
    echo "⏹️  停止旧进程 (端口 $PORT)..."
    lsof -ti :$PORT | xargs kill -9 2>/dev/null
    sleep 1
fi

# 5. 启动后端
echo "🚀 启动后端..."
cd "$SCRIPT_DIR"
source teacher/venv/bin/activate 2>/dev/null || true
nohup python teacher/main.py > "$SCRIPT_DIR/server.log" 2>&1 &
echo "✅ 部署完成 (PID $!, 端口 $PORT)"

# 6. 健康检查
sleep 2
if curl -s -o /dev/null -w "%{http_code}" http://localhost:$PORT/learn/ | grep -q 200; then
    echo "✅ 健康检查通过"
else
    echo "⚠️  健康检查未通过，查看 server.log 排查"
fi
