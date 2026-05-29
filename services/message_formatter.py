from database.db import Session
from database.models import MessageTemplate, ExerciseHistory, IdiomHistory



def get_student_streak(student_id, content_type):

    session = Session()

    try:

        if content_type == "exercise":

            streak = (
                session.query(ExerciseHistory)
                .filter_by(student_id=student_id)
                .count()
            ) + 1
        
        elif content_type == "idiom":

            streak = (
                session.query(IdiomHistory)
                .filter_by(student_id=student_id)
                .count()
            ) + 1
        
        else:

            streak = 1
        
        return streak
    
    finally:

        session.close()
    


def get_template(template_type):

    session = Session()

    try:

        template = (
            session.query(MessageTemplate)
            .filter_by(
                template_type=template_type
            )
            .first()
        )

        if not template:

            return "{content}"
        
        return template.template_text
    
    finally:

        session.close()


def format_message(
        student_id,
        content,
        template_type
):
    
    streak = get_student_streak(
        student_id,
        template_type
    )

    template = get_template(
        template_type
    )

    formatted = template.format(
        streak=streak,
        content=content
    )

    return formatted
