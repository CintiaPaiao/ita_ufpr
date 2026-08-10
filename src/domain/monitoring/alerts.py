from datetime import date,timedelta
def deadline_status(deadline,today=None):
    if deadline is None:return 'SEM_PRAZO'
    today=today or date.today()
    return 'VENCIDO' if deadline<today else 'VENCENDO' if deadline<=today+timedelta(days=3) else 'NO_PRAZO'
