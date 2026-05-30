from database.db import Session
from database.models import Exercise, MessageTemplate
from ai.exercise_bank import EXERCISES

def seed_exercises():
    
    session = Session()
    existing = session.query(Exercise).count()

    if existing > 0:

        print("Database already seeded")

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
    print("Initial exercises seeded")
