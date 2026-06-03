from apscheduler.schedulers.background import BackgroundScheduler
from telegram_client.sync_wrapper import send_message_sync
from database.db import Session
from database.models import Student, PendingMessage, DeliveryHistory
from ai.engine import generate_exercises
from services.message_formatter import format_message
from services.streak_service import update_streak
from services.logger import logger
from datetime import datetime


scheduler = BackgroundScheduler()

def send_scheduled_exercises():
    now = datetime.now()

    today = now.date()

    logger.info(
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
                logger.warning(f"Skipping {student.full_name}: {exercise['message']}")
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

            logger.info(f"Pending review created for {student.full_name}")


        except Exception:
            logger.exception(
                f"Failed creating pending exercise "
                f"for {student.full_name}"
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

            try:
                pending.sent = True

                history = DeliveryHistory(
                    student_id=pending.student_id,
                    student_name=pending.student_name,
                    student_username=pending.student_username,
                    message_type=pending.message_type,
                    content=final_message,
                    streak=streak_info["streak"],
                    milestone=streak_info["milestone"],
                    success=True
                )

                session.add(history)

                session.commit()
            
            except Exception:

                session.rollback()

                logger.exception(f"Database update failed while saving delivery history")

                continue

            logger.info(
                f"Message auto-sent to "
                f"{pending.student_name}"
            )
        
        except Exception:
            
            try:

                history = DeliveryHistory(
                    student_id=pending.student_id,
                    student_name=pending.student_name,
                    student_username=pending.student_username,
                    message_type=pending.message_type,
                    content=pending.message,
                    streak=0,
                    milestone=None,
                    success=False
                )

                session.add(history)

                session.commit()
            
            except Exception as db_error:
                session.rollback()
                logger.exception(f"Failed to save failed-delivery history")

            logger.exception(
                f"Auto-send failed for "
                f"{pending.student_name}"
            )

    session.close()

def start_scheduler():

    if scheduler.running:

        logger.warning("Scheduler already running")

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

    logger.info("Scheduler started")



