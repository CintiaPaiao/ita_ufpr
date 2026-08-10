from __future__ import annotations
from datetime import datetime, timedelta, timezone
from sqlalchemy import delete
from src.models.models import AuditLog, Execution


def purge_technical_logs(session, *, older_than_days:int, dry_run:bool=True) -> dict:
    cutoff=datetime.now(timezone.utc).replace(tzinfo=None)-timedelta(days=older_than_days)
    logs=session.query(AuditLog).filter(AuditLog.timestamp < cutoff).count()
    executions=session.query(Execution).filter(Execution.started_at < cutoff).count()
    if not dry_run:
        session.execute(delete(AuditLog).where(AuditLog.timestamp < cutoff))
        session.execute(delete(Execution).where(Execution.started_at < cutoff))
    return {"cutoff":cutoff.isoformat(),"logs":logs,"executions":executions,"dry_run":dry_run}
