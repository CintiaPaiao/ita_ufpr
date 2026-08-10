from __future__ import annotations
import hashlib
from src.models.models import ImportedFile


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def register_import(session, *, filename: str, source: str, raw: bytes, username: str|None,
                    cycle_code: str|None, row_count: int|None, unique_grr: int|None,
                    schema_name: str|None, validation_status: str) -> ImportedFile:
    obj = ImportedFile(
        filename=filename,
        source=source,
        sha256=sha256_bytes(raw),
        username=username,
        cycle_code=cycle_code,
        row_count=row_count,
        unique_grr=unique_grr,
        schema_name=schema_name,
        validation_status=validation_status,
    )
    session.add(obj)
    session.flush()
    return obj
