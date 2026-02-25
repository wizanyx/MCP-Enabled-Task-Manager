import json
import os
from pydantic import TypeAdapter, ValidationError
from models import Task

# Create an adapter to handle a list of Task objects
task_list_adapter = TypeAdapter(list[Task])


def initialize_db(file_path: str):
    """Creates an empty tasks.json file if it doesn't exist."""
    if not os.path.exists(file_path):
        with open(file_path, "w") as f:
            json.dump([], f, indent=4)


def load_tasks(file_path: str) -> list[Task]:
    """Reads tasks from JSON and validates the entire list via Pydantic."""
    initialize_db(file_path)  # Ensure the file exists before reading
    try:
        with open(file_path, "r") as f:
            data = json.load(f)
            # Validates that the JSON data matches the List[Task] structure
            return task_list_adapter.validate_python(data)
    except (json.JSONDecodeError, ValidationError, FileNotFoundError):
        # If file is corrupt or invalid, return an empty list for safety
        return []


def save_tasks(tasks: list[Task], file_path: str):
    """Saves a list of Task objects to JSON with pretty-printing."""
    with open(file_path, "w") as f:
        # model_dump(mode='json') handles the conversion of datetime/UUID to strings
        json_data = [t.model_dump(mode="json") for t in tasks]
        json.dump(json_data, f, indent=4)
