import os
import json
import threading
from openai import OpenAI

from dotenv import load_dotenv

from database.db import Session
from database.models import Exercise

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1"
)

#Prevent duplicate simultaneous refills

active_refills = set()

def request_ai_refill(subject, level):

    key = f"{subject}:{level}"

    if key in active_refills:
        return

    active_refills.add(key)

    thread = threading.Thread(
        target=refill_exercises,
        args=(subject, level),
        daemon=True
    )

    thread.start()


def refill_exercises(subject, level, custom_prompt=None):

    try:

        print(
            f"AI REFILL STARTED:"
            f"{subject} / {level}"
        )


        if custom_prompt:

            prompt = custom_prompt
        else:

            prompt = f"""
Generate 30 unique {subject} exercises.

Difficulty: {level}

Rules:
- short
- concise
- Telegram friendly
- no explanations
- all exercises different

Return ONLY valid JSON array.

Example:
[
  "Exercise 1",
  "Exercise 2"
]
"""
        response = client.chat.completions.create(
            model="deepseek/deepseek-chat",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        raw_text = (response.choices[0].message.content.strip())

        raw_text = (raw_text.replace("```json", "").replace("```", "").strip())

        exercises = json.loads(raw_text)

        session = Session()

        added = 0

        for content in exercises:

            exists = (
                session.query(Exercise)
                .filter_by(content=content)
                .first()
            )

            if exists:

                continue
            
            exercise = Exercise(
                subject=subject,
                level=level,
                content=content,
            )

            session.add(exercise)

            added += 1

        session.commit()

        session.close()

        print(
            f"AI REFILL COMPLETE: "
            f"{added} exercises added"
        )
    
    except Exception as e:


        print(
            f"AI REFILL FAILED: {e}"
        )
        
    finally:

        key = f"{subject}:{level}"

        active_refills.discard(key)