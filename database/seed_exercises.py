from database.db import Session
from database.models import Exercise
from services.logger import logger
from ai.exercise_bank import EXERCISES

def seed_exercises():
    
    session = Session()
    existing = session.query(Exercise).count()

    if existing > 0:

        logger.info("Exercise database already seeded")

        session.close()

        return

    for subject, levels in EXERCISES.items():

        for level, exercises in levels.items():

            for content in exercises:

                exercise = Exercise(
                    subject=subject,
                    level=level,
                    content=content,
                )
                
                session.add(exercise)
    
    session.commit()
    session.close()
    logger.info("Initial exercises database seeded")
