from apscheduler.schedulers.background import BackgroundScheduler
from telegram_client.sync_wrapper import send_message_sync
from database.db import Session
from database.models import Student, PendingMessage
from ai.engine import generate_exercises
from services.message_formatter import format_message
from services.streak_service import update_streak
from datetime import datetime, date
import random
import time


scheduler = BackgroundScheduler()

def send_scheduled_exercises():
    now = datetime.now()

    today = now.date()

    print(
        f"Checking schedules at {now.strftime('%H:%M')}"
    )

    session = Session()
    students = session.query(Student).all()

    for student in students:
        
        if not student.active:
            continue

        if student.last_generated_date == today:
            continue
            
        student_hour, student_minute = map(
            int,
            student.daily_send_time.split(":")
        )

        scheduled_minutes = (
            student_hour * 60
            + student_minute
        )

        current_minutes = (
            now.hour * 60
            + now.minute
        )

        if current_minutes < scheduled_minutes:
            continue

        existing_pending = (
            session.query(PendingMessage)
            .filter_by(
                student_id=student.id,
                sent=False
            )
            .first()
        )

        if existing_pending:
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

            student.last_generated_date = today

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

            streak_info = update_streak(pending.student_id)

            milestone_message = ""

            if streak_info["milestone"]:

                milestone_message = (
                    f"\n\n🔥 Amazing! "
                    f"You reached a "
                    f"{streak_info['milestone']}-day streak"
                )

            final_message = format_message(
                student_id=pending.student_id,
                content=pending.message,
                template_type=pending.message_type
            )

            final_message += milestone_message
            
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

    if scheduler.running:
        return
    
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



