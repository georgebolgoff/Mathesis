def build_math_prompt(level):
    return f""" 
Create ONE short math exercise.

Difficulty: {level}

Keep it concise and suitable
for Telegram.

Do not include explanations.
"""


def build_english_prompt(level):
    return f""" 
Create ONE short English grammar
exercise.

Difficulty: {level}

Keep it concise and suitable
for Telegram.

Do not include explanations.
"""

def build_vocabulary_prompt(level):
    return f""" 
Create ONE short vocabulary task.

Difficulty: {level}

Keep it concise and suitable
for Telegram.
"""

def build_coding_prompt(level):
    return f""" 
Create ONE beginner coding exercise.

Difficulty: {level}

Keep it concise and suitable
for Telegram.
"""