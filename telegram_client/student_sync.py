from telegram_client.client import client 
from database.db import Session
from database.models import Student

import asyncio

PREFIX = "📚"



async def sync_students_from_telegram():

    session = Session()

    existing_usernames = {
        student.telegram_username
        for student in session.query(Student).all()
    }

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

        print(
            f"Added new student: {clean_name}"
        )

    session.commit()

    session.close()