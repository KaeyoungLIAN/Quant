from sqlalchemy import Column, Integer, String, Text, DateTime, func
from database import Base


class Progress(Base):
    __tablename__ = "progress"

    id = Column(Integer, primary_key=True, index=True)
    chapter_key = Column(String(20), unique=True, index=True, nullable=False)  # e.g. "3.5"
    status = Column(String(20), default="locked")  # locked | in_progress | completed
    sub_items_done = Column(Text, default="[]")  # JSON array of passed items
    updated_at = Column(DateTime, default=func.now())
