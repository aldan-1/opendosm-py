"""Pydantic models for OpenDOSM API responses."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class MetaInfo(BaseModel):
    """Metadata about the API response.

    Returned when `?meta=true` is included in the request.
    """

    model_config = {"extra": "allow"}


class APIResponse(BaseModel):
    """Structured API response when `?meta=true` is used.

    Attributes:
        meta: Metadata about the dataset and applied filters.
        data: The list of data records.
    """

    meta: Optional[MetaInfo] = None
    data: List[Dict[str, Any]] = Field(default_factory=list)


class ErrorDetail(BaseModel):
    """A single error detail from the API."""

    message: str = ""

    model_config = {"extra": "allow"}


class ErrorResponse(BaseModel):
    """Error response structure from the API.

    Attributes:
        status: HTTP status code.
        errors: List of error details.
    """

    status: int
    errors: List[Any] = Field(default_factory=list)
