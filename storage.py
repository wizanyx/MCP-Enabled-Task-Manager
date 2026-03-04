import json
import os
import logging
import tempfile
from datetime import datetime, timezone
from pydantic import TypeAdapter, ValidationError
from models import Task

# Create an adapter to handle a list of Task objects
task_list_adapter = TypeAdapter(list[Task])
logger = logging.getLogger("mcp-todo")


def initialize_db(file_path: str):
    """Creates an empty tasks.json file if it doesn't exist."""
    if not os.path.exists(file_path):
        directory = os.path.dirname(file_path)
        if directory:
            os.makedirs(directory, exist_ok=True)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump([], f, indent=4)


def _quarantine_corrupt_file(file_path: str, error: Exception):
    """Moves a corrupt task DB aside and recreates an empty DB file."""
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    backup_path = f"{file_path}.corrupt-{timestamp}"
    try:
        if os.path.exists(file_path):
            os.replace(file_path, backup_path)
            logger.error("Corrupt tasks DB moved to %s (%s)", backup_path, error)
    except OSError:
        logger.exception("Failed to quarantine corrupt DB file: %s", file_path)
    finally:
        initialize_db(file_path)


def load_tasks(file_path: str) -> list[Task]:
    """Reads tasks from JSON and validates the entire list via Pydantic."""
    initialize_db(file_path)  # Ensure the file exists before reading
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            # Validates that the JSON data matches the List[Task] structure
            return task_list_adapter.validate_python(data)
    except (json.JSONDecodeError, ValidationError) as error:
        _quarantine_corrupt_file(file_path, error)
        return []
    except FileNotFoundError:
        initialize_db(file_path)
        return []


def save_tasks(tasks: list[Task], file_path: str):
    """Saves a list of Task objects to JSON with pretty-printing."""
    directory = os.path.dirname(file_path)
    if directory:
        os.makedirs(directory, exist_ok=True)
    json_data = [t.model_dump(mode="json") for t in tasks]
    with tempfile.NamedTemporaryFile(mode="w", dir=directory, delete=False, encoding="utf-8") as tmp:
        json.dump(json_data, tmp, indent=4)
        tmp_path = tmp.name
    os.replace(tmp_path, file_path)
