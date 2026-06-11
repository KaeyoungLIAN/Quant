from pydantic import BaseModel
from typing import Optional


class ChapterProgress(BaseModel):
    chapter_key: str
    status: str                     # locked | in_progress | completed
    sub_items_done: list[str]       # ["mcq_1", "mcq_3", "essay_1"]


class ProgressResponse(BaseModel):
    chapters: list[ChapterProgress]
    last_visited: Optional[str] = None


class AdvanceRequest(BaseModel):
    chapter_key: str
    sub_item: str                   # "mcq_1" | "essay_1"


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
