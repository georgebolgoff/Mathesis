def build_english_prompt(level="A2", topic="general"):
    return f"""
You are an English teacher.

Create an English exercise for a student with level {level}.

Topic: {topic}

Include:
1. 3 grammar questions
2. 3 vocabulary tasks
3. 1 short writing exercise

Make it simple, clear, and suitable for a classroom student.
"""