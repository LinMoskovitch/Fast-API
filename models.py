from pydantic import BaseModel


class Task(BaseModel):
    id: int
    title: str
    description: str | None
    completed: bool = False