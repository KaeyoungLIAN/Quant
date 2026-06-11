#!/bin/bash
# Quant Learning 启动脚本
# 用法: ./start.sh [bg]

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PORT=${TEACHER_PORT:-8000}
DOTENV="$SCRIPT_DIR/teacher/.env"
VENV="$SCRIPT_DIR/teacher/venv"

# 读取 API Key
if [ -f "$DOTENV" ]; then
    # Read LLM_API_KEY from env file
    LLM_KEY=$(grep '^LLM_API_KEY' "$DOTENV" | head -1 | cut -d= -f2-)
    if [ -n "$LLM_KEY" ]; then
        export LLM_API_KEY="$LLM_KEY"
    fi
fi

# 构建前端
echo "🔨 构建前端..."
cd "$SCRIPT_DIR"
if ! npx vitepress build docs; then
    echo "❌ 前端构建失败"
    exit 1
fi
echo "✅ 前端构建完成"

# 检查 venv
if [ ! -d "$VENV" ]; then
    echo "❌ 请先创建 venv: cd teacher && python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# 启动后端
cd "$SCRIPT_DIR"

if [ "$1" = "bg" ]; then
    nohup "$VENV/bin/python" teacher/main.py > "$SCRIPT_DIR/server.log" 2>&1 &
    PID=$!
    sleep 2
    if curl -s -o /dev/null -w "%{http_code}" http://localhost:$PORT/ | grep -q 200; then
        echo "✅ Quant Learning 启动成功 (PID $PID, 端口 $PORT)"
        echo "📍 http://localhost:$PORT"
        echo "🌐 隧道: cloudflared tunnel --url http://localhost:$PORT"
    else
        echo "⚠️  启动可能失败，查看 server.log"
    fi
else
    echo "🚀 Quant Learning (端口 $PORT)"
    echo "📍 http://localhost:$PORT"
    "$VENV/bin/python" teacher/main.py
fi
