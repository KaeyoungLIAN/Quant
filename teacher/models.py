from sqlalchemy import Column, Integer, String, DateTime, func
from database import Base


class Progress(Base):
    __tablename__ = "progress"

    id = Column(Integer, primary_key=True, index=True)
    chapter_key = Column(String(20), unique=True, index=True, nullable=False)  # e.g. "3.5"
    status = Column(String(20), default="locked")  # locked | in_progress | completed
    updated_at = Column(DateTime, default=func.now())
