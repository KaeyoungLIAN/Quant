import os
import datetime
import json
import logging
from pathlib import Path

# Load .env file
_env_path = Path(__file__).parent / '.env'
if _env_path.exists():
    for line in _env_path.read_text().splitlines():
        line = line.strip()
        if line and '=' in line and not line.startswith('#'):
            k, v = line.split('=', 1)
            os.environ[k] = v

import uvicorn
from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from passlib.hash import bcrypt as bcrypt_hasher
import bcrypt as _bcrypt
from jose import jwt, JWTError

from database import get_db, engine, Base
from models import User, ModuleTracker, LearningRecord, Lesson, ChatHistory
from schemas import (
    RegisterRequest, LoginRequest, TokenResponse, UserProfile,
    TeacherStatus, ModuleProgress, LessonResponse,
    CheckpointRequest, ChatRequest, ChatResponse, LearningRecordOut,
)
from llm import call_llm, build_lesson_prompt, build_chat_prompt

logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger(__name__)

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Quant Teacher", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Static Files (VitePress build output) ────────────────────────

_static_dir = Path(__file__).parent.parent / "docs" / ".vitepress" / "dist"
_static_dir_str = str(_static_dir)

# Mount static assets at /assets/ for performance (no html=True needed here)
assets_dir = _static_dir / "assets"
if assets_dir.exists():
    app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")

# ─── Auth Helpers ────────────────────────────────────────────────

SECRET_KEY = os.environ.get("TEACHER_SECRET_KEY", "quant-teacher-local-dev-key")
ALGORITHM = "HS256"


def create_token(user_id: int) -> str:
    return jwt.encode({"sub": str(user_id), "exp": datetime.datetime.utcnow() + datetime.timedelta(days=30)}, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(authorization: str | None = Header(None), db: Session = Depends(get_db)) -> User:
    if not authorization:
        raise HTTPException(401, "Missing token")
    try:
        token = authorization.replace("Bearer ", "")
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = int(payload["sub"])
    except (JWTError, ValueError, KeyError):
        raise HTTPException(401, "Invalid token")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(401, "User not found")
    return user


# ─── Auth Endpoints ──────────────────────────────────────────────


@app.post("/api/auth/register")
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == req.username).first():
        raise HTTPException(400, "Username already exists")
    user = User(
        username=req.username,
        password_hash=_bcrypt.hashpw(req.password.encode(), _bcrypt.gensalt()).decode(),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return TokenResponse(token=create_token(user.id), user_id=user.id, username=user.username)


@app.post("/api/auth/login")
def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == req.username).first()
    if not user or not _bcrypt.checkpw(req.password.encode(), user.password_hash.encode()):
        raise HTTPException(401, "Invalid credentials")
    return TokenResponse(token=create_token(user.id), user_id=user.id, username=user.username)


@app.get("/api/auth/me")
def get_me(user: User = Depends(get_current_user)):
    return {
        "user_id": user.id,
        "username": user.username,
        "mission": user.mission,
        "math_level": user.math_level,
        "python_level": user.python_level,
        "finance_level": user.finance_level,
    }


# ─── Teacher Endpoints ───────────────────────────────────────────

PHASES = {
    "one": {"name": "搭桥 — 数学 + 金融入门", "modules": [
        "01-calculus", "02-linear-algebra", "03-probability",
        "04-statistics", "finance-basics",
    ]},
    "two": {"name": "核心能力 — 策略与回测", "modules": [
        "05-stochastic-processes", "06-trend-following", "07-mean-reversion",
        "08-backtesting", "09-risk-metrics", "10-execution",
    ]},
    "three": {"name": "独立策略开发", "modules": [
        "11-paper-reproduction", "12-own-strategy", "13-live-trading",
    ]},
}

ALL_MODULES = {}
for p in PHASES.values():
    for m in p["modules"]:
        ALL_MODULES[m] = p["name"]


def get_module_name(key: str) -> str:
    names = {
        "01-calculus": "高等数学",
        "02-linear-algebra": "线性代数",
        "03-probability": "概率论",
        "04-statistics": "数理统计",
        "finance-basics": "金融入门",
        "05-stochastic-processes": "随机过程",
        "06-trend-following": "趋势跟踪策略",
        "07-mean-reversion": "均值回归策略",
        "08-backtesting": "回测框架",
        "09-risk-metrics": "风险指标",
        "10-execution": "执行算法",
        "11-paper-reproduction": "论文复现",
        "12-own-strategy": "自主策略开发",
        "13-live-trading": "实盘交易",
    }
    return names.get(key, key)


