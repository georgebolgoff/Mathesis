from datetime import date, timedelta
from database.db import Session
from database.models import Student


def update_streak(student_id: int):

    session = Session()

    student = session.get(Student, student_id)

    if not student:
        session.close()
        return 0
    
    today = date.today()

    # FIRST TIME EVER
    if not student.last_sent_date:
        student.streak = 1

    
    # already sent today

    elif student.last_sent_date == today:

        session.close()

        return student.streak
    
    # yesterday -> continue streak

    elif (
        student.last_sent_date == today - timedelta(days=1)
    ):
        student.streak += 1

    
    # missed at least one day -> reset
    
    else:
        student.streak += 1
    
    student.last_sent_date = today

    session.commit()

    current_streak = student.streak

    session.close()

    return current_streak

