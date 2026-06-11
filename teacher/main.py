import os
import json
import logging
from pathlib import Path

ROOT = Path(__file__).parent.parent  # Quant project root

# Load .env file
_env_path = ROOT / "teacher" / '.env'
if _env_path.exists():
    for line in _env_path.read_text().splitlines():
        line = line.strip()
        if line and '=' in line and not line.startswith('#'):
            k, v = line.split('=', 1)
            os.environ[k] = v

import uvicorn
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import func

from database import get_db, engine, Base
from models import Progress
from schemas import (
    ChapterProgress, ProgressResponse,
    AdvanceRequest, JudgeRequest, JudgeResponse,
    ChatRequest, ChatResponse,
)
from llm import call_llm

logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger(__name__)

# ─── DB Init ────────────────────────────────────────────────────

Base.metadata.create_all(bind=engine)

# ─── Chapter Registry ───────────────────────────────────────────
# All chapters in order. This is the source of truth for the learning path.

CHAPTERS = [
    "1.1", "1.2", "1.3", "1.4",
    "2.1", "2.2", "2.3", "2.4",
    "3.1", "3.2", "3.3", "3.4", "3.5", "3.6", "3.7", "3.8", "3.9", "3.10",
    "4.1", "4.2", "4.3", "4.4",
    "5.1", "5.2", "5.3", "5.4",
    "6.1", "6.2", "6.3", "6.4",
    "7.1", "7.2", "7.3",
]

# ─── App ────────────────────────────────────────────────────────

