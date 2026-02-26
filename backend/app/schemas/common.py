"""Shared schema models used across multiple API responses."""

from pydantic import BaseModel

class ErrorResponse(BaseModel):
    error: dict
