from datetime import date,timedelta
from src.domain.monitoring.alerts import deadline_status
def test_deadline():
    t=date(2026,8,9);assert deadline_status(t-timedelta(days=1),t)=='VENCIDO';assert deadline_status(t+timedelta(days=2),t)=='VENCENDO';assert deadline_status(t+timedelta(days=10),t)=='NO_PRAZO'
