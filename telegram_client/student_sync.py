from telegram_client.client import client 
from database.db import Session
from database.models import Student
from services.logger import logger, log_event


PREFIX = "📚"



async def sync_students_from_telegram():

    session = Session()

    try:

        logger.info("Starting Telegram student sync")
        log_event("info", "telegram_student_sync_started")

        existing_usernames = {
            student.telegram_username
            for student in session.query(Student).all()
        }

        added_count = 0

        async for dialog in client.iter_dialogs():

            name = dialog.name

            if not name.startswith(PREFIX):
                continue

            entity = dialog.entity

            username = getattr(
                entity,
                "username",
                None
            )

            if not username:
                continue
            username = f"@{username}"

            if username in existing_usernames:
                continue

            clean_name = (
                name.replace(PREFIX, "").strip()
            )

            new_student = Student(
                full_name=clean_name,
                telegram_username=username,
                level="easy",
                subject="english",
                daily_send_time="09:00",
                active=True
            )

            session.add(new_student)

            existing_usernames.add(username)

            added_count += 1

            
            log_event("info", "telegram_student_added", name=clean_name, username=username)

        session.commit()
        log_event("info", "telegram_student_sync_completed", added=added_count)
        logger.info(f"Telegram student sync complete. "
                    f"Added {added_count} new students")
    
    except Exception:

        logger.exception("Telegram student sync failed")
        raise

    finally:

        session.close()