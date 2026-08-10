import streamlit as st, pandas as pd
from sqlalchemy import select
from src.ui.common import page_setup
from src.db.session import session_scope
from src.models.models import Cycle,Prioritization,Student
from src.services.case_service import build_case_summary

page_setup("Fichas Pré-Análise", allowed_roles=('ADMIN', 'PROFISSIONAL', 'CHEFIA'))
with session_scope() as s:
    cycles=list(s.scalars(select(Cycle).order_by(Cycle.codigo)))
    if not cycles: st.stop()
    cycle=st.selectbox("Ciclo",cycles,format_func=lambda c:c.codigo,index=len(cycles)-1)
    prs=list(s.scalars(select(Prioritization).where(Prioritization.cycle_id==cycle.id).order_by(Prioritization.camada,Prioritization.ordem_na_camada)))
    for pr in prs[:500]:
        stt=s.get(Student,pr.student_id); sm=build_case_summary(s,pr.student_id,cycle.id)
        with st.expander(f"{pr.camada} • {stt.nome} • {stt.grr} • {sm['next_action']}"):
            c1,c2,c3=st.columns(3)
            c1.write(f"**IAL:** {sm['ial'].score:.1f}" if sm['ial'] and sm['ial'].score is not None else "**IAL:** não calculável")
            c2.write("**Fase:** "+("Reavaliação" if sm['is_reassessment'] else "Primeira análise"))
            c3.write("**Cobertura:** "+(f"{sm['ial'].cobertura:.0f}%" if sm['ial'] else "—"))
            st.write("**Razões da priorização:**",pr.razoes)
            st.write("**MCN:**"," • ".join(f"Art.{x.artigo} {x.status}" for x in sm['mcn']))
            protecoes=[x for x in sm['protections'] if x.pre_analise]
            st.write("**Proteção prévia:**",", ".join(sorted({f"{x.fator} [{x.fonte}]" for x in protecoes})) or "não identificada nas fontes consultadas")
            st.write("**Acompanhamentos:**",", ".join(sorted({f"{x.setor} ({x.estado})" for x in sm['accompaniments']})) or "não identificados")
            if sm.get('legacy_process'):
                lp=sm['legacy_process']
                st.caption("Há registro histórico do processo de 2025 preservado como legado. Ele não é convertido em IAL, CRPS ou decisão atual.")
                st.write("**Registro legado:**", {"responsável 2025/1":lp.responsavel_2025_1,"1º parecer":lp.parecer_1,"situação 1":lp.situacao_1,"2º parecer":lp.parecer_2})
            st.success("Próxima ação: "+sm['next_action'])
