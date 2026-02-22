from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
from utils import clean_dataframe

app = FastAPI(title="N.E.D. Excel Cleaner API")

class SheetData(BaseModel):
    data: list        # list of dicts [{col1: val1, col2: val2}, ... ]

@app.post("/clean")
def clean(sheet: SheetData):
    df = pd.DataFrame(sheet.data)
    cleaned = clean_dataframe(df)
    return {"cleaned_data": cleaned.to_dict(orient="records")}