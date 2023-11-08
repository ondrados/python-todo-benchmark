import pytest
import requests
import time
from orm import models
from .conftest import BASE_URL


def test_available():
    response = requests.get(f"{BASE_URL}/")

    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}


def test_todos_list(test_app, db_session):
    # Arrange: Prepare the data and dependencies
    todos_data = [
        {"title": "Todo1", "description": "Description1", "done": False},
        {"title": "Todo2", "description": "Description2", "done": True},
        # Add more sample todos if needed
    ]
    for todo in todos_data:
        new_todo = models.Todo(**todo)
        db_session.add(new_todo)
        db_session.commit()

    # Act: Make a request to the endpoint
    response = requests.get(f"{BASE_URL}/todos?skip=0&limit=10")

    # Assert: Check if the response matches the expected output
    assert response.status_code == 200
    assert len(response.json()) == len(todos_data)
    assert response.json()[0]["title"] == todos_data[0]["title"]
    assert response.json()[1]["title"] == todos_data[1]["title"]


def test_todo_create(test_app, db_session):
    # Arrange: Prepare the data and dependencies
    todo_data = {"title": "Todo1", "description": "Description1", "done": False}

    # Act: Make a request to the endpoint
    response = requests.post(f"{BASE_URL}/todos", json=todo_data)

    # Assert: Check if the response matches the expected output
    assert response.status_code == 201
    assert response.json()["title"] == todo_data["title"]
    assert response.json()["description"] == todo_data["description"]
    assert response.json()["done"] == todo_data["done"]

    db_todo = db_session.query(models.Todo).first()

    assert db_todo
    assert db_todo.id == response.json()["id"]
    assert db_todo.title == todo_data["title"]
    assert db_todo.description == todo_data["description"]
    assert db_todo.done == todo_data["done"]


@pytest.mark.parametrize(
    "todo_data, expected",
    [
        ({"title": "Todo1"}, {"title": "Todo1", "description": None, "done": False, "id": 1}),
        ({"title": "Todo1", "description": "Description1"}, {"title": "Todo1", "description": "Description1", "done": False, "id": 1}),
        ({"title": "Todo1", "done": True}, {"title": "Todo1", "description": None, "done": True, "id": 1}),
        ({"title": "Todo1", "done": False}, {"title": "Todo1", "description": None, "done": False, "id": 1})
    ],
)
def test_todo_create_incomplete_data(test_app, db_session, todo_data, expected):
    # Act: Make a request to the endpoint
    response = requests.post(f"{BASE_URL}/todos", json=todo_data)

    # Assert: Check if the response matches the expected output
    assert response.status_code == 201
    assert response.json() == expected


def test_create_todo_invalid_data(test_app, db_session):
    # Arrange: Prepare the data and dependencies
    todo_data = {"description": "Description1", "done": "False"}

    # Act: Make a request to the endpoint
    response = requests.post(f"{BASE_URL}/todos", json=todo_data)

    # Assert: Check if the response matches the expected output
    assert response.status_code == 422
    assert len(db_session.query(models.Todo).all()) == 0


def test_todo_detail(test_app, db_session):
    # Arrange: Prepare the data and dependencies
    todo_data = {"title": "Todo1", "description": "Description1", "done": False}
    new_todo = models.Todo(**todo_data)
    db_session.add(new_todo)
    db_session.commit()
    db_session.refresh(new_todo)

    # Act: Make a request to the endpoint
    response = requests.get(f"{BASE_URL}/todos/{new_todo.id}")

    # Assert: Check if the response matches the expected output
    assert response.status_code == 200
    assert response.json()["id"] == new_todo.id
    assert response.json()["title"] == todo_data["title"]
    assert response.json()["description"] == todo_data["description"]
    assert response.json()["done"] == todo_data["done"]


def test_todo_detail_not_found(test_app, db_session):
    # Arrange: Prepare the data and dependencies
    todo_data = {"title": "Todo1", "description": "Description1", "done": False}
    new_todo = models.Todo(**todo_data)
    db_session.add(new_todo)
    db_session.commit()
    db_session.refresh(new_todo)

    # Act: Make a request to the endpoint
    response = requests.get(f"{BASE_URL}/todos/{new_todo.id + 1}")

    # Assert: Check if the response matches the expected output
    assert response.status_code == 404
    assert response.json()["detail"] == "Todo not found"


# TODO: add parametrized input for update and partial update
def test_todo_update(test_app, db_session):
    # Arrange: Prepare the data and dependencies
    todo_data = {"title": "Todo1", "description": "Description1", "done": False}
    new_todo = models.Todo(**todo_data)
    db_session.add(new_todo)
    db_session.commit()
    db_session.refresh(new_todo)

    # Act: Make a request to the endpoint
    response = requests.put(
        f"{BASE_URL}/todos/{new_todo.id}", json={"title": "Todo1 Updated", "description": "Description1", "done": False}
    )

    # Assert: Check if the response matches the expected output
    assert response.status_code == 200
    assert response.json()["id"] == new_todo.id
    assert response.json()["title"] == "Todo1 Updated"
    assert response.json()["description"] == todo_data["description"]
    assert response.json()["done"] == todo_data["done"]

    db_todo = db_session.query(models.Todo).first()

    assert db_todo
    assert db_todo.id == new_todo.id
    assert db_todo.title == "Todo1 Updated"
    assert db_todo.description == todo_data["description"]
    assert db_todo.done == todo_data["done"]


def test_todo_partial_update(test_app, db_session):
    # Arrange: Prepare the data and dependencies
    todo_data = {"title": "Todo1", "description": "Description1", "done": False}
    new_todo = models.Todo(**todo_data)
    db_session.add(new_todo)
    db_session.commit()
    db_session.refresh(new_todo)

    # Act: Make a request to the endpoint
    response = requests.patch(
        f"{BASE_URL}/todos/{new_todo.id}", json={"title": "Todo1 Updated"}
    )

    # Assert: Check if the response matches the expected output
    assert response.status_code == 200
    assert response.json()["id"] == new_todo.id
    assert response.json()["title"] == "Todo1 Updated"
    assert response.json()["description"] == todo_data["description"]
    assert response.json()["done"] == todo_data["done"]

    db_todo = db_session.query(models.Todo).first()

    assert db_todo
    assert db_todo.id == new_todo.id
    assert db_todo.title == "Todo1 Updated"
    assert db_todo.description == todo_data["description"]
    assert db_todo.done == todo_data["done"]


def test_todo_delete(test_app, db_session):
    # Arrange: Prepare the data and dependencies
    todo_data = {"title": "Todo1", "description": "Description1", "done": False}
    new_todo = models.Todo(**todo_data)
    db_session.add(new_todo)
    db_session.commit()
    db_session.refresh(new_todo)

    # Act: Make a request to the endpoint
    response = requests.delete(f"{BASE_URL}/todos/{new_todo.id}")

    # Assert: Check if the response matches the expected output
    assert response.status_code == 204
    assert response.text == ""

    db_todo = db_session.query(models.Todo).first()

    assert db_todo is None
