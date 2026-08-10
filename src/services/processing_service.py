from __future__ import annotations
import json,re
from sqlalchemy import select, delete
from src.models.models import *
from src.domain.mcn.rules import RuleResult,calcular_art17,calcular_art18,calcular_art19,calcular_art20,calcular_art21
from src.domain.ial.calculator import rendimento_component,frequencia_component,progressao_component,calculate_ial
from src.domain.prioritization.engine import PriorityInput,prioritize
from src.config.settings import PRIORITY_CONFIG, IAL_CONFIG, MCN_CONFIG
from src.services.base_status_service import required_ready
from src.logging.audit import log_action


def period_key(p):
    s=str(p or "")
    m=re.search(r"(\d{4}).*?([12])",s)
    if m:return int(m.group(1))*10+int(m.group(2))
    return -1


def _as_rate(v):
    if v is None:return None
    try:x=float(v)
    except Exception:return None
    return x/100 if x>1 else x


def _history_periods(session, student_id):
    rows=list(session.scalars(select(AcademicHistory).where(AcademicHistory.student_id==student_id)))
    return sorted({x.periodo for x in rows},key=period_key)


def _approval_pct(rows):
    eligible=[x for x in rows if x.cancelado is not True]
    if not eligible:return None
    known=[x for x in eligible if x.aprovado is not None]
    if not known:return None
    return 100*sum(x.aprovado is True for x in known)/len(known)


def _freq_rate(rows):
    eligible=[x for x in rows if x.cancelado is not True]
    if not eligible:return None
    known=[x for x in eligible if x.rep_freq is not None]
    if not known:return None
    return sum(x.rep_freq is True for x in known)/len(eligible)


def _approved_ch(rows):
    vals=[x.ch for x in rows if x.aprovado is True and x.ch is not None]
    return sum(vals) if vals else None


def _curriculum_param(session, st):
    if not st.codigo_curso and not st.curso:return None
    rows=[]
    if st.codigo_curso:
        rows=list(session.scalars(select(CurriculumParameter).where(CurriculumParameter.codigo_curso==st.codigo_curso)))
    if not rows and st.curso:
        rows=list(session.scalars(select(CurriculumParameter).where(CurriculumParameter.codigo_curso==st.curso)))
    if st.curriculo and rows:
        exact=[x for x in rows if x.curriculo==st.curriculo]
        if exact:rows=exact
    if st.campus and rows:
        exact=[x for x in rows if x.campus==st.campus]
        if exact:rows=exact
    return rows[0] if rows else None


def _snapshot(session, sid, cycle_id):
    return session.scalar(select(LegacyAcademicSnapshot).where(LegacyAcademicSnapshot.student_id==sid,LegacyAcademicSnapshot.cycle_id==cycle_id))


def _mcn_from_discipline_data(session, st, cycle, current_rows):
    mand=[]
    if st.codigo_curso:
        mand=list(session.scalars(select(MandatoryDiscipline).where(MandatoryDiscipline.codigo_curso==st.codigo_curso)))
    if st.curriculo and mand:
        exact=[x for x in mand if x.curriculo==st.curriculo]
        if exact:mand=exact
    current_codes={x.disciplina_codigo for x in current_rows if x.cancelado is not True}
    approved_codes={x.disciplina_codigo for x in session.scalars(select(AcademicHistory).where(AcademicHistory.student_id==st.id,AcademicHistory.aprovado==True))}
    art17=calcular_art17(mandatory_enrolled=(any(m.disciplina_codigo in current_codes for m in mand) if mand else None),all_mandatory_completed=(all(m.disciplina_codigo in approved_codes for m in mand) if mand else None))
    par=_curriculum_param(session,st)
    chmat=sum(x.ch or 0 for x in current_rows if x.cancelado is not True) if any(x.ch is not None for x in current_rows) else None
    art18=calcular_art18(ch_matriculada=chmat,ch_minima=par.ch_minima_art18 if par else None,grau_evidencia=par.grau_evidencia if par else None)
    eligible=[x for x in current_rows if x.cancelado is not True]
    art19=calcular_art19(n_disciplinas=len(eligible),rep_freq=sum(x.rep_freq is True for x in eligible))
    rates=list(session.scalars(select(ClassApprovalRate).where(ClassApprovalRate.periodo==cycle.codigo)))
    rate_map={(x.disciplina_codigo,x.turma):x for x in rates}
    comps=[]
    for x in current_rows:
        rate=rate_map.get((x.disciplina_codigo,x.turma)) or rate_map.get((x.disciplina_codigo,None))
        comps.append({"cancelado":x.cancelado,"aprovado":x.aprovado,"taxa_turma":rate.taxa_aprovacao_pct if rate else None,"taxa_turma_validada":rate.validada if rate else False})
    art20=calcular_art20(components=comps)
    it=session.scalar(select(IntegrationTime).where(IntegrationTime.student_id==st.id,IntegrationTime.cycle_id==cycle.id))
    art21=calcular_art21(periodos_computaveis=it.periodos_computaveis if it else None,periodos_regulares=(it.periodos_regulares if it and it.periodos_regulares else par.duracao_regular_periodos if par else None))
    return [art17,art18,art19,art20,art21]


