from typing import Literal

from models import Task
from storage import load_tasks, save_tasks

DB_FILE = "tasks.json"

def add_task(title: str, description: str = "", file_path: str = DB_FILE) -> Task:
    """Creates and persists a new task, then returns it."""
    new_task = Task(title=title, description=description)
    tasks = load_tasks(file_path)
    tasks.append(new_task)
    save_tasks(tasks, file_path)
    return new_task

def get_task(task_id: str, file_path: str = DB_FILE) -> Task:
    """Returns a single task by id.

    Raises:
        ValueError: If the provided task_id does not exist.
    """
    tasks = load_tasks(file_path)
    for task in tasks:
        if task.id == task_id:
            return task

    raise ValueError(f"Task with id '{task_id}' was not found.")

def get_tasks(file_path: str = DB_FILE, status: Literal["pending", "completed"] | None = None) -> list[Task]:
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
) -> Task:
    """Updates a task and returns it.

    Raises:
        ValueError: If the provided task_id does not exist.
    """
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

    raise ValueError(f"Task with id '{task_id}' was not found.")


def delete_task(task_id: str, file_path: str = DB_FILE) -> str:
    """Deletes a task by id and returns a confirmation message.

    Raises:
        ValueError: If the provided task_id does not exist.
    """
    tasks = load_tasks(file_path)
    for index, task in enumerate(tasks):
        if task.id == task_id:
            tasks.pop(index)
            save_tasks(tasks, file_path)
            return True

    return False

def clear_completed(file_path: str = DB_FILE) -> int:
    """Removes all tasks marked as completed. Returns count of removed tasks."""
    tasks = load_tasks(file_path)
    initial_count = len(tasks)
    tasks = [t for t in tasks if t.status != "completed"]
    save_tasks(tasks, file_path)
    return initial_count - len(tasks)
