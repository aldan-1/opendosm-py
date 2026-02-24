"""Pydantic models for OpenDOSM API responses."""

from __future__ import annotations

from typing import Any

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

    meta: MetaInfo | None = None
    data: list[dict[str, Any]] = Field(default_factory=list)



class DatasetInfo(BaseModel):
    """Metadata for a single dataset in the data catalogue.

    Returned by :meth:`DataCatalogueAPI.list_datasets`.
    """

    id: str
    title_en: str = ""
    title_bm: str = ""
    category_en: str = ""
    category_bm: str = ""
    subcategory_en: str = ""
    subcategory_bm: str = ""
    source: str = ""
    frequency: str = ""
    geography: str = ""
    demography: str = ""
    dataset_begin: str = ""
    dataset_end: str = ""
    date_created: str = ""

    model_config = {"extra": "allow"}


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
    errors: list[Any] = Field(default_factory=list)
