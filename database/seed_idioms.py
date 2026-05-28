from database.db import Session
from database.models import Idiom


def seed_idioms():

    session = Session()

    existing = session.query(Idiom).first()

    if existing:
        session.close()
    
    idioms = [

        # EASY
        {
            "level": "easy",
            "content": (
                "Break the ice\n\n"
                "Meaning: start a conversation "
                "in a social situation."
            )
        },

        {
            "level": "easy",
            "content": (
                "Piece of cake\n\n"
                "Meaning: very easy."
            )
        },

        # MEDIUM
        {
            "level": "medium",
            "content": (
                "Hit the nail on the head\n\n"
                "Meaning: say exactly "
                "the right thing."
            )
        },

        # HARD
        {
            "level": "hard",
            "content": (
                "Burn the candle at both ends\n\n"
                "Meaning: work too hard "
                "without enough rest."
            )
        }
    ]

    for item in idioms:

        idiom = Idiom(
            level=item["level"],
            content=item["content"]
        )

        session.add(idiom)
    

    session.commit()

    session.close()

    print("Idioms seeded successfully")