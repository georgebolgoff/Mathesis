from datetime import date
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

    
    # SAME DAY -> do nothing
    elif student.last_sent_date == today:
        session.close()
        return student.streak
    
    # NEXT DAY -> increase streak
    else:
        student.streak += 1
    
    student.last_sent_date = today

    session.commit()
    session.close()

    return student.streak

