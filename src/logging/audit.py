from src.models.models import AuditLog
def log_action(session,**kw):
    obj=AuditLog(**{k:v for k,v in kw.items() if hasattr(AuditLog,k)});session.add(obj);session.flush();return obj
