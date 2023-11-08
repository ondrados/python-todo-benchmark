from typing import Optional

from pydantic import BaseModel


class NotFound(BaseModel):
    detail: str


class TodoBase(BaseModel):
    title: str
    description: Optional[str] = None
    done: bool = False


class TodoCreate(TodoBase):
    pass


class TodoUpdate(TodoBase):
    pass


class Todo(TodoBase):
    id: int
