from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.models import Base

engine = create_engine("sqlite:///students.db", connect_args={"check_same_thread": False})

Session = sessionmaker(bind=engine)

Base.metadata.create_all(engine)
