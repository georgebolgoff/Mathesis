from telegram_client.client import send_message
from ai.engine import generate_exercises


async def send_ai_exercise(student, level="A2", topic="grammar"):
    exercise = generate_exercises(
        subject=topic,
        level=level,
        student_id=student.id
    )

    await send_message(
        student.telegram_username,
        exercise
    )