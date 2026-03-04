from pydantic import BaseModel, Field
from datetime import datetime, timezone
from uuid import uuid4
from typing import Literal


class Task(BaseModel):
    id: str = Field(
        default_factory=lambda: str(uuid4()),
        description="Stable UUID for the task. Use this exact value when updating or deleting an existing task.",
    )
    title: str = Field(
        ...,
        min_length=1,
        description="Short action-oriented task title, e.g. 'Submit report'. Must not be empty.",
    )
    description: str = Field(
        default="",
        description="Optional task details, constraints, or context that clarify what needs to be done.",
    )
    status: Literal["pending", "completed"] = Field(
        default="pending",
        description="Execution state of the task. Use 'pending' for open work and 'completed' for finished work.",
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Creation timestamp in ISO 8601 format. Generated automatically when a task is created.",
    )
