from __future__ import annotations
from io import BytesIO
import pandas as pd
from sqlalchemy import select
from src.models import models as m

SHEETS=[
    ('00_CONTROLE',m.Execution),('02_MCN',m.MCNResult),('03_IAL',m.IALResult),
    ('04_FATORES_PROTECAO',m.ProtectionFactor),('05_ACOMPANHAMENTOS',m.Accompaniment),
    ('06_PRIORIZACAO_300',m.Prioritization),('07_CASOS_DISTRIBUIDOS',m.Allocation),
    ('08_CONTEXTUALIZACAO',m.Contextualization),('09_MAIC',m.MAIC),('10_MNA',m.MNA),
    ('12_MANUTENCAO',m.Maintenance),('13_MONITORAMENTO',m.Monitoring),('14_REAVALIACAO',m.Reassessment),
    ('15_CRPS',m.CRPS),('16_RECURSOS',m.Appeal),('17_AUDITORIA',m.AuditLog)
]

def _df(rows, model):
    return pd.DataFrame([{c.name:getattr(r,c.name) for c in model.__table__.columns} for r in rows])

def _universo_df(session):
    students={s.id:s for s in session.scalars(select(m.Student))}
    benefits=list(session.scalars(select(m.Benefit)))
    snaps={(x.student_id,x.cycle_id):x for x in session.scalars(select(m.LegacyAcademicSnapshot))}
    cycles={c.id:c for c in session.scalars(select(m.Cycle))}
    rows=[]
    # Uma linha por estudante × ciclo de benefício, preservando o universo processável.
    for b in benefits:
        st=students.get(b.student_id); cy=cycles.get(b.cycle_id); snap=snaps.get((b.student_id,b.cycle_id))
        row={
            'student_id':b.student_id,'GRR':st.grr if st else None,'NOME':st.nome if st else None,
            'curso':st.curso if st else None,'codigo_curso':st.codigo_curso if st else None,
            'curriculo':st.curriculo if st else None,'campus':st.campus if st else None,'ingresso':st.ingresso if st else None,
            'ciclo':cy.codigo if cy else None,'beneficio':b.modalidade,'status_beneficio':b.status,
        }
        if snap:
            for col in ['setor','proafe','motivo','renda_per_capita','ano_ingresso','tempo_sem','ch_integralizada_pct','qtd_matriculada','qtd_rep_nota','qtd_rep_freq','qtd_cancelada','ira_sem','aprovacao_pct','ch_recomendada_sem','ch_mat_total','hist_rf_1','hist_rf_2','hist_rf_3','hist_rf_media','avaliacao_anterior','legacy_ita']:
                row[f'legado_{col}']=getattr(snap,col)
        rows.append(row)
    return pd.DataFrame(rows)

def _piaap_df(session):
    plans={p.id:p for p in session.scalars(select(m.PIAAP))}
    actions=list(session.scalars(select(m.PIAAPAction)))
    rows=[]
    for a in actions:
        p=plans.get(a.piaap_id)
        rows.append({'piaap_id':a.piaap_id,'student_id':p.student_id if p else None,'cycle_id':p.cycle_id if p else None,
                     'objetivo_geral':p.objetivo_geral if p else None,'status_plano':p.status if p else None,
                     'acao_id':a.id,'tipo':a.tipo,'descricao':a.descricao,'parte_responsavel':a.parte_responsavel,
                     'responsavel':a.responsavel,'prazo':a.prazo,'indicador':a.indicador,'status_acao':a.status,'resultado':a.resultado})
    if not rows:
        for p in plans.values(): rows.append({'piaap_id':p.id,'student_id':p.student_id,'cycle_id':p.cycle_id,'objetivo_geral':p.objetivo_geral,'status_plano':p.status})
    return pd.DataFrame(rows)

def export_unified_workbook(session):
    out=BytesIO()
    with pd.ExcelWriter(out,engine='xlsxwriter') as w:
        # 00 controle: execuções + ciclos + importações em uma aba auditável.
        execs=_df(list(session.scalars(select(m.Execution))),m.Execution)
        cycles=_df(list(session.scalars(select(m.Cycle))),m.Cycle); cycles.insert(0,'registro_tipo','CICLO') if not cycles.empty else None
        imports=_df(list(session.scalars(select(m.ImportedFile))),m.ImportedFile); imports.insert(0,'registro_tipo','ARQUIVO_IMPORTADO') if not imports.empty else None
        if not execs.empty: execs.insert(0,'registro_tipo','EXECUCAO')
        pd.concat([execs,cycles,imports],ignore_index=True,sort=False).to_excel(w,sheet_name='00_CONTROLE',index=False)
        _universo_df(session).to_excel(w,sheet_name='01_UNIVERSO',index=False)
        for sheet,model in SHEETS:
            if sheet=='00_CONTROLE': continue
            _df(list(session.scalars(select(model))),model).to_excel(w,sheet_name=sheet,index=False)
        _piaap_df(session).to_excel(w,sheet_name='11_PIAAP',index=False)
        dictionary=[]
        for table in m.Base.metadata.sorted_tables:
            for c in table.columns:
                dictionary.append({'tabela':table.name,'coluna':c.name,'tipo':str(c.type),'nullable':c.nullable,'primary_key':c.primary_key})
        pd.DataFrame(dictionary).to_excel(w,sheet_name='18_DICIONARIO_DADOS',index=False)
    return out.getvalue()
