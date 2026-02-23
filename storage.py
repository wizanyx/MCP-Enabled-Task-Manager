#storage.py - charles cain - 18.2.26

import json

from pydantic import TypeAdapter

from task import Task

"""reads json file and returns a dictionary of all tasks"""
def read_json(file_path) -> list[Task]:
    try:
        with open(file_path, 'r') as json_file:
            json_data = json.load(json_file)
    except (json.JSONDecodeError, FileNotFoundError):
        #returns empty list
        return []

    #Converts from JSON to Tasks:
    return TypeAdapter(list[Task]).validate_python(json_data)

"""takes a list of task objects in a dictionary and writes to file"""
def write_json(tasks: list[Task], file_path):
    #opens file and OVERWRITES it ('w')
    #closes after the 'with' block
    with open(file_path, 'w') as json_file:
        #convert task list to json
        #brackets make it a list
        task_json = [t.model_dump(mode='json') for t in tasks]

        #indent = 4 is default tab size
        json.dump(task_json, json_file, indent=4)