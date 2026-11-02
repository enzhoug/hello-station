from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Response
from pydantic import BaseModel, ConfigDict, Field

from app import database, repository


class TaskCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    title: str = Field(min_length=1, max_length=200)


class TaskUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    title: str | None = Field(default=None, min_length=1, max_length=200)
    done: bool | None = None


class Task(BaseModel):
    id: int
    title: str
    done: bool


@asynccontextmanager
async def lifespan(_app: FastAPI):
    database.initialize()
    yield


app = FastAPI(title="Hello Station", version="0.1.0", lifespan=lifespan)


@app.get("/")
def home():
    return {"service": "hello-station", "docs": "/docs", "health": "/health"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/api/tasks", response_model=list[Task])
def list_tasks():
    return repository.list_tasks()


@app.post("/api/tasks", response_model=Task, status_code=201)
def create_task(task: TaskCreate):
    return repository.create_task(task.title)


@app.get("/api/tasks/{task_id}", response_model=Task)
def get_task(task_id: int):
    task = repository.get_task(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@app.patch("/api/tasks/{task_id}", response_model=Task)
def update_task(task_id: int, task: TaskUpdate):
    changes = task.model_dump(exclude_unset=True)
    if not changes or any(value is None for value in changes.values()):
        raise HTTPException(status_code=422, detail="Provide at least one non-null field")
    result = repository.update_task(task_id, changes)
    if result is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return result


@app.delete("/api/tasks/{task_id}", status_code=204)
def delete_task(task_id: int):
    if not repository.delete_task(task_id):
        raise HTTPException(status_code=404, detail="Task not found")
    return Response(status_code=204)
