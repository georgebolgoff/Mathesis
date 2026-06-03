import random

from services.logger import logger
from database.db import Session
from database.models import Idiom, IdiomHistory

def generate_idiom(level, student_id):

    level = level.lower().strip()

    session = Session()

    used_idioms_ids = {

        row.idiom_id

        for row in (
            session.query(IdiomHistory)
            .filter_by(student_id=student_id)
            .all()

        )
    }
    
    logger.info(f"Used idiom IDs: {used_idioms_ids}")

    idioms = (

        session.query(Idiom)
        .filter_by(level=level)
        .all()
    )

    filtered = [

        idiom 
        
        for idiom in idioms 

        if idiom.id not in used_idioms_ids 
    ]

    if not filtered:
        session.close()

        return {
            "ok": False,
            "message": "No idioms left",
            "content": None,
            "id": None
        }

    idiom = random.choice(filtered)

    session.close()

    return {
        "ok": True,
        "content": idiom.content,
        "id": idiom.id
    }


def save_idiom_history(
        student_id,
        idiom_id
    ):

    session = Session()

    history = IdiomHistory(
        student_id=student_id,
        idiom_id=idiom_id
    )

    session.add(history)

    session.commit()

    session.close()

