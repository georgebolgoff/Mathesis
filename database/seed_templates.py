from database.db import Session

from database.models import (
    MessageTemplate
)

from services.logger import logger


def seed_message_templates():

    session = Session()

    existing_exercise = (
        session.query(MessageTemplate)
        .filter_by(
            template_type="exercise"
        )
        .first()
    )

    if not existing_exercise:

        exercise_template = MessageTemplate(
            template_type="exercise",
            template_text=(
                "📖✨✨One sentence per day🧏 #{streak}\n\n"
                "{content}"
            )
        )

        session.add(exercise_template)

        logger.info(
            "Exercise template seeded"
        )

    existing_idiom = (
        session.query(MessageTemplate)
        .filter_by(
            template_type="idiom"
        )
        .first()
    )

    if not existing_idiom:

        idiom_template = MessageTemplate(
            template_type="idiom",
            template_text=(
                "🎗🎗One idiom per day "
                "(just for fun) 🔍🔍 #{streak}\n\n"
                "{content}"
            )
        )

        session.add(idiom_template)

        logger.info(
            "Idiom template seeded"
        )

    session.commit()

    logger.info("Message template initialization completed")

    session.close()