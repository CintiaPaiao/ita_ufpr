from io import BytesIO
import pandas as pd
from sqlalchemy import select
from src.models import models as m
SHEETS=[('00_CONTROLE',m.Execution),('01_UNIVERSO',m.Student),('02_MCN',m.MCNResult),('03_IAL',m.IALResult),('04_FATORES_PROTECAO',m.ProtectionFactor),('05_ACOMPANHAMENTOS',m.Accompaniment),('06_PRIORIZACAO_300',m.Prioritization),('07_CASOS_DISTRIBUIDOS',m.Allocation),('08_CONTEXTUALIZACAO',m.Contextualization),('09_MAIC',m.MAIC),('10_MNA',m.MNA),('11_PIAAP',m.PIAAP),('12_MANUTENCAO',m.Maintenance),('13_MONITORAMENTO',m.Monitoring),('14_REAVALIACAO',m.Reassessment),('15_CRPS',m.CRPS),('16_RECURSOS',m.Appeal),('17_AUDITORIA',m.AuditLog)]
def export_unified_workbook(session):
    out=BytesIO()
    with pd.ExcelWriter(out,engine='xlsxwriter') as w:
        for sheet,model in SHEETS:
            rows=list(session.scalars(select(model)));pd.DataFrame([{c.name:getattr(r,c.name) for c in model.__table__.columns} for r in rows]).to_excel(w,sheet_name=sheet,index=False)
        d=[]
        for sheet,model in SHEETS:
            for c in model.__table__.columns:d.append({'aba':sheet,'coluna':c.name,'tipo':str(c.type),'nullable':c.nullable,'primary_key':c.primary_key})
        pd.DataFrame(d).to_excel(w,sheet_name='18_DICIONARIO_DADOS',index=False)
    return out.getvalue()
