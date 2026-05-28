def build_topic_prompt(selected_data):

    level = selected_data.get(
        "level",
        "medium"
    )

    grammar_topics = selected_data.get(
        "grammar_topics",
        []
    )

    vocabulary_topics = selected_data.get(
        "vocabulary_topics",
        []
    )

    exercise_types = selected_data.get(
        "exercise_types",
        []
    )

    skills = selected_data.get(
        "skills",
        []
    )

    difficulty_modifiers = selected_data.get(
        "difficulty_modifiers",
        []
    )

    themes = selected_data.get(
        "themes",
        []
    )

    prompt = f"""
Generate ONE English exercise.

Difficulty:
{level}

IMPORTANT RULES:
- concise
- educational
- Telegram friendly
- no explanations
- realistic English
- student-friendly
- only output the exercise itself
"""
    if grammar_topics:

        prompt += "\n\nFocus grammar topics:\n"

        for topic in grammar_topics:

            prompt += f"{topic}\n"
    
    if vocabulary_topics:

        prompt += "\n\nFocus vocabulary topics:\n"

        for topic in vocabulary_topics:

            prompt += f"- {topic}\n"
    
    if exercise_types:

        prompt += "\n\nExercise types:\n"

        for item in exercise_types:

            prompt += f"- {item}\n"
    
    if skills:

        prompt += "\n\nTarget skills:\n"

        for skill in skills:

            prompt += f"- {skill}\n"
    
    if difficulty_modifiers:

        prompt += "\n\nDiffculty modifiers:\n"

        for item in difficulty_modifiers:

            prompt += f"- {item}\n"
    
    if themes:

        prompt += "\n\nEducational themes:\n"

        for item in themes:

            prompt += f"- {item}\n"
    
    prompt += """
Generate a UNIQUE exercise.
Do not generate explanations.
Do not generate answers.
"""

    return prompt
