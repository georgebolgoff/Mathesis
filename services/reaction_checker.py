from database.db import Session
from database.models import ExerciseAttempt, StreakApproval, Student
from  datetime import datetime


from telegram_client.client import client
from services.logger import logger 

import asyncio

async def check_reactions():

    session = Session()

    try:

        attempts = (
            session.query(ExerciseAttempt)
            .filter_by(streak_awarded=False)
            .all()
        )

        logger.info(
            f"Checking {len(attempts)} exercise attempts"
        )

        for attempt in attempts:

            try:

                student = session.get(
                    Student,
                    attempt.student_id
                )

                if not student:
                    continue

                entity = await client.get_entity(
                    student.telegram_username
                )

                message = await client.get_messages(
                    entity,
                    ids=attempt.telegram_message_id
                )

                if not message:
                    continue

                if not message.reactions:
                    continue

                approved = False

                for reaction in message.reactions.results:

                    emoji = (
                        reaction.reaction.emoticon
                    )

                    if emoji == "💯":

                        approved = True
                        break
                
                if not approved:
                    continue

                existing = (
                    session.query(StreakApproval)
                    .filter_by(
                        telegram_message_id=
                        attempt.telegram_message_id
                    )
                    .first()
                )

                if existing:
                    continue

                approval = StreakApproval(
                    student_id=attempt.student_id,
                    telegram_message_id=
                    attempt.telegram_message_id
                )

                session.add(approval)

                attempt.streak_awarded = True

                student.streak += 1

                student.last_approved_exercise_at = datetime.utcnow()

                session.commit()

                logger.info(
                    f"STREAK APPROVED "
                    f"student={student.full_name} "
                    f"streak={student.streak}"
                )
            
            except Exception:

                logger.exception(
                    f"Failed attempt "
                    f"{attempt.id}"
                )
    
    finally:

        session.close()