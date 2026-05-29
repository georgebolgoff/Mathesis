from database.db import Session
from database.models import MessageTemplate, Student


def get_template(template_type: str):
    session = Session()

    template = (
        session.query(MessageTemplate)
        .filter_by(template_type=template_type)
        .first()
    )

    session.close()

    return template


def format_message(student_id: int, content: str, template_type: str):
    """
    Core formatting engine for ALL outgoing messages.
    """

    session = Session()

    student = session.get(Student, student_id)

    session.close()

    if not student:
        return content
    
    # TODO: replace with real streak logic later
    streak = getattr(student, "streak", 1)

    template = get_template(template_type)

    if not template:
        return content
    
    message = template.template_text

    message = message.replace("{content}", content)
    message = message.replace("{streak}", str(streak))

    return message

