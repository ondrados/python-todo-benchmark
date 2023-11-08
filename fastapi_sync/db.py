from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine("sqlite:////Users/ondrados/dev/personal/python_todo/fastapi_sync/test.db", connect_args={"check_same_thread": False})

session = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = session()
    try:
        yield db
    finally:
        db.close()
