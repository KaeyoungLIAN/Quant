from pydantic import BaseModel
from typing import Optional


class ChapterProgress(BaseModel):
    chapter_key: str
    status: str                     # locked | in_progress | completed


class ProgressResponse(BaseModel):
    chapters: list[ChapterProgress]
    last_visited: Optional[str] = None


class AdvanceRequest(BaseModel):
    chapter_key: str


class JudgeRequest(BaseModel):
    chapter_key: str
    question: str
    answer: str


class JudgeResponse(BaseModel):
    passed: bool
    feedback: str
    suggestions: list[str] = []


class ChatRequest(BaseModel):
    message: str
    context: Optional[dict] = None   # {chapter_key, progress}


class ChatResponse(BaseModel):
    reply: str
