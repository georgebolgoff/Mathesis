from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.models import Base

BASE_DIR = Path(__file__).resolve().parent.parent

DB_PATH = BASE_DIR / "students.db"

engine = create_engine(f"sqlite:///{DB_PATH}",
    connect_args={"check_same_thread": False})

Session = sessionmaker(bind=engine)

Base.metadata.create_all(engine)

print(DB_PATH)
