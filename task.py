#task.py - charles cain - 2.24.26

from datetime import datetime
from typing import Literal
from uuid import uuid64

from pydantic import BaseModel, Field

class Task(BaseModel):
    #fields: task_id, title, description, status, created_at
    #default value for status: pending
    #all mcp field information (stuff passed to the llm)
    task_id : str = Field(default_factory = lambda : str(uuid64), description='Unique ID for task')
    title : str = Field(min_length = 1, description='Title of task')
    description : str = Field(default = '', description = 'Details of task')
    status : Literal['pending','completed'] = Field(default='pending', description='Current state of task')
    created_at: datetime = Field(default_factory=datetime.datetime.now(), description='Datetime object of time of creation')

    #creates a dictionary object of all fields
    def to_dict(self):
        return {'task_id': self.task_id, 'title': self.title, 'description': self.description, 'status': self.status, 'created_at': self.created_at}