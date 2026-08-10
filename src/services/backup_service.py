from __future__ import annotations
from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path
import json, sqlite3, zipfile
from src.db.session import DATABASE_URL, database_backend
from src.exports.unified_excel import export_unified_workbook


def sqlite_backup_bytes() -> bytes | None:
    if database_backend() != "sqlite":
        return None
    path=DATABASE_URL.replace("sqlite:///", "", 1)
    src=sqlite3.connect(path)
    tmp=Path("database/.backup_temp.db")
    dst=sqlite3.connect(tmp)
    try:
        src.backup(dst)
    finally:
        dst.close(); src.close()
    data=tmp.read_bytes(); tmp.unlink(missing_ok=True)
    return data


def institutional_backup_zip(session) -> bytes:
    out=BytesIO()
    manifest={
        "generated_at":datetime.now(timezone.utc).isoformat(),
        "database_backend":database_backend(),
        "contains_real_data_warning":"Este backup pode conter dados pessoais/sensíveis. Armazenar em ambiente institucional restrito.",
    }
    with zipfile.ZipFile(out,"w",zipfile.ZIP_DEFLATED) as z:
        z.writestr("manifest.json",json.dumps(manifest,ensure_ascii=False,indent=2))
        z.writestr("planilha_unificada.xlsx",export_unified_workbook(session))
        db=sqlite_backup_bytes()
        if db is not None:
            z.writestr("pae.sqlite.backup.db",db)
    return out.getvalue()
