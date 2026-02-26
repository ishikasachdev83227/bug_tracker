from datetime import datetime
from typing import Literal
from pydantic import BaseModel

IssueStatus = Literal["open", "in_progress", "resolved", "closed"]
IssuePriority = Literal["low", "medium", "high", "critical"]

class IssueCreate(BaseModel):
    title: str
    description: str | None = None
    priority: IssuePriority = "medium"
    assignee_id: int | None = None

class IssueUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    status: IssueStatus | None = None
    priority: IssuePriority | None = None
    assignee_id: int | None = None

class IssueOut(BaseModel):
    id: int
    project_id: int
    title: str
    description: str | None
    status: IssueStatus
    priority: IssuePriority
    reporter_id: int
    assignee_id: int | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
