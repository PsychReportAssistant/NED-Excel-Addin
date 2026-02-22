import pandas as pd
import numpy as np

STATE_MAP = {
    "al": "Alabama", "ak": "Alaska", "az": "Arizona", "ar": "Arkansas", "ca": "California",
    # ... all other states as before
}

def clean_column(series, dtype):
    if dtype == "email":
        return (series.str.lower().str.strip()
                .str.replace("(at)", "@", regex=False)
                .str.replace(r'@{2,}', '@', regex=True)
                .str.replace(r'\.{2,}', '.', regex=True))
    if dtype == "date":
        parsed = pd.to_datetime(series, errors='coerce', format='mixed')
        mask = parsed.isna() & series.notna()
        if mask.any():
            day_first = pd.to_datetime(series[mask], errors='coerce', dayfirst=True)
            parsed.update(day_first)
        return parsed.dt.strftime('%Y-%m-%d').fillna(series)
    if dtype == "name":
        def fix_name(x):
            if pd.isna(x): return x
            s = str(x).strip()
            if ',' in s:
                parts = s.split(',')
                if len(parts) == 2:
                    s = f"{parts[1]} {parts[0]}"
            return ' '.join(s.split()).title()
        return series.apply(fix_name)
    return series

def detect_type(series):
    sample = series.dropna()
    if sample.empty: return "name"
    is_email = sample.str.contains(r'@', na=False).mean() > 0.4
    date_check = pd.to_datetime(sample, errors='coerce', format='mixed')
    is_date = date_check.notna().mean() > 0.4
    is_numeric = pd.to_numeric(sample.str.replace(r'[^\d.-]', '', regex=True), errors='coerce').notna().mean() > 0.6
    is_state = sample.str.lower().str.replace(".", "", regex=False).isin(STATE_MAP.keys()).mean() > 0.3
    if is_email: return "email"
    elif is_date: return "date"
    elif is_numeric: return "numeric"
    elif is_state: return "state"
    else: return "name"

def clean_dataframe(df):
    cleaned = pd.DataFrame()
    for col in df.columns:
        dtype = detect_type(df[col])
        cleaned[col+"_clean"] = clean_column(df[col], dtype)
    return cleaned