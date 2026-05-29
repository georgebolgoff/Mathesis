from apscheduler.schedulers.background import BackgroundScheduler
from telegram_client.sync_wrapper import send_message_sync
from database.db import Session
from database.models import Student, PendingMessage
from ai.engine import generate_exercises
from services.message_formatter import format_message
from services.streak_service import update_streak
from datetime import datetime
import random
import time


scheduler = BackgroundScheduler()

def send_scheduled_exercises():
    current_time = datetime.now().strftime(
        "%H:%M"
    )

    print(
        f"Checking schedules at {current_time}"
    )

    session = Session()
    students = session.query(Student).all()

    for student in students:
        
        if not student.active:
            continue

        if student.daily_send_time != current_time:
            continue

        try:
            exercise = generate_exercises(
                    subject=student.subject,
                    level=student.level,
                    student_id=student.id
                )

            if not exercise["ok"]:
                print(f"Skipping {student.full_name}: {exercise['message']}")
                continue

            pending = PendingMessage(
                student_id=student.id,
                student_username=student.telegram_username,
                student_name=student.full_name,
                message=exercise["content"],
                message_type="exercise"
            )

            session.add(pending)
            session.commit()

            print(f"Pending review created for {student.full_name}")


        except Exception as e:
            print(
                f"Failed sending to "
                f"{student.full_name}: {e}"
            )

            session.rollback()
    
    session.close()

def auto_send_scheduled_exercises():

    from datetime import datetime, timedelta

    session = Session()

    cutoff = (
        datetime.utcnow() - timedelta(minutes=10)
    )

    pending_messages = (
        session.query(PendingMessage)
        .filter(
            PendingMessage.sent == False,
            PendingMessage.created_at <= cutoff
        )
        .all()
    )

    for pending in pending_messages:

        try:

            streak = update_streak(pending.student_id)

            final_message = format_message(
                student_id=pending.student_id,
                content=pending.message,
                template_type=pending.message_type
            )
            
            send_message_sync(
                pending.student_username,
                final_message

            )

            pending.sent = True

            session.commit()

            print(
                f"AUTO-SENT: "
                f"{pending.student_name}"
            )
        
        except Exception as e:
            print(
                f"AUTO-SEND FAILED: {e}"
            )

            session.rollback()
    session.close()

def start_scheduler():
    scheduler.add_job(
        send_scheduled_exercises,
        "interval",
        minutes=1
    )

    scheduler.add_job(
        auto_send_scheduled_exercises,
        "interval",
        minutes=1
    )

    scheduler.start()

    print("Scheduler started")



