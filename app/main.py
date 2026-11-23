
from contextlib import asynccontextmanager
import logging
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from app.database import Base, engine, SessionLocal
from app.models import Task

BASE_DIR = Path(__file__).resolve().parent

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger("nexus-pro")


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    logger.info("NEXUS-PRO started successfully")
    yield
    logger.info("NEXUS-PRO stopped")


app = FastAPI(
    title="NEXUS-PRO Task Manager API",
    description="Smart Task Management REST API",
    version="1.0.0",
    lifespan=lifespan
)

app.mount(
    "/static",
    StaticFiles(directory=str(BASE_DIR / "static")),
    name="static"
)

templates = Jinja2Templates(
    directory=str(BASE_DIR / "templates")
)


@app.get("/health")
def health():
    return {
        "status": "ok",
        "application": "NEXUS-PRO"
    }


@app.get("/api/tasks")
def list_tasks():
    try:
        with SessionLocal() as db:
            tasks = db.scalars(
                select(Task).order_by(Task.created_at.desc())
            ).all()

            return [task.to_dict() for task in tasks]

    except SQLAlchemyError:
        logger.exception("Task retrieval failed")
        raise HTTPException(
            status_code=500,
            detail="Could not retrieve tasks"
        )


@app.post("/api/tasks", status_code=201)
def create_task(payload: dict):
    title = str(payload.get("title", "")).strip()
    description = str(payload.get("description", "")).strip()
    priority = str(payload.get("priority", "medium")).lower()

    if not title or len(title) > 120:
        raise HTTPException(
            status_code=422,
            detail="Enter a valid task title"
        )

    if priority not in {"low", "medium", "high"}:
        raise HTTPException(
            status_code=422,
            detail="Invalid priority"
        )

    try:
        with SessionLocal() as db:
            task = Task(
                title=title,
                description=description,
                priority=priority
            )

            db.add(task)
            db.commit()
            db.refresh(task)

            return task.to_dict()

    except SQLAlchemyError:
        logger.exception("Task creation failed")
        raise HTTPException(
            status_code=500,
            detail="Could not create task"
        )


@app.patch("/api/tasks/{task_id}")
def update_task(task_id: int, payload: dict):
    allowed = {"title", "description", "priority", "status"}
    updates = {
        key: value
        for key, value in payload.items()
        if key in allowed
    }

    if not updates:
        raise HTTPException(
            status_code=400,
            detail="No valid fields supplied"
        )

    if "status" in updates and updates["status"] not in {
        "pending", "in_progress", "completed"
    }:
        raise HTTPException(
            status_code=422,
            detail="Invalid status"
        )

    if "priority" in updates and updates["priority"] not in {
        "low", "medium", "high"
    }:
        raise HTTPException(
            status_code=422,
            detail="Invalid priority"
        )

    try:
        with SessionLocal() as db:
            task = db.get(Task, task_id)

            if task is None:
                raise HTTPException(
                    status_code=404,
                    detail="Task not found"
                )

            for key, value in updates.items():
                if isinstance(value, str):
                    value = value.strip()
                setattr(task, key, value)

            db.commit()
            db.refresh(task)

            return task.to_dict()

    except SQLAlchemyError:
        logger.exception("Task update failed")
        raise HTTPException(
            status_code=500,
            detail="Could not update task"
        )


@app.delete("/api/tasks/{task_id}", status_code=204)
def delete_task(task_id: int):
    try:
        with SessionLocal() as db:
            task = db.get(Task, task_id)

            if task is None:
                raise HTTPException(
                    status_code=404,
                    detail="Task not found"
                )

            db.delete(task)
            db.commit()

    except SQLAlchemyError:
        logger.exception("Task deletion failed")
        raise HTTPException(
            status_code=500,
            detail="Could not delete task"
        )


@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request):
    try:
        with SessionLocal() as db:
            tasks = db.scalars(
                select(Task).order_by(Task.created_at.desc())
            ).all()

            return templates.TemplateResponse(
                request=request,
                name="index.html",
                context={
                    "tasks": tasks,
                    "total": len(tasks),
                    "completed": sum(
                        t.status == "completed" for t in tasks
                    ),
                    "pending": sum(
                        t.status == "pending" for t in tasks
                    )
                }
            )

    except SQLAlchemyError:
        logger.exception("Dashboard error")
        raise HTTPException(
            status_code=500,
            detail="Dashboard unavailable"
        )


@app.post("/tasks")
def create_task_form(
    title: str = Form(...),
    description: str = Form(""),
    priority: str = Form("medium")
):
    title = title.strip()

    if not title or len(title) > 120:
        raise HTTPException(
            status_code=422,
            detail="Invalid title"
        )

    if priority not in {"low", "medium", "high"}:
        raise HTTPException(
            status_code=422,
            detail="Invalid priority"
        )

    with SessionLocal() as db:
        db.add(
            Task(
                title=title,
                description=description.strip(),
                priority=priority
            )
        )
        db.commit()

    return RedirectResponse("/", status_code=303)


@app.post("/tasks/{task_id}/status")
def change_status(
    task_id: int,
    status: str = Form(...)
):
    if status not in {"pending", "in_progress", "completed"}:
        raise HTTPException(
            status_code=422,
            detail="Invalid status"
        )

    with SessionLocal() as db:
        task = db.get(Task, task_id)

        if task is None:
            raise HTTPException(
                status_code=404,
                detail="Task not found"
            )

        task.status = status
        db.commit()

    return RedirectResponse("/", status_code=303)


@app.post("/tasks/{task_id}/delete")
def delete_task_form(task_id: int):
    with SessionLocal() as db:
        task = db.get(Task, task_id)

        if task is None:
            raise HTTPException(
                status_code=404,
                detail="Task not found"
            )

        db.delete(task)
        db.commit()

    return RedirectResponse("/", status_code=303)
          
