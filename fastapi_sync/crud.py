from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from orm import models
from . import schemas


def get_todos(db: Session, skip: int = 0, limit: int = 10) -> list[models.Todo]:
    try:
        return db.query(models.Todo).offset(skip).limit(limit).all()
    except SQLAlchemyError as e:
        print(e)
        raise HTTPException(status_code=500, detail="Failed to fetch todos")


def get_todo_by_id(db: Session, id: int) -> models.Todo | None:
    try:
        todo = db.query(models.Todo).filter(models.Todo.id == id).first()
        if not todo:
            raise HTTPException(status_code=404, detail="Todo not found")
        return todo
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail="Failed to fetch todo by ID")


def create_todo(db: Session, todo: schemas.TodoCreate) -> models.Todo:
    try:
        db_todo = models.Todo(
            title=todo.title, description=todo.description, done=todo.done
        )
        db.add(db_todo)
        db.commit()
        db.refresh(db_todo)
        return db_todo
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create todo")


def update_todo(db: Session, id: int, todo: schemas.TodoUpdate, partial: bool = False) -> models.Todo | None:
    try:
        db_todo = db.query(models.Todo).filter(models.Todo.id == id).first()
        if not db_todo:
            raise HTTPException(status_code=404, detail="Todo not found")
        todo_data = todo.model_dump(exclude_unset=True) if partial else todo.model_dump()
        for key, value in todo_data.items():
            setattr(db_todo, key, value)
        db.add(db_todo)
        db.commit()
        db.refresh(db_todo)
        return db_todo
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to update todo")


def delete_todo_by_id(db: Session, id: int) -> None:
    try:
        db_todo = db.query(models.Todo).filter(models.Todo.id == id).first()
        if not db_todo:
            raise HTTPException(status_code=404, detail="Todo not found")
        db.delete(db_todo)
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to delete todo")
