from __future__ import annotations
from sqlalchemy import select, func
from src.models.models import ImportedFile
from src.config.base_registry import BASES

def base_status(session, cycle_code: str) -> list[dict]:
    rows=[]
    for key,spec in BASES.items():
        latest=session.scalar(select(ImportedFile).where(ImportedFile.cycle_code==cycle_code,ImportedFile.source==key).order_by(ImportedFile.imported_at.desc()))
        rows.append({
            "tipo":key,"base":spec.get("label",key),"obrigatoria":bool(spec.get("required",False)),
            "status":"IMPORTADA" if latest else "PENDENTE",
            "arquivo":latest.filename if latest else None,"data":latest.imported_at if latest else None,
            "linhas":latest.row_count if latest else None,"grrs":latest.unique_grr if latest else None,
        })
    return rows

def required_ready(session, cycle_code: str) -> tuple[bool,list[str]]:
    status=base_status(session,cycle_code)
    missing=[r["tipo"] for r in status if r["obrigatoria"] and r["status"]!="IMPORTADA"]
    return not missing,missing
