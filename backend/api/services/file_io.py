from dataclasses import dataclass
from pathlib import Path
import pandas as pd
import csv

@dataclass
class LoadedFrame:
    df: pd.DataFrame
    name: str
    ext: str

SUPPORTED = {".csv", ".xlsx", ".xls"}

# -----------------------
# Decoding & newline
# -----------------------
def _read_bytes(filepath: Path) -> bytes:
    return filepath.read_bytes()

def _decode_best_effort(raw: bytes) -> str:
    try:
        return raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        pass

    try:
        return raw.decode("gb18030")
    except UnicodeDecodeError:
        pass

    for enc in ("big5", "shift_jis", "utf-16", "utf-32", "cp1252"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue

    return raw.decode("latin-1", errors="replace")

def _normalize_newlines(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n")

# -----------------------
# CSV parsing (loose)
# -----------------------
_CANDIDATE_DELIMS = [",", ";", "\t", "|"]

def _detect_delimiter(lines: list[str]) -> str:
    N = min(50, len(lines))
    scores = {d: 0 for d in _CANDIDATE_DELIMS}
    for i in range(N):
        line = lines[i]
        for d in _CANDIDATE_DELIMS:
            scores[d] += line.count(d)
    return max(scores, key=lambda k: scores[k]) if any(scores.values()) else ","

def _dedupe_and_fill_headers(headers: list[str]) -> list[str]:
    cleaned: list[str] = []
    counts: dict[str, int] = {}
    for idx, h in enumerate(headers, start=1):
        name = (h or "").strip()
        if not name:
            name = f"Unnamed_{idx}"
        base = name
        if base in counts:
            counts[base] += 1
            name = f"{base}_{counts[base]}"
        else:
            counts[base] = 1
        cleaned.append(name)
    return cleaned

def _parse_csv_with_header(text: str) -> pd.DataFrame:
    lines = text.splitlines()
    if not lines:
        return pd.DataFrame()

    delim = _detect_delimiter(lines)

    reader = csv.reader(lines, delimiter=delim)
    rows = [list(r) for r in reader]
    if not rows:
        return pd.DataFrame()

    raw_header = rows[0]
    data_rows = rows[1:]

    max_data_cols = max((len(r) for r in data_rows), default=0)
    header_len = len(raw_header)

    if max_data_cols > header_len:
        extras = [f"Extra_{i}" for i in range(1, max_data_cols - header_len + 1)]
        raw_header = raw_header + extras
        header_len = len(raw_header)

    header = _dedupe_and_fill_headers(raw_header)

    norm_rows = []
    for r in data_rows:
        if len(r) < header_len:
            r = r + [""] * (header_len - len(r))
        else:
            r = r[:header_len]
        norm_rows.append(r)

    df = pd.DataFrame(norm_rows, columns=header)

    for c in df.columns:
        df[c] = df[c].astype("string")

    return df

# -----------------------
# Public API
# -----------------------
def load_to_df(filepath: Path) -> LoadedFrame:
    ext = filepath.suffix.lower()
    if ext not in SUPPORTED:
        raise ValueError(f"Unsupported file type: {ext}")

    if ext == ".csv":
        raw = _read_bytes(filepath)
        text = _decode_best_effort(raw)
        text = _normalize_newlines(text)
        df = _parse_csv_with_header(text)
        return LoadedFrame(df=df, name=filepath.name, ext=ext)

    df = pd.read_excel(filepath, dtype="string")
    return LoadedFrame(df=df, name=filepath.name, ext=ext)
