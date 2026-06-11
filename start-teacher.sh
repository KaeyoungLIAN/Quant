#!/bin/bash
# Quant Learning 启动脚本
# 用法: ./start-teacher.sh          # 前台运行
#        ./start-teacher.sh bg      # 后台运行

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# 读取 LLM API Key（从 health-dashboard/.env）
DOTENV="$HOME/SelfProjects/health-dashboard/.env"
if [ -f "$DOTENV" ]; then
    export LLM_API_KEY=$(grep '^LLM_API_KEY' "$DOTENV" | head -1 | cut -d= -f2-)
else
    echo "⚠️  未找到 $DOTENV，LLM_API_KEY 未设置"
fi

# 默认端口
PORT=${TEACHER_PORT:-8000}

# 检查 venv
cd "$SCRIPT_DIR/teacher"
if [ ! -d "venv" ]; then
    echo "❌ venv 不存在，请先运行: cd teacher && python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi
source venv/bin/activate

# 先 build 前端
echo "🔨 构建前端..."
cd "$SCRIPT_DIR"
npx vitepress build docs > /dev/null 2>&1 || { echo "❌ 前端构建失败"; exit 1; }
echo "✅ 前端构建完成"

# 检查端口
if lsof -i :$PORT >/dev/null 2>&1; then
    echo "⚠️  端口 $PORT 已被占用，尝试杀掉旧进程..."
    lsof -ti :$PORT | xargs kill -9 2>/dev/null
    sleep 1
fi

if [ "$1" = "bg" ]; then
    nohup python teacher/main.py > "$SCRIPT_DIR/server.log" 2>&1 &
    echo "✅ Quant Learning 后端已启动 (PID $!, 端口 $PORT)"
    echo "📄 日志: $SCRIPT_DIR/server.log"
    echo "🌐 本地访问: http://localhost:$PORT"
    echo "🌐 隧道: cloudflared tunnel --url http://localhost:$PORT"
else
    echo "🚀 启动 Quant Learning 后端 (端口 $PORT)..."
    echo "🌐 访问: http://localhost:$PORT"
    python teacher/main.py
fi
