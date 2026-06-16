from apscheduler.schedulers.background import BackgroundScheduler

from telegram_client.sync_wrapper import send_message_sync
from telegram_client.reaction_sync_wrapper import check_reactions_sync
from telegram_client.streak_reset_wrapper import check_streak_resets_sync
from database.db import Session
from database.models import Student, PendingMessage, DeliveryHistory, ExerciseAttempt
from ai.engine import generate_exercises
from services.message_formatter import format_message
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

                    unfinished_attempt = (
                        session.query(ExerciseAttempt)
                        .filter_by(
                            student_id=student.id,
                            streak_awarded=False,
                            reset_processed=False
                        )
                    )

                    if unfinished_attempt:

                        logger.inof(
                            f"Skipping {student.full_name}: unfinished exercise exists"
                        )

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
                        message_type="exercise",
                        exercise_id=exercise["id"]
                    )

                    session.add(pending)
                    session.commit()

                    logger.info(
                        f"PENDING_CREATED_FOR_{student.full_name}"
                    )

                    try:

                        logger.info(
                            "ABOUT_TO_SEND_TELEGRAM_NOTIFICATION"
                        )

                        send_message_sync(
                            "Mathesis Notifications",
                            (
                                "⚠️ Mathesis Auto-Send Queue\n\n"
                                f"Student: {student.full_name}\n"
                                f"Username: {student.telegram_username}\n"
                                f"Type: exercise\n"
                                f"Scheduled: {student.daily_send_time}\n\n"
                                "Message added to Pending Messages.\n"
                                "Auto-send will occur in ~10 minutes."
                            )
                        )

                        logger.info(
                            "TELEGRAM_NOTIFICATION_SENT"
                        )

                    except Exception as e:

                        logger.exception(
                            f"Notification failed: {e}"
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

            final_message = format_message(
                student_id=pending.student_id,
                content=pending.message,
                template_type=pending.message_type
            )
            
            message = send_message_sync(
                pending.student_username,
                final_message

            )

            attempt = ExerciseAttempt(
                student_id=pending.student_id,
                exercise_id=pending.exercise_id,
                telegram_message_id=message.id
            )

            session.add(attempt)

            log_event("info", "auto_message_sent", student_id=pending.student_id, username=pending.student_username, message_type=pending.message_type)

            try:
                pending.sent = True

                student = session.get(
                    Student,
                    pending.student_id
                )

                if student:
                    student.last_generated_date = datetime.now().date()

                student = session.get(
                    Student,
                    pending.student_id
                )

                history = DeliveryHistory(
                    student_id=pending.student_id,
                    student_name=pending.student_name,
                    student_username=pending.student_username,
                    message_type=pending.message_type,
                    content=final_message,
                    streak=student.streak if student else 0,
                    milestone=None,
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

    scheduler.add_job(
        check_reactions_sync,
        "interval",
        minutes=5
    )

    scheduler.add_job(
        check_streak_resets_sync,
        "interval",
        minutes=5
    )



    scheduler.start()

