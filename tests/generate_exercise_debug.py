


from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(ROOT))

from database.db import Session
from database.models import Student

from datetime import datetime

session = Session()

for student in session.query(Student).all():

    if student.streak > 0 and not student.last_approved_exercise_at:

        student.last_approved_exercise_at = datetime.utcnow()

session.commit()
session.close()

print("fixed")