@app.get("/api/teacher/status")
def teacher_status(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    trackers = db.query(ModuleTracker).filter(ModuleTracker.user_id == user.id).all()
    tracker_map = {t.module_key: t for t in trackers}

    # Determine current phase
    current_phase = "one"
    phase_progress = {}
    for phase_key, phase_info in PHASES.items():
        completed = 0
        total = len(phase_info["modules"])
        for mk in phase_info["modules"]:
            t = tracker_map.get(mk)
            if t and t.status == "completed":
                completed += 1
        pct = (completed / total * 100) if total else 0
        phase_progress[phase_key] = pct
        if pct >= 100 and phase_key == "one":
            current_phase = "two"
        if pct >= 100 and phase_key == "two":
            current_phase = "three"

    # Build module list
    modules = []
    for mk in PHASES[current_phase]["modules"]:
        t = tracker_map.get(mk)
        modules.append(ModuleProgress(
            module_key=mk,
            status=t.status if t else "not_started",
            confidence=t.confidence if t else 1,
        ))

    # Find current module (first not completed)
    current_module = None
    for mk in PHASES[current_phase]["modules"]:
        t = tracker_map.get(mk)
        if not t or t.status != "completed":
            current_module = mk
            break

    # Overall progress
    total_modules = sum(len(p["modules"]) for p in PHASES.values())
    completed_modules = sum(1 for t in trackers if t.status == "completed")
    overall = (completed_modules / total_modules * 100) if total_modules else 0

    return TeacherStatus(
        phase=current_phase,
        phase_name=PHASES[current_phase]["name"],
        overall_progress=round(overall, 1),
        modules=modules,
        current_module=current_module,
        current_topic=get_module_name(current_module) if current_module else None,
        summary=f"已完成 {completed_modules}/{total_modules} 个模块，当前阶段：{PHASES[current_phase]['name']}",
    )


@app.get("/api/teacher/history")
def teacher_history(limit: int = 20, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    records = db.query(LearningRecord).filter(
        LearningRecord.user_id == user.id
    ).order_by(LearningRecord.session_date.desc()).limit(limit).all()
    return [LearningRecordOut(
        id=r.id, module_key=r.module_key, session_date=r.session_date,
        content=r.content, notes=r.notes, checkpoint_passed=r.checkpoint_passed,
    ) for r in records]


@app.post("/api/teacher/lesson")
def request_lesson(module_key: str | None = None, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Request a new lesson. If module_key is None, pick the current module automatically."""
    if not module_key:
        status = teacher_status(user, db)
        module_key = status.current_module
        if not module_key:
            raise HTTPException(400, "All modules completed! You're done with this phase.")

    # Build context for LLM
    trackers = db.query(ModuleTracker).filter(
        ModuleTracker.user_id == user.id
    ).all()
    trackers_context = "\n".join(
        f"- {get_module_name(t.module_key)}: {t.status} (confidence: {t.confidence}/5)"
        for t in trackers
    ) or "No progress yet."

    student_level = f"Math: {user.math_level}/5, Python: {user.python_level}/5, Finance: {user.finance_level}/5"

    prompt = build_lesson_prompt(
        module_key=get_module_name(module_key),
        mission=user.mission,
        trackers_context=trackers_context,
        student_level=student_level,
    )
    raw = call_llm(prompt, temperature=0.4, max_tokens=4000)
    if not raw:
        # Fallback lesson
        lesson = Lesson(
            user_id=user.id, module_key=module_key,
            title=f"学习 {get_module_name(module_key)}",
            html_content=f"<h2>{get_module_name(module_key)}</h2><p>AI 暂时不可用，请参考 Wiki 对应章节学习。</p>",
            checkpoint="请阅读 Wiki 后回答：这个模块的核心概念是什么？",
        )
    else:
        try:
            parsed = json.loads(raw)
            lesson = Lesson(
                user_id=user.id, module_key=module_key,
                title=parsed.get("title", get_module_name(module_key)),
                html_content=parsed.get("html_content", ""),
                checkpoint=parsed.get("checkpoint", ""),
            )
        except (json.JSONDecodeError, KeyError):
            lesson = Lesson(
                user_id=user.id, module_key=module_key,
                title=get_module_name(module_key),
                html_content=raw,
                checkpoint="完成学习后请确认掌握",
            )

    db.add(lesson)

    # Update or create tracker
    tracker = db.query(ModuleTracker).filter(
        ModuleTracker.user_id == user.id,
        ModuleTracker.module_key == module_key,
    ).first()
    if not tracker:
        tracker = ModuleTracker(
            user_id=user.id, module_key=module_key,
            status="in_progress", started_at=datetime.datetime.utcnow(),
        )
        db.add(tracker)
    else:
        tracker.status = "in_progress"

    db.commit()
    db.refresh(lesson)

    return LessonResponse(
        lesson_id=lesson.id,
        title=lesson.title,
        html_content=lesson.html_content,
        checkpoint=lesson.checkpoint,
    )


@app.post("/api/teacher/checkpoint")
def submit_checkpoint(req: CheckpointRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    lesson = db.query(Lesson).filter(Lesson.id == req.lesson_id, Lesson.user_id == user.id).first()
    if not lesson:
        raise HTTPException(404, "Lesson not found")

    # Save learning record
    record = LearningRecord(
        user_id=user.id,
        module_key=lesson.module_key,
        content=f"Lesson: {lesson.title}",
        notes=req.notes,
        checkpoint_passed=req.passed,
    )
    db.add(record)

    # Update tracker confidence
    tracker = db.query(ModuleTracker).filter(
        ModuleTracker.user_id == user.id,
        ModuleTracker.module_key == lesson.module_key,
    ).first()
    if tracker:
        if req.passed:
            tracker.confidence = min(tracker.confidence + 1, 5)
        else:
            tracker.confidence = max(tracker.confidence - 1, 1)

    db.commit()
    return {"ok": True, "message": "记录已保存"}


@app.post("/api/teacher/chat")
def chat(req: ChatRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Build context
    trackers = db.query(ModuleTracker).filter(
        ModuleTracker.user_id == user.id
    ).all()
    context_parts = [f"Mission: {user.mission or 'Learn quant'}"]
    context_parts.append(f"Levels - Math: {user.math_level}/5, Python: {user.python_level}/5, Finance: {user.finance_level}/5")
    completed = [get_module_name(t.module_key) for t in trackers if t.status == "completed"]
    if completed:
        context_parts.append(f"Completed: {', '.join(completed)}")
    in_progress = [get_module_name(t.module_key) for t in trackers if t.status == "in_progress"]
    if in_progress:
        context_parts.append(f"In progress: {', '.join(in_progress)}")
    context = "\n".join(context_parts)

    # Get recent chat history
    recent_chats = db.query(ChatHistory).filter(
        ChatHistory.user_id == user.id
    ).order_by(ChatHistory.created_at.desc()).limit(10).all()
    history_lines = []
    for c in reversed(recent_chats):
        prefix = "Student" if c.role == "user" else "Teacher"
        history_lines.append(f"{prefix}: {c.message[:200]}")
    history = "\n".join(history_lines)

    prompt = build_chat_prompt(req.message, context, history)
    raw = call_llm(prompt, temperature=0.6, max_tokens=1500)
    reply = raw or "抱歉，AI 暂时不可用，请稍后再试。"

    # Save to history
    db.add(ChatHistory(user_id=user.id, role="user", message=req.message))
    db.add(ChatHistory(user_id=user.id, role="assistant", message=reply))
    db.commit()

    return ChatResponse(reply=reply)


# ─── Catch-all: serve VitePress SPA ──────────────────────────────

from fastapi.responses import FileResponse
from fastapi import Request

_static_dir = Path(__file__).parent.parent / "docs" / ".vitepress" / "dist"


@app.api_route("/{path:path}", methods=["GET"])
async def serve_spa(request: Request, path: str):
    """Serve static files for non-API paths. SPA fallback to index.html."""
    if path.startswith("api/"):
        return JSONResponse({"detail": "Not Found"}, status_code=404)
    file_path = _static_dir / path
    if file_path.exists() and file_path.is_file():
        return FileResponse(str(file_path))
    index_path = _static_dir / "index.html"
    if index_path.exists():
        return FileResponse(str(index_path))
    return JSONResponse({"detail": "Not Found"}, status_code=404)


if __name__ == "__main__":
    port = int(os.environ.get("TEACHER_PORT", "8000"))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)
