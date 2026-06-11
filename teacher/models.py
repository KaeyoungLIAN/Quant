import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Float, ForeignKey, create_engine
from sqlalchemy.orm import relationship
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # 学习档案
    mission = Column(Text, default="")          # 为什么学量化
    math_level = Column(Integer, default=1)     # 1-5
    python_level = Column(Integer, default=3)   # 计算机硕士
    finance_level = Column(Integer, default=1)  # 零基础

    trackers = relationship("ModuleTracker", back_populates="user", cascade="all, delete-orphan")
    records = relationship("LearningRecord", back_populates="user", cascade="all, delete-orphan")
    lessons = relationship("Lesson", back_populates="user", cascade="all, delete-orphan")
    chats = relationship("ChatHistory", back_populates="user", cascade="all, delete-orphan")


class ModuleTracker(Base):
    """学习进度跟踪——对应 teach 的 trackers/"""
    __tablename__ = "module_trackers"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    module_key = Column(String(50), nullable=False)      # '01-calculus', '02-linear-algebra'...
    status = Column(String(20), default="not_started")   # not_started | in_progress | completed
    confidence = Column(Integer, default=1)               # 1-5 掌握度
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="trackers")


class LearningRecord(Base):
    """每次学习记录——对应 teach 的 learning-records/"""
    __tablename__ = "learning_records"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    module_key = Column(String(50), nullable=False)
    session_date = Column(DateTime, default=datetime.datetime.utcnow)
    content = Column(Text, default="")          # 学了什么
    notes = Column(Text, default="")            # 你的笔记
    checkpoint_passed = Column(Boolean, default=False)

    user = relationship("User", back_populates="records")


class Lesson(Base):
    """AI 生成的一节课"""
    __tablename__ = "lessons"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    module_key = Column(String(50), nullable=False)
    title = Column(String(200), default="")
    html_content = Column(Text, default="")     # 交互式 HTML
    checkpoint = Column(Text, default="")       # 掌握检查题
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="lessons")


class ChatHistory(Base):
    """对话上下文"""
    __tablename__ = "chat_histories"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role = Column(String(10), nullable=False)   # 'user' | 'assistant'
    message = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="chats")
