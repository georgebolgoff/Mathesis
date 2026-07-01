from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Date
from datetime import datetime

class Base(DeclarativeBase):
    pass

class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True)
    full_name = Column(String)
    telegram_username = Column(String, nullable=False, unique=True)
    level = Column(String, nullable=False)
    subject = Column(String)
    daily_send_time = Column(String, default="09:00")
    daily_send_times = Column(String, default="09:00")
    active = Column(Boolean, default=True)
    streak = Column(Integer, default=0)
    last_sent_date = Column(Date, nullable=True)
    last_generated_date = Column(Date)
    last_approved_exercise_at = Column(DateTime, nullable=True)
    last_streak_credit_date = Column(Date, nullable=True)
    exercises_per_day = Column(Integer, default=1, nullable=False)

class Exercise(Base):
    __tablename__ = "exercises"

    id = Column(Integer, primary_key=True)
    subject = Column(String)
    level = Column(String)
    content = Column(String)

class ExerciseAttempt(Base):

    __tablename__ = "exercise_attempts"

    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    exercise_id = Column(Integer, ForeignKey("exercises.id"), nullable=False)
    telegram_message_id = Column(Integer, nullable=True)
    sent_at = Column(DateTime, default=datetime.utcnow)
    streak_awarded = Column(Boolean, default=False)
    reset_processed = Column(Boolean, default=False)


class StreakApproval(Base):

    __tablename__ = "streak_approvals"

    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    telegram_message_id = Column(Integer, unique=True)
    approved_at = Column(DateTime, default=datetime.utcnow)



class Idiom(Base):
    __tablename__ = "idioms"

    id = Column(Integer, primary_key=True)
    level = Column(String)
    content = Column(Text)

class PendingMessage(Base):
    __tablename__ = "pending_messages"

    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, nullable=False)
    student_username = Column(String, nullable=False)
    student_name = Column(String, nullable=False)
    message = Column(String, nullable=False)
    message_type = Column(String, default="exercise") # exercise | idiom | manual
    sent = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    exercise_id = Column(Integer, nullable=True)


class DeliveryHistory(Base):

    __tablename__ = "delivery_history"

    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, nullable=False)
    student_name = Column(String, nullable=False)
    student_username = Column(String, nullable=False)
    message_type = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    sent_at = Column(DateTime, default=datetime.utcnow)
    streak = Column(Integer, default=0)
    milestone = Column(Integer, nullable=True)
    success = Column(Boolean, default=True)


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

    
        