app = FastAPI(title="Quant Learning API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Static Files ───────────────────────────────────────────────

_static_dir = ROOT / "docs" / ".vitepress" / "dist"
_assets_dir = _static_dir / "assets"
if _assets_dir.exists():
    app.mount("/assets", StaticFiles(directory=str(_assets_dir)), name="assets")

# ─── Helpers ────────────────────────────────────────────────────

def init_progress(db: Session):
    """Ensure all chapters exist in DB with correct unlock chain."""
    existing = {r.chapter_key for r in db.query(Progress).all()}
    for i, key in enumerate(CHAPTERS):
        if key not in existing:
            status = "in_progress" if i == 0 else "locked"
            p = Progress(
                chapter_key=key,
                status=status,
                sub_items_done="[]",
                updated_at=func.now(),
            )
            db.add(p)
    db.commit()


def compute_progress(db: Session) -> ProgressResponse:
    """Build full progress state. Lock/unlock is computed, not stored."""
    rows = db.query(Progress).order_by(Progress.chapter_key).all()
    row_map = {r.chapter_key: r for r in rows}

    # Determine the first incompleted chapter
    first_incomplete_idx = None
    for i, key in enumerate(CHAPTERS):
        r = row_map.get(key)
        if not r or r.status != "completed":
            first_incomplete_idx = i
            break

    chapters = []
    last_visited = None
    for i, key in enumerate(CHAPTERS):
        r = row_map.get(key)
        sub_items = json.loads(r.sub_items_done) if r and r.sub_items_done else []
        status = r.status if r else "locked"

        # Lock/unlock logic: only the first incomplete chapter is "in_progress"
        if first_incomplete_idx is not None:
            if i < first_incomplete_idx:
                status = "completed"
            elif i == first_incomplete_idx:
                status = "in_progress"
            else:
                status = "locked"

        chapters.append(ChapterProgress(
            chapter_key=key,
            status=status,
            sub_items_done=sub_items,
        ))

        if status == "in_progress":
            last_visited = key

    # If all completed, the last chapter stays completed
    if first_incomplete_idx is None:
        for c in chapters:
            c.status = "completed"

    return ProgressResponse(chapters=chapters, last_visited=last_visited)


# ─── Ensure DB initialized on first request ─────────────────────

@app.on_event("startup")
def startup():
    db = next(get_db())
    try:
        init_progress(db)
    finally:
        db.close()


# ─── API: Progress ──────────────────────────────────────────────

@app.get("/api/v1/progress", response_model=ProgressResponse)
def get_progress(db: Session = Depends(get_db)):
    return compute_progress(db)


@app.post("/api/v1/progress/advance")
def advance_progress(req: AdvanceRequest, db: Session = Depends(get_db)):
    p = db.query(Progress).filter(Progress.chapter_key == req.chapter_key).first()
    if not p:
        raise HTTPException(404, "Chapter not found")

    sub_items = json.loads(p.sub_items_done)
    if req.sub_item not in sub_items:
        sub_items.append(req.sub_item)
        p.sub_items_done = json.dumps(sub_items)
        p.updated_at = func.now()

    # Mark chapter completed on any advance
    p.status = "completed"
    db.commit()

    return {"ok": True, "chapter_key": req.chapter_key, "sub_items_done": sub_items}


# ─── API: AI Judge ──────────────────────────────────────────────

SYSTEM_JUDGE_PROMPT = """你是一位严格的量化金融导师。用户回答了一道论述题，你需要：

1. 判断答案是否正确/完整（passed: true/false）
2. 给出详细的文字反馈（feedback）
3. 给出改进建议列表（suggestions）

评分标准：
- passed = true：答案核心正确，逻辑清晰，涵盖了关键点
- passed = false：答案有明显错误、遗漏关键点、逻辑混乱

用中文输出严格的 JSON 格式，不要包含 markdown 代码块标记：
{"passed": true/false, "feedback": "...", "suggestions": ["...", "..."]}"""


@app.post("/api/v1/progress/judge", response_model=JudgeResponse)
def judge_answer(req: JudgeRequest):
    prompt = f"""{SYSTEM_JUDGE_PROMPT}

## 章节
{req.chapter_key}

## 题目
{req.question}

## 用户的回答
{req.answer}

请判断并输出 JSON。"""
    raw = call_llm(prompt, temperature=0.3, max_tokens=1000)
    if not raw:
        return JudgeResponse(passed=True, feedback="AI 暂时不可用，答案已记录。", suggestions=[])

    try:
        parsed = json.loads(raw)
        return JudgeResponse(
            passed=parsed.get("passed", True),
            feedback=parsed.get("feedback", ""),
            suggestions=parsed.get("suggestions", []),
        )
    except (json.JSONDecodeError, KeyError):
        return JudgeResponse(passed=True, feedback=raw, suggestions=[])


# ─── API: Chat ──────────────────────────────────────────────────

SYSTEM_CHAT_PROMPT = """你是 Quant Learning 的 AI 助教。用户在学量化交易课程，回答他的问题。

规则：
1. 用中文回答
2. 如果需要公式，用 LaTeX 格式（$...$）
3. 如果需要代码，用 Python 代码块
4. 如果用户问的概念还没学到，提醒他前置知识
5. 尽量简短直接"""  # noqa: E501


@app.post("/api/v1/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    context_str = ""
    if req.context:
        context_str = f"\n用户当前学习进度：第 {req.context.get('chapter_key', '?')} 章\n"

    prompt = f"""{SYSTEM_CHAT_PROMPT}{context_str}

用户的问题：
{req.message}"""
    raw = call_llm(prompt, temperature=0.6, max_tokens=1500)
    reply = raw or "抱歉，AI 暂时不可用，请稍后再试。"
    return ChatResponse(reply=reply)


# ─── Catch-all: serve VitePress SPA ─────────────────────────────

@app.api_route("/{path:path}", methods=["GET"])
async def serve_spa(request: Request, path: str):
    if path.startswith("api/"):
        return JSONResponse({"detail": "Not Found"}, status_code=404)
    file_path = _static_dir / path
    # Try with .html suffix (for cleanUrls builds)
    if not (file_path.exists() and file_path.is_file()):
        file_path = _static_dir / f"{path}.html"
    if file_path.exists() and file_path.is_file():
        return FileResponse(str(file_path))
    index_path = _static_dir / "index.html"
    if index_path.exists():
        return FileResponse(str(index_path))
    return JSONResponse({"detail": "Not Found"}, status_code=404)


# ─── Entry ──────────────────────────────────────────────────────

if __name__ == "__main__":
    port = int(os.environ.get("TEACHER_PORT", "8000"))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)
