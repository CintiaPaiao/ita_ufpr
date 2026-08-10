from __future__ import annotations
from io import BytesIO
import pandas as pd


def list_excel_sheets(filename: str, raw: bytes) -> list[str]:
    if filename.lower().endswith((".xlsx",".xls")):
        return pd.ExcelFile(BytesIO(raw)).sheet_names
    return []


def read_uploaded_bytes(filename: str, raw: bytes, sheet_name=0) -> pd.DataFrame:
    bio=BytesIO(raw)
    if filename.lower().endswith(".csv"):
        return pd.read_csv(bio)
    return pd.read_excel(bio,sheet_name=sheet_name)


def choose_legacy_main_sheet(filename: str, raw: bytes) -> str|int:
    sheets=list_excel_sheets(filename,raw)
    for preferred in ("PLANILHA COMPLETA","Planilha Completa","PLANILHA_COMPLETA","Sheet1"):
        if preferred in sheets:
            return preferred
    return sheets[0] if sheets else 0


def normalize_sector_from_sheet(sheet: str) -> str:
    s=sheet.strip().lower()
    if "social" in s: return "SERVICO_SOCIAL_P4E"
    if "psico" in s: return "PSICOLOGIA_P4E"
    if "pedagog" in s: return "PEDAGOGIA_P4E"
    if "acess" in s or "caise" in s: return "CAISE_P4E"
    if "cppov" in s or "povos" in s: return "CPPOVOS_PROAFE"
    if "catrim" in s: return "CATRIM_ERI"
    if "cas" == s or s.startswith("cas "): return "CAS_PROAFE"
    return sheet.strip().upper().replace(" ","_")