def _mcn_from_legacy_snapshot(session, st, cycle, snap):
    # Art.17 exige informação de componente obrigatório, ausente na PLANILHA COMPLETA agregada.
    art17=RuleResult("17","DADO_PENDENTE",{"motivo":"Planilha legada agregada não identifica disciplinas obrigatórias."},True)
    par=_curriculum_param(session,st)
    art18=calcular_art18(ch_matriculada=snap.ch_mat_total,ch_minima=par.ch_minima_art18 if par else None,grau_evidencia=par.grau_evidencia if par else None)
    art19=calcular_art19(n_disciplinas=snap.qtd_matriculada,rep_freq=snap.qtd_rep_freq)
    # O percentual legado não permite verificar exclusões do art.20 por turma. Preserva o valor observado e exige conferência.
    if snap.aprovacao_pct is None:
        art20=RuleResult("20","DADO_PENDENTE",{"motivo":"Percentual de aprovação não disponível."},True)
    else:
        art20=RuleResult("20","REQUER_CONFERENCIA",{"aprovacao_observada_pct":snap.aprovacao_pct,"motivo":"Base agregada não demonstra exclusão de cancelamentos/turmas <50% exigida pela metodologia atual."},True)
    # TEMPO UFPR-SEM é vínculo bruto; sem dados de trancamento/tempo computável, não sustenta conclusão restritiva.
    regular=(par.duracao_regular_periodos if par else None)
    if snap.tempo_sem is not None and regular is not None:
        limite=regular*float(MCN_CONFIG["art21"]["max_regular_factor"])
        art21=RuleResult("21","REQUER_CONFERENCIA",{"periodos_vinculo_observados":snap.tempo_sem,"periodos_regulares":regular,"limite_150":limite,"motivo":"Tempo computável não confirmado; vínculo bruto não substitui cálculo normativo."},True)
    else:
        art21=RuleResult("21","REQUER_CONFERENCIA",{"motivo":"Parâmetros/tempo computável insuficientes."},True)
    return [art17,art18,art19,art20,art21]


def _mcn_for_student(session, st, cycle, current_rows):
    if current_rows:
        return _mcn_from_discipline_data(session,st,cycle,current_rows)
    snap=_snapshot(session,st.id,cycle.id)
    if snap:
        return _mcn_from_legacy_snapshot(session,st,cycle,snap)
    return [RuleResult(str(a),"DADO_PENDENTE",{"motivo":"Base acadêmica não disponível."},True) for a in range(17,22)]


