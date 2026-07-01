from datetime import datetime, timedelta, date, time

from telethon.tl.types import ReactionEmoji

from database.db import Session
from database.models import Student, StreakApproval, ExerciseAttempt
from telegram_client.client import client
from services.logger import logger


def has_hundred_reaction(message):
    if not message.reactions:
        return False

    for reaction in message.reactions.results:
        if (
            isinstance(reaction.reaction, ReactionEmoji)
            and reaction.reaction.emoticon == "💯"
        ):
            return True

    return False


def _exercises_per_day(student: Student) -> int:
    return getattr(student, "exercises_per_day", 1) or 1


def _day_bounds(day: date):
    start = datetime.combine(day, time.min)
    end = start + timedelta(days=1)
    return start, end


def _attempts_sent_on_day(session, student_id: int, day: date):
    start, end = _day_bounds(day)
    return (
        session.query(ExerciseAttempt)
        .filter(
            ExerciseAttempt.student_id == student_id,
            ExerciseAttempt.sent_at >= start,
            ExerciseAttempt.sent_at < end,
        )
        .all()
    )


def _all_sent_exercises_approved(session, student_id: int, day: date) -> bool:
    attempts = _attempts_sent_on_day(session, student_id, day)
    if not attempts:
        return False
    return all(attempt.streak_awarded for attempt in attempts)


def _credit_streak_if_due(session, student: Student, day: date) -> bool:
    if student.last_streak_credit_date == day:
        return False

    exercises_per_day = _exercises_per_day(student)

    if exercises_per_day <= 1:
        if not _all_sent_exercises_approved(session, student.id, day):
            return False
    else:
        if not _all_sent_exercises_approved(session, student.id, day):
            return False
    

    student.streak += 1
    student.last_streak_credit_date = day
    student.last_approved_exercise_at = datetime.utcnow()
    return True


async def check_reaction_approvals():
    session = Session()

    try:
        students = session.query(Student).all()

        for student in students:
            try:
                entity = await client.get_entity(student.telegram_username)
                messages = await client.get_messages(entity, limit=50)

                for message in messages:
                    if not has_hundred_reaction(message):
                        continue

                    existing_approval = (
                        session.query(StreakApproval)
                        .filter_by(telegram_message_id=message.id)
                        .first()
                    )
                    if existing_approval:
                        continue

                    attempt = (
                        session.query(ExerciseAttempt)
                        .filter_by(telegram_message_id=message.id)
                        .first()
                    )
                    if not attempt:
                        continue

                    student_obj = session.get(Student, attempt.student_id)
                    if not student_obj:
                        continue

                    approval = StreakApproval(
                        student_id=attempt.student_id,
                        telegram_message_id=message.id,
                    )
                    session.add(approval)

                    attempt.streak_awarded = True

                    exercise_day = attempt.sent_at.date()
                    credited = _credit_streak_if_due(
                        session,
                        student_obj,
                        exercise_day,
                    )

                    session.commit()

                    if credited:
                        logger.info(
                            f"STREAK APPROVED | "
                            f"{student_obj.full_name} "
                            f"-> {student_obj.streak}"
                        )
                    else:
                        todays_attempts = _attempts_sent_on_day(
                            session,
                            student_obj.id,
                            exercise_day,
                        )
                        approved = sum(
                            1 for a in todays_attempts if a.streak_awarded
                        )
                        total = len(todays_attempts)

                        logger.info(
                            f"EXERCISE APPROVED | "
                            f"{student_obj.full_name} "
                            f"{approved}/{total} for {exercise_day} "
                            f"(streak unchanged: {student_obj.streak})"
                        )

            except Exception:
                logger.exception(
                    f"Failed checking {student.full_name}"
                )

    finally:
        session.close()


async def check_streak_resets():
    session = Session()

    try:
        cutoff = datetime.utcnow() - timedelta(hours=48)

        expired_attempts = (
            session.query(ExerciseAttempt)
            .filter(
                ExerciseAttempt.sent_at <= cutoff,
                ExerciseAttempt.streak_awarded == False,
                ExerciseAttempt.reset_processed == False,
            )
            .all()
        )

        logger.info(
            f"Found {len(expired_attempts)} expired attempts"
        )

        for attempt in expired_attempts:
            try:
                student = session.get(Student, attempt.student_id)
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
                    f"Failed resetting streak for student_id {attempt.student_id}"
                )

    finally:
        session.close()