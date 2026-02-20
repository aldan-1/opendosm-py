"""Pandas integration for the OpenDOSM SDK."""

from __future__ import annotations

from typing import Any, Dict, List, Union

from opendosm.models import APIResponse


def to_dataframe(data: object) -> Any:
    """Convert API response data to a ``pandas.DataFrame``.

    Handles both raw list-of-dicts responses and ``APIResponse`` objects.

    Args:
        data: Either a ``list[dict]`` from the API, or an ``APIResponse``.

    Returns:
        A ``pandas.DataFrame`` with automatic date column inference.

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

    records: Union[List[Dict[str, Any]], Any]

    if isinstance(data, APIResponse):
        records = data.data
    elif isinstance(data, list):
        records = data
    else:
        raise TypeError(
            f"Expected list or APIResponse, got {type(data).__name__}. "
            "Pass the data list or an APIResponse from a meta=True request."
        )

    df = pd.DataFrame(records)

    # Auto-detect and parse date-like columns
    _infer_dates(df)

    return df


def _infer_dates(df: Any) -> None:
    """Try to parse columns that look like dates into datetime dtype."""
    import pandas as pd

    date_hints = ("date", "timestamp", "year_month", "year")
    for col in df.columns:
        col_lower = str(col).lower()
        if any(hint in col_lower for hint in date_hints):
            try:
                df[col] = pd.to_datetime(df[col], errors="coerce")
            except Exception:
                pass
