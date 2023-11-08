import os
import pytest
import threading
import uvicorn
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from time import sleep

from orm.models import Base
from fastapi_sync.main import app, get_db as original_get_db

HOST = "127.0.0.1"
PORT = 8000
BASE_URL = f"http://{HOST}:{PORT}"


# Starting and stopping the FastAPI server, scoped to the entire test session
@pytest.fixture(scope="session", autouse=True)
def start_fastapi_server():
    config = uvicorn.Config("fastapi_sync.main:app", host=HOST, port=PORT, log_level="info")
    server = uvicorn.Server(config=config)
    thread = threading.Thread(target=server.run)
    thread.start()
    sleep(1)  # Give it some time to start properly before running the tests
    yield
    server.should_exit = True
    thread.join()


# Generate a unique database URL for each test function
@pytest.fixture(scope="function")
def test_db_url(request):
    return f"sqlite:///test_{request.node.name}.db"


# Creating and dropping the database for each test function
@pytest.fixture(scope="function")
def test_engine(test_db_url):
    engine = create_engine(test_db_url, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)  # Create tables for this test
    yield engine
    Base.metadata.drop_all(bind=engine)  # Drop tables after the test
    engine.dispose()
    # Delete the SQLite database file
    db_file_path = test_db_url.replace("sqlite:///", "")
    if os.path.exists(db_file_path):
        os.remove(db_file_path)


# Creating a new session for each test function
@pytest.fixture(scope="function")
def db_session(test_engine):
    session = sessionmaker(bind=test_engine)
    db = session()
    yield db
    db.close()


# Overriding the get_db dependency with the test session
@pytest.fixture(scope="function")
def test_app(db_session):
    app.dependency_overrides[original_get_db] = lambda: db_session
    yield app
    app.dependency_overrides = {}
