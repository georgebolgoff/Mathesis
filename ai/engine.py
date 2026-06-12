import random 
import os
from services.logger import logger

from database.db import Session
from database.models import Exercise, ExerciseHistory, Student
from config.models import EXERCISE_MODEL

from ai.topic_prompt_builder import build_topic_prompt

from openai import OpenAI
from dotenv import load_dotenv


def generate_exercises(subject, level, student_id):

    subject = subject.lower().strip()
    level = level.lower().strip()

    session = Session()

    used_exercise_ids = {
        row.exercise_id

        for row in (
            session.query(ExerciseHistory)
            .filter_by(student_id=student_id)
            .all()
        )
    }

    available_exercises = (

        session.query(Exercise)
        .filter_by(
            subject=subject,
            level=level
        )
        .all()
    )

    logger.info(
            f"Searching exercises: "
            f"subject={subject}, "
            f"level={level}"
        )

    logger.info(
        f"Available exercises found: "
        f"{len(available_exercises)}"
    )

    logger.info(
        f"Used exercises found: "
        f"{len(used_exercise_ids)}"
    )

    filtered = [
        ex

        for ex in available_exercises

        if ex.id not in used_exercise_ids
    ]



    remaining = len(filtered)

    logger.info(
            f"Remaining exercises after filtering: "
            f"{remaining}"
        )

    if remaining <= 5:
        logger.warning(
            f"Only {remaining} exercises remaining "
            f"for student {student_id}"
        )


    if remaining == 0:

        session.close()

        return {
            "ok": False,
            "id": None,
            "content": None,
            "message": "Student completed all exercises"
        }

    exercise = random.choice(filtered)

    session.close()

    return {
        "ok": True,
        "id": exercise.id,
        "content": exercise.content,
        "message": None
    }


def generate_controlled_exercise(
        selected_data
):
    
    load_dotenv()

    client = OpenAI(
        api_key=os.getenv(
            "OPENROUTER_API_KEY"
        ),
        base_url=(
            "https://openrouter.ai/api/v1"
        )
    )

    prompt = build_topic_prompt(
        selected_data
    )

    logger.info(
        f"CONTROLLED PROMPT:\n{prompt}"
    )

    try:

        response = (
            client.chat.completions.create(
                model=EXERCISE_MODEL,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
        )

        content = (
            response
            .choices[0]
            .message
            .content
            .strip()
        )

        return {
            "ok": True,
            "content": content
        }
    
    except Exception as e:

        return {
            "ok": False,
            "message": str(e)
        }
    
    
    # from services.exercise_refill_service import request_ai_refill

    # request_ai_refill(subject, level)

    #  #1. check subject
    # if subject not in EXERCISES:
    #     print(f"Unknown subject: {subject}")
    #     return ("No exercises available for this subject")
    
    # #2. check level safely
    # if level not in EXERCISES[subject]:
    #     print(f"INVALID LEVEL: {repr(level)} → defaulting to easy ")
    #     level = "easy"
    
    # return random.choice(EXERCISES[subject][level])












# import os
# from dotenv import load_dotenv
# from openai import OpenAI
# from ai.prompts import build_coding_prompt, build_english_prompt, build_math_prompt, build_vocabulary_prompt
# import random


# load_dotenv()

# client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# def generate_exercise(subject, level):

#     subject = subject.lower()

#     if subject == "math":
#         prompt = build_math_prompt(level)
    
#     elif subject == "english":
#         prompt = build_english_prompt(level)

#     elif subject == "vocabulary":
#         prompt = build_vocabulary_prompt(level)
    
#     elif subject == "coding":
#         prompt = build_coding_prompt(level)

#     else:
#         prompt = ("Create a short educational exercise")

#     return random.choice(exercises)


# def generate_english_exercise(level="A2", topic="grammar"):
#     prompt = build_english_prompt(level, topic)

#     response = client.chat.completions.create(
#         model="gpt-4o-mini",
#         messages=[
#             {"role": "system", "content": "You are a helpful English teacher."},
#             {"role": "user", "content": prompt}
#         ]
#     )

#     return response.choices[0].message.content
