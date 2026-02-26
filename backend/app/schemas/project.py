"""Project and membership request/response schema definitions."""

from datetime import datetime
from typing import Literal
from pydantic import BaseModel, EmailStr, Field

class ProjectCreate(BaseModel):
    name: str
    key: str
    description: str | None = None

class ProjectOut(BaseModel):
    id: int
    name: str
    key: str
    description: str | None
    created_at: datetime

    class Config:
        from_attributes = True

class ProjectMemberAdd(BaseModel):
    email: EmailStr
    role: Literal["member", "maintainer"]

class ProjectMemberUpdate(BaseModel):
    role: Literal["member", "maintainer"]

class ProjectMemberOnboard(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)
    role: Literal["member", "maintainer"] = "member"

class ProjectMemberOut(BaseModel):
    user_id: int
    name: str
    email: EmailStr
    role: Literal["member", "maintainer"]
