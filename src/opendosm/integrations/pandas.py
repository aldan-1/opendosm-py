"""Pandas integration for the OpenDOSM SDK."""

from __future__ import annotations

import contextlib
from typing import Any

from pydantic import BaseModel

from opendosm.models import APIResponse


def to_dataframe(data: object) -> Any:
    """Convert API response data to a ``pandas.DataFrame``.

    Handles raw list-of-dicts responses, ``APIResponse`` objects, and lists
    of Pydantic models (e.g. from ``list_datasets()``).

    Args:
        data: Either a ``list[dict]``, a ``list[BaseModel]``, or an
            ``APIResponse``.

    Returns:
        A ``pandas.DataFrame`` with automatic date column inference and
        numeric type coercion.

    Raises:
        ImportError: If pandas is not installed.
        TypeError: If data is not a supported type.
    """
    try:
        import pandas as pd
    except ImportError:
        raise ImportError(
            "pandas is required for DataFrame conversion. "
            "Install it with: pip install opendosm[pandas]"
        ) from None

    records: list[dict[str, Any]] | Any

    if isinstance(data, APIResponse):
        records = data.data
    elif isinstance(data, list):
        # Auto-convert Pydantic models to dicts
        if data and isinstance(data[0], BaseModel):
            records = [item.model_dump() for item in data]
        else:
            records = data
    else:
        raise TypeError(
            f"Expected list or APIResponse, got {type(data).__name__}. "
            "Pass the data list or an APIResponse from a meta=True request."
        )

    df = pd.DataFrame(records)

    # Auto-detect and parse date-like columns
    _infer_dates(df)

    # Coerce object columns that are actually numeric
    _coerce_numerics(df)

    return df


def _infer_dates(df: Any) -> None:
    """Try to parse columns that look like dates into datetime dtype."""
    import pandas as pd

    date_hints = ("date", "timestamp", "year_month", "year")
    for col in df.columns:
        col_lower = str(col).lower()
        if any(hint in col_lower for hint in date_hints):
            with contextlib.suppress(Exception):
                df[col] = pd.to_datetime(df[col], errors="coerce")


def _coerce_numerics(df: Any) -> None:
    """Coerce object columns containing numeric data (possibly with nulls).

    Columns with values like ``[2.05, None, 2.10]`` arrive as ``object``
    dtype because of the ``None``.  This converts them to proper numeric
    types so aggregation methods work immediately.
    """
    import pandas as pd

    for col in df.columns:
        if df[col].dtype == object:
            converted = pd.to_numeric(df[col], errors="coerce")
            # Only apply if at least half the non-null values converted
            non_null = df[col].notna().sum()
            if non_null > 0 and converted.notna().sum() >= non_null * 0.5:
                df[col] = converted
