from __future__ import annotations
import json
from src.models.models import AuditLog

def _serialize(v):
    if v is None or isinstance(v, str):
        return v
    try:
        return json.dumps(v, ensure_ascii=False, default=str)
    except Exception:
        return str(v)

def log_action(session, *, username=None, action: str, entity=None, entity_id=None,
               cycle_code=None, grr=None, old_value=None, new_value=None, reason=None,
               code_version="0.3.0", rule_version=None):
    obj = AuditLog(
        username=username,
        action=action,
        entity=entity,
        entity_id=str(entity_id) if entity_id is not None else None,
        cycle_code=cycle_code,
        grr=grr,
        old_value=_serialize(old_value),
        new_value=_serialize(new_value),
        reason=reason,
        code_version=code_version,
        rule_version=rule_version,
    )
    session.add(obj)
    session.flush()
    return obj
