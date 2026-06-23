from database.db import Session
from database.models import MessageTemplate, Student
from services.logger import logger


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
    session = Session()

    student = session.get(Student, student_id)

    session.close()

    if not student:
        logger.warning(f"Student {student_id} not found during message formatting")
        return content

    template = get_template(template_type)

    if not template:
        logger.warning(f"Template '{template_type}' not found")
        return content

    # 🔥 CRITICAL FIX: prevent double header insertion
    header_marker = "Your Streak:"
    if header_marker in content:
        logger.warning("Message already formatted → skipping reformat")
        return content

    message = template.template_text

    message = message.replace("{content}", content)
    message = message.replace("{streak}", str(student.streak or 0))

    logger.info(f"Formatted {template_type} message for student {student.full_name}")

    return message