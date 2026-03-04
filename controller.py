from typing import Literal
from pathlib import Path
import logging

from models import Task
from storage import load_tasks, save_tasks

DB_FILE = str(Path(__file__).resolve().parent / "data" / "tasks.json")
logger = logging.getLogger("mcp-todo")


def add_task(title: str, description: str = "", file_path: str = DB_FILE) -> Task:
    """Creates and persists a new task, then returns it."""
    new_task = Task(title=title, description=description)
    tasks = load_tasks(file_path)
    tasks.append(new_task)
    save_tasks(tasks, file_path)
    return new_task


def get_task(task_id: str, file_path: str = DB_FILE) -> Task | None:
    """Returns a single task by id."""
    tasks = load_tasks(file_path)
    for task in tasks:
        if task.id == task_id:
            return task

    return None


def get_tasks(
    status: Literal["pending", "completed"] | None = None, file_path: str = DB_FILE
) -> list[Task]:
    """Returns all persisted tasks."""
    tasks = load_tasks(file_path)
    if status is not None:
        tasks = [task for task in tasks if task.status == status]
    return tasks


def update_task(
    task_id: str,
    title: str | None = None,
    description: str | None = None,
    status: Literal["pending", "completed"] | None = None,
    file_path: str = DB_FILE,
) -> Task | None:
    """Updates a task and returns it."""
    tasks = load_tasks(file_path)
    for index, task in enumerate(tasks):
        if task.id == task_id:
            updated_task = task.model_copy(
                update={
                    "title": title if title is not None else task.title,
                    "description": (
                        description if description is not None else task.description
                    ),
                    "status": status if status is not None else task.status,
                }
            )
            tasks[index] = updated_task
            save_tasks(tasks, file_path)
            return updated_task
    
    return None


def delete_task(task_id: str, file_path: str = DB_FILE) -> bool:
    """Deletes a task by id and returns a confirmation message."""
    tasks = load_tasks(file_path)
    for index, task in enumerate(tasks):
        if task.id == task_id:
            tasks.pop(index)
            save_tasks(tasks, file_path)
            logger.info(f"Deletion: removed task id={task_id}")
            return True

    return False


def clear_completed(file_path: str = DB_FILE) -> int:
    """Removes all tasks marked as completed. Returns count of removed tasks."""
    tasks = load_tasks(file_path)
    initial_count = len(tasks)
    tasks = [t for t in tasks if t.status != "completed"]
    save_tasks(tasks, file_path)
    removed_count = initial_count - len(tasks)
    if removed_count > 0:
        logger.info(f"Deletion: cleared {removed_count} completed task(s)")
    return removed_count
