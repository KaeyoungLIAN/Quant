from database import engine, Base
from models import User, ModuleTracker, LearningRecord, Lesson, ChatHistory

Base.metadata.create_all(bind=engine)
print("Tables created.")
