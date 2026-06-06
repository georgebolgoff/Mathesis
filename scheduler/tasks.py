from apscheduler.schedulers.background import BackgroundScheduler

from telegram_client.sync_wrapper import send_message_sync
from database.db import Session
from database.models import Student, PendingMessage, DeliveryHistory
from ai.engine import generate_exercises
from services.message_formatter import format_message
from services.streak_service import update_streak
from services.logger import logger, log_event
from datetime import datetime, timedelta


scheduler = BackgroundScheduler()

def send_scheduled_exercises():

    try:

        now = datetime.now()
        today = now.date()

        log_event(
            "info",
            "scheduler_tick_started",
            time=now.strftime("%H:%M"),
            date=str(today)
        )

        session = Session()

        try:

            students = session.query(Student).all()

            logger.info(
                f"Scheduler found {len(students)} students"
            )

            for student in students:

                try:

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

                    logger.info(
                        f"Generating exercise for "
                        f"{student.full_name}"
                    )

                    exercise = generate_exercises(
                        subject=student.subject,
                        level=student.level,
                        student_id=student.id
                    )

                    if not exercise["ok"]:

                        logger.warning(
                            f"Skipping {student.full_name}: "
                            f"{exercise['message']}"
                        )

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

                    try:

                        notification_message = (
                            "⚠️ Mathesis Review Needed\n\n"
                            f"Student: {student.full_name}\n"
                            f"Username: {student.telegram_username}\n"
                            f"Type: exercise\n\n"
                            "This message will be auto-sent "
                            "in approximately 10 minutes."
                        )

                        send_message_sync(
                            "@explins",
                            notification_message
                        )

                        log_event(
                            "info",
                            "pending_notification_sent",
                            student=student.full_name
                        )

                    except Exception as e:

                        log_event(
                            "error",
                            "pending_notification_failed",
                            student=student.full_name,
                            error=str(e)
                        )


                    logger.info(
                        f"Pending review created for "
                        f"{student.full_name}"
                    )

                except Exception:

                    session.rollback()

                    logger.exception(
                        f"Failed processing student "
                        f"{student.full_name}"
                    )

        finally:
            session.close()

    except Exception:

        logger.exception(
            "Scheduler tick crashed"
        )

def auto_send_scheduled_exercises():

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

            log_event("info", "auto_message_sent", student_id=pending.student_id, username=pending.student_username, message_type=pending.message_type)

            try:
                pending.sent = True

                student = session.get(
                    Student,
                    pending.student_id
                )

                if student:
                    student.last_generated_date = datetime.now().date()

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

                log_event("error", "auto_send_failed", student_id=pending.student_id, student=pending.student_name)

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

    with open("SCHEDULER_START.txt", "a") as f:
        f.write("ENTERED\n")

    if scheduler.running:

        with open("SCHEDULER_START.txt", "a") as f:
            f.write("ALREADY_RUNNING\n")

        return

    scheduler.add_job(
        send_scheduled_exercises,
        "interval",
        minutes=1
    )

    with open("SCHEDULER_START.txt", "a") as f:
        f.write("JOB1_ADDED\n")

    scheduler.add_job(
        auto_send_scheduled_exercises,
        "interval",
        minutes=1
    )



    with open("SCHEDULER_START.txt", "a") as f:
        f.write("JOB2_ADDED\n")

    scheduler.start()

    with open("JOBS_DEBUG.txt", "w") as f:
        for job in scheduler.get_jobs():
            f.write(f"{job.id} | {job.next_run_time}\n")

    with open("SCHEDULER_START.txt", "a") as f:
        f.write("STARTED\n")


