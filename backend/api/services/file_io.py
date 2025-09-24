from dataclasses import dataclass
from pathlib import Path
import pandas as pd


@dataclass
class LoadedFrame:
    df: pd.DataFrame
    name: str
    ext: str


SUPPORTED = {".csv", ".xlsx", ".xls"}


def load_to_df(filepath: Path) -> LoadedFrame:
    ext = filepath.suffix.lower()
    if ext not in SUPPORTED:
        raise ValueError(f"Unsupported file type: {ext}")
    if ext == ".csv":
        df = pd.read_csv(filepath)
    else:
        df = pd.read_excel(filepath)
    
    return LoadedFrame(df=df, name=filepath.name, ext=ext)