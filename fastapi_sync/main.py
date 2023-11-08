from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session

from . import crud, schemas
from .db import get_db


app = FastAPI()


@app.get("/", include_in_schema=False)
def root():
    return {"message": "Hello World"}


@app.get("/todos", status_code=200)
def todos_list(
    db: Session = Depends(get_db), skip: int = 0, limit: int = 10
) -> list[schemas.Todo]:
    todos = crud.get_todos(db, skip, limit)
    return todos


@app.get("/todos/{id}", status_code=200, responses={404: {"model": schemas.NotFound}})
def todo_detail(id: int, db: Session = Depends(get_db)) -> schemas.Todo:
    print(id)
    todo = crud.get_todo_by_id(db, id)
    return todo


@app.post("/todos", status_code=201)
def todo_create(
    todo: schemas.TodoCreate, db: Session = Depends(get_db)
) -> schemas.Todo:
    todo = crud.create_todo(db, todo)
    return todo


@app.put("/todos/{id}", status_code=200, responses={404: {"model": schemas.NotFound}})
def todo_update(
    id: int, todo: schemas.TodoUpdate, db: Session = Depends(get_db)
) -> schemas.Todo:
    todo = crud.update_todo(db, id, todo, partial=False)
    return todo


@app.patch("/todos/{id}", status_code=200, responses={404: {"model": schemas.NotFound}})
def todo_partial_update(
    id: int, todo: schemas.TodoUpdate, db: Session = Depends(get_db)
) -> schemas.Todo:
    todo = crud.update_todo(db, id, todo, partial=True)
    return todo


@app.delete(
    "/todos/{id}", status_code=204, responses={404: {"model": schemas.NotFound}}
)
def todo_delete(id: int, db: Session = Depends(get_db)) -> None:
    crud.delete_todo_by_id(db, id)
    return None