def _ial_from_discipline_data(session, st, cycle, current_rows):
    periods=_history_periods(session,st.id)
    previous=[p for p in periods if period_key(p)<period_key(cycle.codigo)][-3:]
    prev_rows={p:list(session.scalars(select(AcademicHistory).where(AcademicHistory.student_id==st.id,AcademicHistory.periodo==p))) for p in previous}
    current_ap=_approval_pct(current_rows)
    prev_aps=[_approval_pct(prev_rows[p]) for p in previous]
    prev_aps=[x for x in prev_aps if x is not None]
    prev_mean=sum(prev_aps)/len(prev_aps) if prev_aps else None
    r=rendimento_component(current_ap,prev_mean)
    eligible=[x for x in current_rows if x.cancelado is not True]
    f=frequencia_component(len(eligible),sum(x.rep_freq is True for x in eligible),[_freq_rate(prev_rows[p]) for p in previous])
    it=session.scalar(select(IntegrationTime).where(IntegrationTime.student_id==st.id,IntegrationTime.cycle_id==cycle.id))
    par=_curriculum_param(session,st)
    recent=previous[-2:]+[cycle.codigo]
    ch_recent=0;known=False
    for p0 in recent[-2:]:
        rows=current_rows if p0==cycle.codigo else prev_rows.get(p0,[])
        ch=_approved_ch(rows)
        if ch is not None:ch_recent+=ch;known=True
    total=it.ch_total if it and it.ch_total else par.ch_total if par else None
    reg=it.periodos_regulares if it and it.periodos_regulares else par.duracao_regular_periodos if par else None
    expected_two=(total/reg*2) if total and reg else None
    pace=(ch_recent/expected_two) if known and expected_two else None
    p=progressao_component(it.ch_integralizada if it else None,total,it.periodos_computaveis if it else None,reg,pace)
    return calculate_ial(r,f,p)


def _ial_from_legacy_snapshot(session, st, cycle, snap):
    # Rendimento atual é utilizável; tendência fica ausente se não houver snapshot anterior comparável.
    prior_snap=session.scalar(select(LegacyAcademicSnapshot).join(Cycle,LegacyAcademicSnapshot.cycle_id==Cycle.id).where(LegacyAcademicSnapshot.student_id==st.id,Cycle.codigo!=cycle.codigo).order_by(Cycle.codigo.desc()))
    prior_ap=prior_snap.aprovacao_pct if prior_snap else None
    r=rendimento_component(snap.aprovacao_pct,prior_ap)
    hist=[_as_rate(x) for x in [snap.hist_rf_3,snap.hist_rf_2,snap.hist_rf_1] if x is not None]
    f=frequencia_component(snap.qtd_matriculada,snap.qtd_rep_freq,hist)
    # Progressão só é calculada quando existe duração regular confirmada. CH integralizada da planilha antiga é percentual.
    par=_curriculum_param(session,st)
    if snap.ch_integralizada_pct is not None and snap.tempo_sem is not None and par and par.duracao_regular_periodos:
        observado=max(0,min(1,snap.ch_integralizada_pct/100 if snap.ch_integralizada_pct>1 else snap.ch_integralizada_pct))
        esperado=min(1,snap.tempo_sem/par.duracao_regular_periodos)
        gap=max(0,esperado-observado)
        ref=float(IAL_CONFIG["parameters"]["progress_gap_reference"])
        p=min(1,gap/ref)
    else:
        p=None
    return calculate_ial(r,f,p)


def _ial_for_student(session, st, cycle, current_rows):
    if current_rows:return _ial_from_discipline_data(session,st,cycle,current_rows)
    snap=_snapshot(session,st.id,cycle.id)
    if snap:return _ial_from_legacy_snapshot(session,st,cycle,snap)
    return calculate_ial(None,None,None)


def _longitudinal_worsening(session, sid, current_ial):
    prior=list(session.scalars(select(IALResult).join(Cycle,IALResult.cycle_id==Cycle.id).where(IALResult.student_id==sid).order_by(Cycle.codigo.desc())))
    prior=[x for x in prior if x.score is not None and x.score != current_ial.score]
    return bool(prior and current_ial.score is not None and current_ial.score > prior[0].score + 5)


