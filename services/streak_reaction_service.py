from telethon.tl.types import ReactionEmoji

from database.db import Session
from database.models import Student, StreakApproval, ExerciseAttempt

from telegram_client.client import client 

from services.logger import logger 

from datetime import datetime, timedelta



def has_hundred_reaction(message):

    if not message.reactions:
        return False
    
    for reaction in message.reactions.results:

        if (
            isinstance(
                reaction.reaction,
                ReactionEmoji
            )
        and
        reaction.reaction.emoticon == "💯"
        ): 
            return True
        
    return False


async def check_reaction_approvals():

    session = Session()


    try: 

        students = session.query(Student).all()

        for student in students:

            try:

                entity = await client.get_entity(
                    student.telegram_username
                )

                messages = await client.get_messages(
                    entity,
                    limit=50
                )

                for message in messages:

                    if not message.reactions:
                        continue

                    has_approval = False

                    for reaction in message.reactions.results:

                        if (
                            hasattr(
                                reaction.reaction,
                                "emoticon"
                            )
                            and
                            reaction.reaction.emoticon == "💯"
                        ):
                            has_approval = True
                            break
                    
                    if not has_approval:
                        continue

                    exisiting_approval = (
                        session.query(StreakApproval)
                        .filter_by(
                            telegram_message_id=message.id
                        )
                        .first()
                    )

                    if exisiting_approval:
                        continue

                    attempt = (
                        session.query(
                            ExerciseAttempt
                        )
                        .filter_by(
                            telegram_message_id=message.id
                        )
                        .first()
                    )

                    if not attempt:
                        continue


                    student_obj = session.get(
                        Student,
                        attempt.student_id
                    )

                    if not student_obj:
                        continue

                    student_obj.streak += 1

                    student_obj.last_approved_exercise_at = (
                        datetime.utcnow()
                    )

                    logger.info(
                        f"SETTING APPROVAL TIME FOR "
                        f"{student_obj.full_name}: "
                        f"{student_obj.last_approved_exercise_at}"
                    )

                    approval = StreakApproval(
                        student_id=attempt.student_id,
                        telegram_message_id=message.id
                    )

                    attempt.streak_awarded = True
                    attempt.reset_processed = True

                    session.add(approval)

                    session.commit()

                    logger.info(
                        f"AFTER COMMIT: "
                        f"{student_obj.last_approved_exercise_at}"
                    )

                    logger.info(
                        f"STREAK APPROVED | "
                        f"{student_obj.full_name} "
                        f" -> {student_obj.streak}"
                    )
            
            except Exception as e:

                logger.exception(
                    f"Failed checking {student.full_name}"
                )
    
    finally:

        session.close()


async def check_streak_resets():

    session = Session()

    try:

        cutoff = (
            datetime.utcnow()
            - timedelta(hours=48)
        )

        expired_attempts = (

            session.query(
                ExerciseAttempt
            )

            .filter(
                ExerciseAttempt.sent_at <= cutoff,
                ExerciseAttempt.streak_awarded == False,
                ExerciseAttempt.reset_processed == False
            )

            .all()
        )

        logger.info(
            f"Found {len(expired_attempts)} "
            f"expired attempts"
        )

        for attempt in expired_attempts:

            try:

                student = session.get(
                    Student,
                    attempt.student_id
                )

                if not student:
                    continue

                old_streak = student.streak

                student.streak = 0

                attempt.reset_processed = True

                session.commit()

                logger.info(
                    f"STREAK RESET | {student.full_name} {old_streak} -> 0"
                )
            
            except Exception:

                session.rollback()

                logger.exception(
                    f"Failed resetting streak "
                    f"for student_id"
                    f"{attempt.student_id}"
                )
    
    finally:

        session.close()

# async def scan_streak_reactions():
#     pass