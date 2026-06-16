# from datetime import date, timedelta
# from database.db import Session
# from database.models import Student
# from services.logger import logger


# def update_streak(student_id: int):

#     session = Session()

#     student = session.get(Student, student_id)

#     if not student:

#         logger.warning(f"Student {student_id} not found while updating streak")

#         session.close()
#         return {
#             "streak": 0,
#             "milestone": None
#         }
    
#     today = date.today()

#     # FIRST TIME EVER
#     if not student.last_sent_date:
#         student.streak = 1

#         logger.info(f"Started streak for {student.full_name}")

    
#     # already sent today

#     elif student.last_sent_date == today:

#         current_streak = student.streak

#         logger.info(f"Streak already updated today for {student.full_name}")

#         session.close()

#         return {
#             "streak": current_streak,
#             "milestone": None
#         }
    
#     # yesterday -> continue streak

#     elif (
#         student.last_sent_date == today - timedelta(days=1)
#     ):
#         student.streak += 1

#         logger.info(
#             f"Streak increased for {student.full_name} {student.streak}"
#         )

    
#     # missed at least one day -> reset
    
#     else:
#         logger.warning(f"Streak reset for {student.full_name}")
#         student.streak = 1
    
#     student.last_sent_date = today

#     session.commit()

#     current_streak = student.streak

#     milestone = None

#     if current_streak in [7, 30, 100]:

#         milestone = current_streak

#         logger.info(f"Milestone reached by {student.full_name} {milestone} days")

#     session.close()

#     return {
#         "streak": current_streak,
#         "milestone": milestone
#     }

