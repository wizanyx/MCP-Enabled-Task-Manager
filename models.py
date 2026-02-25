from pydantic import BaseModel, Field
from datetime import datetime
from uuid import uuid4
from typing import Literal


class Task(BaseModel):
    id: str = Field(
        default_factory=lambda: str(uuid4()),
        description="Unique identifier for the task",
    )
    title: str = Field(
        ..., min_length=1, description="The short title or name of the task"
    )
    description: str = Field(
        default="", description="A more detailed explanation of what needs to be done"
    )
    status: Literal["pending", "completed"] = Field(
        default="pending", description="The current state of the task"
    )
    created_at: datetime = Field(
        default_factory=datetime.now,
        description="The ISO timestamp when the task was created",
    )

    class Config:
        # Ensures datetime is serialized as an ISO string in JSON
        json_encoders = {datetime: lambda v: v.isoformat()}