def process_cycle(session, *, cycle_code: str, username: str, n_cases: int|None=None, allow_incomplete: bool=False):
    cycle=session.scalar(select(Cycle).where(Cycle.codigo==cycle_code))
    if not cycle:raise ValueError("Ciclo não cadastrado")
    ready,missing=required_ready(session,cycle_code)
    # Compatibilidade 0.3: PLANILHA COMPLETA legada pode substituir, para homologação/uso transitório, SIGA+histórico detalhado+integralização.
    has_legacy=session.scalar(select(LegacyAcademicSnapshot.id).where(LegacyAcademicSnapshot.cycle_id==cycle.id).limit(1)) is not None
    effective_missing=list(missing)
    if has_legacy:
        for b in ["SIGA_BENEFICIARIOS","HISTORICO_ACADEMICO","INTEGRALIZACAO_TEMPO","PARAMETROS_CURRICULARES","DISCIPLINAS_OBRIGATORIAS"]:
            if b in effective_missing: effective_missing.remove(b)
    if effective_missing and not allow_incomplete:
        raise ValueError("Bases obrigatórias pendentes: "+", ".join(effective_missing))
    for model in (MCNResult,IALResult,Prioritization,Allocation):
        session.execute(delete(model).where(model.cycle_id==cycle.id))
    beneficiaries=list(session.scalars(select(Benefit).where(Benefit.cycle_id==cycle.id)))
    student_ids=sorted({b.student_id for b in beneficiaries})
    inputs=[]
    for sid in student_ids:
        st=session.get(Student,sid)
        current=list(session.scalars(select(AcademicHistory).where(AcademicHistory.student_id==sid,AcademicHistory.periodo==cycle_code)))
        mcn_res=_mcn_for_student(session,st,cycle,current)
        for rr in mcn_res:
            session.add(MCNResult(student_id=sid,cycle_id=cycle.id,artigo=rr.artigo,status=rr.status,evidencia=json.dumps(rr.evidencia,ensure_ascii=False),fonte="PROCESSAMENTO_0.3",qualidade_dado="REQUER_CONFERENCIA" if rr.requer_conferencia else "CALCULADO",requer_conferencia=rr.requer_conferencia,regra_versao=MCN_CONFIG.get("version","MCN")))
        ial=_ial_for_student(session,st,cycle,current)
        session.add(IALResult(student_id=sid,cycle_id=cycle.id,r=ial.r,f=ial.f,p=ial.p,score=ial.score,cobertura=ial.coverage,status=ial.status,faixa=ial.band,versao=IAL_CONFIG.get("version","IAL")))
        noncomp=sum(x.status=="NAO_ATENDE" for x in mcn_res); pend=sum(x.requer_conferencia for x in mcn_res)
        hist=bool(session.scalar(select(EvaluationHistory.id).where(EvaluationHistory.student_id==sid).limit(1)))
        prot=bool(session.scalar(select(ProtectionFactor.id).where(ProtectionFactor.student_id==sid,ProtectionFactor.cycle_id==cycle.id,ProtectionFactor.pre_analise==True).limit(1)))
        acomp=bool(session.scalar(select(Accompaniment.id).where(Accompaniment.student_id==sid,Accompaniment.cycle_id==cycle.id).limit(1)))
        inputs.append(PriorityInput(grr=st.grr,mcn_noncompliance_count=noncomp,mcn_pending_count=pend,ial_score=ial.score,ial_band=ial.band,reassessment=hist,longitudinal_worsening=_longitudinal_worsening(session,sid,ial),protective_priority=prot,intervention_need=(acomp and (noncomp>0 or (ial.score or 0)>=35)),institutional_barrier=False,near_completion=False))
    n=n_cases or int(PRIORITY_CONFIG.get("selection",{}).get("n_cases",300))
    priorit=prioritize(inputs,min(n,len(inputs)))
    for idx,r in enumerate(priorit,1):
        st=session.scalar(select(Student).where(Student.grr==r.grr))
        session.add(Prioritization(student_id=st.id,cycle_id=cycle.id,camada=r.layer,ordem_na_camada=idx,razoes="; ".join(r.reasons),pre_selecionado=True,validado_equipe=False,selecionado_final=False))
    cycle.status="PRIORIZACAO"
    log_action(session,username=username,action="PROCESSAR_CICLO_0_3",entity="ciclo",entity_id=cycle.id,cycle_code=cycle_code,new_value={"universo":len(student_ids),"priorizados":len(priorit),"bases_pendentes":effective_missing,"modo_legado":has_legacy},reason="Processamento integrado com compatibilidade às bases da Calculadora ITA 2025")
    session.flush()
    return {"universo":len(student_ids),"priorizados":len(priorit),"missing_bases":effective_missing,"legacy_mode":has_legacy}
