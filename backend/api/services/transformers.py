import pandas as pd
import re
from typing import Iterable
from .llm_regex import safe_compile

TEXT_DTYPES = {"object", "string"}


def _text_columns(df: pd.DataFrame) -> list[str]:
    return [c for c in df.columns if str(df[c].dtype) in TEXT_DTYPES]




def regex_replace(df: pd.DataFrame, pattern: str, replacement: str, columns: Iterable[str] | None = None) -> pd.DataFrame:
    rx = safe_compile(pattern)
    cols = list(columns) if columns else _text_columns(df)
    out = df.copy()
    for c in cols:
        out[c] = out[c].astype("string").str.replace(rx, replacement, regex=True)
    return out


# --- Optional creative transforms ---
def normalize_au_phone(df: pd.DataFrame, columns: Iterable[str] | None = None) -> pd.DataFrame:
    """Convert AU numbers to +61 format where possible."""
    cols = list(columns) if columns else _text_columns(df)
    out = df.copy()
    rx = re.compile(r"(?:\+?61|0)([2-478])(\d{7,8})")
    def fmt(s: str) -> str:
        return rx.sub(lambda m: "+61" + m.group(1) + m.group(2), s)
    for c in cols:
        out[c] = out[c].astype("string").map(lambda v: fmt(v) if isinstance(v, str) else v)
    return out


def normalize_dates(df: pd.DataFrame, to_fmt: str = "%Y-%m-%d", columns: Iterable[str] | None = None) -> pd.DataFrame:
    cols = list(columns) if columns else _text_columns(df)
    out = df.copy()
    for c in cols:
        out[c] = pd.to_datetime(out[c], errors="ignore", dayfirst=True).astype("string")
    # Re-parse and standardize where parseable
    for c in cols:
        out[c] = pd.to_datetime(out[c], errors="coerce").dt.strftime(to_fmt).fillna(out[c])
    return out