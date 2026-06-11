from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# ─── Auth ────────────────────────────────────────────────────────

class RegisterRequest(BaseModel):
    username: str = Field(min_length=2, max_length=50)
    password: str = Field(min_length=4, max_length=128)

class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    token: str
    user_id: int
    username: str

class UserProfile(BaseModel):
    mission: str = ""
    math_level: int = Field(default=1, ge=1, le=5)
    python_level: int = Field(default=3, ge=1, le=5)
    finance_level: int = Field(default=1, ge=1, le=5)


# ─── Teacher ─────────────────────────────────────────────────────

class ModuleProgress(BaseModel):
    module_key: str
    status: str
    confidence: int

class TeacherStatus(BaseModel):
    phase: str                              # "one" | "two" | "three"
    phase_name: str
    overall_progress: float                 # 0-100
    modules: List[ModuleProgress]
    current_module: Optional[str] = None    # 推荐下一步
    current_topic: Optional[str] = None
    summary: str                            # 一句话总结

class LessonResponse(BaseModel):
    lesson_id: int
    title: str
    html_content: str
    checkpoint: str

class CheckpointRequest(BaseModel):
    lesson_id: int
    passed: bool
    notes: str = ""

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    reply: str

class LearningRecordOut(BaseModel):
    id: int
    module_key: str
    session_date: datetime
    content: str
    notes: str
    checkpoint_passed: bool
