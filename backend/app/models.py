from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Index, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from app.enums import TaskStatus, TaskPriority


# Импортируем Base из database.py (если он там создается)
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    login = Column(String(50), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True)
    name = Column(String(100))
    groupName = Column(String(100))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    subjects = relationship("Subject", back_populates="user", cascade="all, delete")
    tasks = relationship("Task", back_populates="user", cascade="all, delete")

class Subject(Base):
    __tablename__ = "subjects"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="subjects")
    tasks = relationship("Task", back_populates="subject", cascade="all, delete")

    # Уникальное сочетание пользователь + название предмета
    __table_args__ = (
        Index('ix_subject_user_name', 'user_id', 'name', unique=True),
    )

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    subject_id = Column(Integer, ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    deadline = Column(DateTime, index=True)  # ← ИНДЕКС УЖЕ ЗДЕСЬ!

    status = Column(SQLEnum(TaskStatus), default="assigned", index=True)
    priority = Column(SQLEnum(TaskPriority), default="medium", index=True)

    user = relationship("User", back_populates="tasks")
    subject = relationship("Subject", back_populates="tasks")

    __table_args__ = (
        Index('ix_tasks_user_status', 'user_id', 'status'),
        Index('ix_tasks_user_subject', 'user_id', 'subject_id'),
        # УБРАЛИ: Index('ix_tasks_deadline', 'deadline'),  # ← ДУБЛИКАТ!
    )
