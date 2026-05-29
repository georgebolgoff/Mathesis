from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from datetime import datetime

class Base(DeclarativeBase):
    pass

class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True)
    full_name = Column(String)
    telegram_username = Column(String, nullable=False, unique=True)
    level = Column(String, default="A1")
    subject = Column(String)
    daily_send_time = Column(String, default="09:00")
    active = Column(Boolean, default=True)

class Exercise(Base):
    __tablename__ = "exercises"

    id = Column(Integer, primary_key=True)
    subject = Column(String)
    level = Column(String)
    content = Column(String, unique=True)

class Idiom(Base):
    __tablename__ = "idioms"

    id = Column(Integer, primary_key=True)
    level = Column(String)
    content = Column(Text)

class PendingMessage(Base):
    __tablename__ = "pending_messages"

    id = Column(Integer, primary_key=True)
    student_username = Column(String)
    student_name = Column(String)
    message = Column(String)
    approved = Column(Boolean, default=False)
    sent = Column(Boolean, default=False)
    exercise_id = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class ExerciseHistory(Base):

    __tablename__ = "exercise_history"

    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    exercise_id = Column(Integer, ForeignKey("exercises.id"))
    sent_at = Column(DateTime, default=datetime.utcnow)

class IdiomHistory(Base):

    __tablename__ = "idiom_history"

    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    idiom_id = Column(Integer, ForeignKey("idioms.id"))


class MessageTemplate(Base):

    __tablename__ = "message_templates"

    id = Column(
        Integer,
        primary_key=True
    )

    template_type = Column(
        String,
        unique=True,
        nullable=False
    )

    template_text = Column(
        Text,
        nullable=False
    )

    
        