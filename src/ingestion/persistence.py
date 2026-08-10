from __future__ import annotations
import math, json
from datetime import datetime, date, timezone
import pandas as pd
from sqlalchemy import delete, select
from src.models.models import *
from src.validation.normalization import padronizar_grr, validar_grr
from src.ingestion.legacy_ita_profile import parse_raw_json, extract_embedded_accompaniments, extract_proafe_protection_factors, extract_legacy_process
from src.config.base_registry import get_base_spec

TRUE_VALUES={"1","true","sim","s","yes","y","x","ativo","identificado"}
FALSE_VALUES={"0","false","nao","não","n","no",""}

def _none(v):
    if v is None: return None
    try:
        if pd.isna(v): return None
    except Exception: pass
    return v

def _str(v):
    v=_none(v); return None if v is None else str(v).strip()

def _float(v):
    v=_none(v)
    if v is None: return None
    if isinstance(v,str): v=v.replace("%","").replace(".","").replace(",",".") if "," in v else v
    try: return float(v)
    except Exception: return None

def _int(v):
    x=_float(v); return int(x) if x is not None else None

def _bool(v):
    v=_none(v)
    if v is None: return None
    if isinstance(v,bool): return v
    s=str(v).strip().lower()
    if s in TRUE_VALUES: return True
    if s in FALSE_VALUES: return False
    # common academic statuses
    if "aprov" in s: return True
    if "reprov" in s or "cancel" in s: return False
    return None

def _date(v):
    v=_none(v)
    if v is None:return None
    try:return pd.to_datetime(v).date()
    except Exception:return None

def _get_or_create_student(session, grr, name=None, **attrs):
    g=padronizar_grr(grr)
    if not validar_grr(g): return None
    obj=session.scalar(select(Student).where(Student.grr==g))
    if not obj:
        obj=Student(grr=g,nome=_str(name) or g)
        session.add(obj);session.flush()
    elif name and (obj.nome==obj.grr or not obj.nome): obj.nome=_str(name)
    for key,val in attrs.items():
        if val is not None and hasattr(obj,key): setattr(obj,key,val)
    return obj

def _split_multi(v):
    s=_str(v)
    if not s:return []
    import re
    return [x.strip() for x in re.split(r"[;|,]",s) if x.strip()]

def _delete_cycle_rows(session, model, cycle_id):
    if hasattr(model,"cycle_id"):
        session.execute(delete(model).where(model.cycle_id==cycle_id))

def import_canonical(session, *, base_type: str, df: pd.DataFrame, cycle: Cycle, replace: bool=True) -> dict:
    spec=get_base_spec(base_type); count=0; skipped=0; warnings=[]
    if base_type=="SIGA_BENEFICIARIOS":
        if replace: _delete_cycle_rows(session,Benefit,cycle.id)
        for _,r in df.iterrows():
            st=_get_or_create_student(session,r.get("GRR"),r.get("NOME"),curso=_str(r.get("CURSO")),codigo_curso=_str(r.get("CODIGO_CURSO")),curriculo=_str(r.get("CURRICULO")),campus=_str(r.get("CAMPUS")),ingresso=_str(r.get("INGRESSO")))
            if not st: skipped+=1; continue
            aux=_split_multi(r.get("AUXILIOS")) or ["PAE"]
            for a in aux: session.add(Benefit(student_id=st.id,cycle_id=cycle.id,modalidade=a,status=_str(r.get("STATUS_BENEFICIO")) or "ATIVO"))
            # proteção pré-análise estruturada disponível no SIGA
            prot_cols=["DEFICIENCIA_ACESSIBILIDADE","PARENTALIDADE_CUIDADO","REFUGIO_MIGRACAO","ACOLHIMENTO","POVOS_COMUNIDADES"]
            for f in prot_cols:
                val=r.get(f)
                if _bool(val) is True or (_str(val) and _str(val).lower() not in {"nao","não","0","false"}):
                    session.add(ProtectionFactor(student_id=st.id,cycle_id=cycle.id,fator=f,fonte="SIGA",status="IDENTIFICADO",data_registro=date.today(),status_atualidade="ATUAL",observacao=None,pre_analise=True))
            renda=_float(r.get("RENDA_PER_CAPITA"))
            if renda is not None:
                session.add(ProtectionFactor(student_id=st.id,cycle_id=cycle.id,fator="VULNERABILIDADE_SOCIOECONOMICA",fonte="SIGA",status="IDENTIFICADO",data_registro=date.today(),status_atualidade="ATUAL",observacao="Renda disponível na base institucional; utilizar conforme critérios PNAES, sem score no IAL.",pre_analise=True))
            count+=1
    elif base_type=="HISTORICO_ACADEMICO":
        # histórico é multi-ciclo; substitui somente períodos presentes no arquivo para estudantes do arquivo
        periods=set(_str(x) for x in df.get("PERIODO",pd.Series(dtype=str)).dropna().tolist())
        if replace and periods:
            student_ids=[]
            for g in df.get("GRR",[]):
                st=_get_or_create_student(session,g)
                if st: student_ids.append(st.id)
            if student_ids:
                session.execute(delete(AcademicHistory).where(AcademicHistory.student_id.in_(set(student_ids)),AcademicHistory.periodo.in_(periods)))
        for _,r in df.iterrows():
            st=_get_or_create_student(session,r.get("GRR"))
            if not st: skipped+=1; continue
            sit=(_str(r.get("SITUACAO")) or "").lower()
            aprovado=_bool(r.get("APROVADO")); repn=_bool(r.get("REP_NOTA")); repf=_bool(r.get("REP_FREQ")); canc=_bool(r.get("CANCELADO"))
            if aprovado is None and sit: aprovado="aprov" in sit
            if repn is None and sit: repn=("reprov" in sit and "freq" not in sit and "falta" not in sit)
            if repf is None and sit: repf=("freq" in sit or "falta" in sit) and "reprov" in sit
            if canc is None and sit: canc="cancel" in sit
            session.add(AcademicHistory(student_id=st.id,periodo=_str(r.get("PERIODO")) or cycle.codigo,disciplina_codigo=_str(r.get("DISCIPLINA_CODIGO")) or "PENDENTE",disciplina_nome=_str(r.get("DISCIPLINA_NOME")),turma=_str(r.get("TURMA")),ch=_float(r.get("CH")),obrigatoria=_bool(r.get("OBRIGATORIA")),situacao=_str(r.get("SITUACAO")),aprovado=aprovado,rep_nota=repn,rep_freq=repf,cancelado=canc,nota=_float(r.get("NOTA")),frequencia_pct=_float(r.get("FREQUENCIA_PCT"))))
            count+=1
    elif base_type=="PARAMETROS_CURRICULARES":
        if replace: session.execute(delete(CurriculumParameter))
        for _,r in df.iterrows():
            code=_str(r.get("CODIGO_CURSO"));
            if not code: skipped+=1;continue
            grade=_str(r.get("GRAU_EVIDENCIA")) or "D"
            grade=grade.strip().upper()[0] if grade else "D"
            session.add(CurriculumParameter(codigo_curso=code,curriculo=_str(r.get("CURRICULO")) or "NAO_INFORMADO",campus=_str(r.get("CAMPUS")),etapa=_str(r.get("ETAPA")),duracao_regular_periodos=_int(r.get("DURACAO_REGULAR_PERIODOS")),ch_total=_float(r.get("CH_TOTAL")),ch_minima_art18=_float(r.get("CH_MINIMA_ART18")),grau_evidencia=grade if grade in "ABCD" else "D",fonte=_str(r.get("FONTE"))))
            count+=1
    elif base_type=="DISCIPLINAS_OBRIGATORIAS":
        if replace: session.execute(delete(MandatoryDiscipline))
        for _,r in df.iterrows():
            code=_str(r.get("CODIGO_CURSO"));disc=_str(r.get("DISCIPLINA_CODIGO"))
            if not code or not disc: skipped+=1;continue
            session.add(MandatoryDiscipline(codigo_curso=code,curriculo=_str(r.get("CURRICULO")) or "NAO_INFORMADO",disciplina_codigo=disc,disciplina_nome=_str(r.get("DISCIPLINA_NOME")),etapa_recomendada=_str(r.get("ETAPA_RECOMENDADA"))))
            count+=1
    elif base_type=="TAXAS_APROVACAO_TURMAS":
        # substitui somente ciclo atual
        if replace: session.execute(delete(ClassApprovalRate).where(ClassApprovalRate.periodo==cycle.codigo))
        for _,r in df.iterrows():
            per=_str(r.get("PERIODO")) or cycle.codigo;disc=_str(r.get("DISCIPLINA_CODIGO"))
            if not disc:skipped+=1;continue
            taxa=_float(r.get("TAXA_APROVACAO_PCT"));mat=_int(r.get("MATRICULADOS"));apr=_int(r.get("APROVADOS"))
            if taxa is None and mat and apr is not None: taxa=100*apr/mat
            session.add(ClassApprovalRate(periodo=per,disciplina_codigo=disc,turma=_str(r.get("TURMA")),matriculados=mat,aprovados=apr,taxa_aprovacao_pct=taxa,fonte=_str(r.get("FONTE")),validada=_bool(r.get("VALIDADA")) is True))
            count+=1
    elif base_type=="INTEGRALIZACAO_TEMPO":
        if replace:_delete_cycle_rows(session,IntegrationTime,cycle.id)
        for _,r in df.iterrows():
            st=_get_or_create_student(session,r.get("GRR"))
            if not st:skipped+=1;continue
            session.add(IntegrationTime(student_id=st.id,cycle_id=cycle.id,ch_total=_float(r.get("CH_TOTAL")),ch_integralizada=_float(r.get("CH_INTEGRALIZADA")),periodos_vinculo=_int(r.get("PERIODOS_VINCULO")),periodos_computaveis=_int(r.get("PERIODOS_COMPUTAVEIS")),periodos_regulares=_int(r.get("PERIODOS_REGULARES")),mudanca_curso=_bool(r.get("MUDANCA_CURSO")) is True,retorno=_bool(r.get("RETORNO")) is True,trancamentos=_int(r.get("TRANCAMENTOS")),processo_academico=_str(r.get("PROCESSO_ACADEMICO")),poa_plano_estudos=_str(r.get("POA_PLANO_ESTUDOS"))))
            count+=1
    elif base_type.startswith("ACOMPANHAMENTO_"):
        fixed=spec.get("fixed_sector",base_type.replace("ACOMPANHAMENTO_",""))
        if replace: session.execute(delete(Accompaniment).where(Accompaniment.cycle_id==cycle.id,Accompaniment.setor.like(f"{fixed}%")))
        for _,r in df.iterrows():
            st=_get_or_create_student(session,r.get("GRR"))
            if not st:skipped+=1;continue
            setor=_str(r.get("SETOR")) or fixed
            session.add(Accompaniment(student_id=st.id,cycle_id=cycle.id,setor=setor,estado=_str(r.get("ESTADO")) or "ATIVO",data_ultimo_registro=_date(r.get("DATA_ULTIMO_REGISTRO")),fonte=_str(r.get("FONTE")) or base_type,objetivo_sintetico=_str(r.get("OBJETIVO_SINTETICO"))))
            for f in _split_multi(r.get("FATORES_PROTECAO")):
                session.add(ProtectionFactor(student_id=st.id,cycle_id=cycle.id,fator=f.upper().replace(" ","_"),fonte=fixed,status="IDENTIFICADO",data_registro=_date(r.get("DATA_ULTIMO_REGISTRO")) or date.today(),status_atualidade="ATUAL",pre_analise=True))
            count+=1
    elif base_type=="LEGADO_PLANILHA_COMPLETA":
        if replace:
            _delete_cycle_rows(session,LegacyAcademicSnapshot,cycle.id)
            session.execute(delete(ProtectionFactor).where(ProtectionFactor.cycle_id==cycle.id,ProtectionFactor.fonte=="SIGA_LEGADO"))
            session.execute(delete(Accompaniment).where(Accompaniment.cycle_id==cycle.id,Accompaniment.fonte=="PLANILHA_UNIFICADA_ITA_2025"))
            session.execute(delete(LegacyProcessEvent).where(LegacyProcessEvent.cycle_id==cycle.id))
        # A planilha da calculadora de 2025 é agregada por estudante. Ela alimenta um snapshot próprio,
        # preservando os valores originais sem reproduzir o antigo score ITA.
        for _,r in df.iterrows():
            st=_get_or_create_student(session,r.get("GRR"),r.get("NOME"),curso=_str(r.get("CURSO")),campus=_str(r.get("SETOR")),ingresso=_str(r.get("ANO_INGRESSO")))
            if not st: skipped+=1; continue
            # Garante presença no universo do ciclo. O tipo de auxílio permanece genérico quando a planilha legada não o informa.
            if not session.scalar(select(Benefit.id).where(Benefit.student_id==st.id,Benefit.cycle_id==cycle.id).limit(1)):
                session.add(Benefit(student_id=st.id,cycle_id=cycle.id,modalidade="PAE",status="ATIVO"))
            # Não transforma renda em score. Somente marcadores explícitos de PROAFE são convertidos
            # em fatores de proteção, preservando a informação original.
            proafe=_str(r.get("PROAFE"))
            for pf in extract_proafe_protection_factors(proafe):
                session.add(ProtectionFactor(student_id=st.id,cycle_id=cycle.id,fator=pf["factor"],fonte="SIGA_LEGADO",status="IDENTIFICADO",data_registro=date.today(),status_atualidade="REQUER_ATUALIZACAO",observacao=pf["observation"],pre_analise=True))
            snap=LegacyAcademicSnapshot(
                student_id=st.id,cycle_id=cycle.id,source_name="PLANILHA_COMPLETA_ITA_2025",setor=_str(r.get("SETOR")),curso=_str(r.get("CURSO")),
                proafe=proafe,motivo=_str(r.get("MOTIVO")),renda_per_capita=_float(r.get("RENDA_PER_CAPITA")),classe_renda=_str(r.get("CLASSE_RENDA")),
                nota_renda=_float(r.get("NOTA_RENDA")),ano_ingresso=_int(r.get("ANO_INGRESSO")),tempo_sem=_int(r.get("TEMPO_SEM")),
                ch_integralizada_pct=_float(r.get("CH_INTEGRALIZADA_PCT")),ch_ideal=_float(r.get("CH_IDEAL")),qtd_matriculada=_int(r.get("QTD_MATRICULADA")),
                qtd_rep_nota=_int(r.get("QTD_REP_NOTA")),qtd_rep_freq=_int(r.get("QTD_REP_FREQ")),qtd_cancelada=_int(r.get("QTD_CANCELADA")),ira_sem=_float(r.get("IRA_SEM")),
                aprovacao_pct=_float(r.get("APROVACAO_PCT")),ch_recomendada_sem=_float(r.get("CH_RECOMENDADA_SEM")),ch_mat_total=_float(r.get("CH_MAT_TOTAL")),
                baixa_mat=_str(r.get("BAIXA_MAT")),hist_rf_1=_float(r.get("HIST_RF_1")),hist_rf_2=_float(r.get("HIST_RF_2")),hist_rf_3=_float(r.get("HIST_RF_3")),
                hist_rf_media=_float(r.get("HIST_RF_MEDIA")),avaliacao_anterior=_bool(r.get("AVALIACAO_ANTERIOR")),avaliacao_2024=_str(r.get("AVALIACAO_2024")),
                recebeu_aux_anterior=_bool(r.get("RECEBEU_AUX_ANTERIOR")),legacy_ita=_float(r.get("LEGACY_ITA")),legacy_classificacao=_str(r.get("LEGACY_CLASSIFICACAO")),
                responsavel_anterior=_str(r.get("RESPONSAVEL_ANTERIOR")),raw_json=_str(r.get("RAW_JSON")))
            session.add(snap)
            # Snapshot de tempo: mantém apenas aquilo que a planilha realmente informa. Períodos computáveis não são inferidos.
            if replace:
                session.execute(delete(IntegrationTime).where(IntegrationTime.student_id==st.id,IntegrationTime.cycle_id==cycle.id))
            session.add(IntegrationTime(student_id=st.id,cycle_id=cycle.id,ch_total=None,ch_integralizada=None,periodos_vinculo=_int(r.get("TEMPO_SEM")),periodos_computaveis=None,periodos_regulares=None,mudanca_curso=False,retorno=False,trancamentos=None))
            # Histórico de avaliação: somente SIM/1 verdadeiro gera registro; 0 não é convertido em participação.
            if _bool(r.get("AVALIACAO_ANTERIOR")) is True:
                if not session.scalar(select(EvaluationHistory.id).where(EvaluationHistory.student_id==st.id,EvaluationHistory.ciclo_codigo=="CICLO_ANTERIOR_LEGADO").limit(1)):
                    session.add(EvaluationHistory(student_id=st.id,ciclo_codigo="CICLO_ANTERIOR_LEGADO",participou=True,profissional=_str(r.get("RESPONSAVEL_ANTERIOR")),resultado=_str(r.get("AVALIACAO_2024")) or "PARTICIPOU",fase="LEGADO",ial_anterior=None,mcn_resumo="Registro importado da planilha agregada; ITA legado não convertido em IAL."))

            # A planilha final utilizada em 2025 já incorporava blocos das equipes. Esses blocos
            # são importados como conhecimento institucional prévio, nunca como pontuação.
            raw_obj=parse_raw_json(_str(r.get("RAW_JSON")))
            for ac in extract_embedded_accompaniments(raw_obj):
                session.add(Accompaniment(student_id=st.id,cycle_id=cycle.id,setor=ac["sector"],estado=ac["state"],data_ultimo_registro=None,fonte="PLANILHA_UNIFICADA_ITA_2025",objetivo_sintetico=ac["summary"]))

            legacy_process=extract_legacy_process(raw_obj)
            if legacy_process:
                existing_legacy=session.scalar(select(LegacyProcessEvent).where(LegacyProcessEvent.student_id==st.id,LegacyProcessEvent.cycle_id==cycle.id))
                if existing_legacy:
                    session.delete(existing_legacy); session.flush()
                session.add(LegacyProcessEvent(student_id=st.id,cycle_id=cycle.id,source_name="PLANILHA_UNIFICADA_ITA_2025",raw_json=_str(r.get("RAW_JSON")),**legacy_process))
            count+=1
    elif base_type=="FORMULARIO_CONTEXTUALIZACAO":
        if replace: _delete_cycle_rows(session,Contextualization,cycle.id)
        factor_fields=["DEFICIENCIA_ACESSIBILIDADE","PARENTALIDADE_CUIDADO","REFUGIO_MIGRACAO","POVOS_COMUNIDADES","TRABALHO_SUBSISTENCIA","MORADIA","TRANSPORTE","SAUDE_REPERCUSSAO_ACADEMICA"]
        for _,r in df.iterrows():
            st=_get_or_create_student(session,r.get("GRR"))
            if not st: skipped+=1; continue
            session.add(Contextualization(student_id=st.id,cycle_id=cycle.id,tipo="CONTEXTUALIZACAO_INICIAL",status="RESPONDIDO",resposta_json=_str(r.get("RAW_JSON")),data_resposta=pd.to_datetime(_none(r.get("DATA_RESPOSTA")),errors="coerce").to_pydatetime() if _none(r.get("DATA_RESPOSTA")) is not None and not pd.isna(pd.to_datetime(_none(r.get("DATA_RESPOSTA")),errors="coerce")) else datetime.now(timezone.utc).replace(tzinfo=None)))
            for field in factor_fields:
                val=_str(r.get(field))
                if not val: continue
                # Só registra fator quando existe coluna estruturada explicitamente mapeada; não faz NLP sobre texto livre.
                if _bool(val) is True or val.lower() not in {"nao","não","0","false","nao se aplica","não se aplica"}:
                    session.add(ProtectionFactor(student_id=st.id,cycle_id=cycle.id,fator=field,fonte="FORMULARIO",status="AUTODECLARADO_CONTEXUALIZAR",data_registro=date.today(),status_atualidade="ATUALIZADO_FORMULARIO",observacao=None,pre_analise=False))
            count+=1
    elif base_type=="HISTORICO_AVALIACAO":
        # histórico pode conter diversos ciclos; não apaga por padrão todo histórico
        for _,r in df.iterrows():
            st=_get_or_create_student(session,r.get("GRR"))
            if not st:skipped+=1;continue
            cic=_str(r.get("CICLO_CODIGO")) or "ANTERIOR"
            if replace:
                session.execute(delete(EvaluationHistory).where(EvaluationHistory.student_id==st.id,EvaluationHistory.ciclo_codigo==cic))
            session.add(EvaluationHistory(student_id=st.id,ciclo_codigo=cic,participou=_bool(r.get("PARTICIPOU")) is not False,profissional=_str(r.get("PROFISSIONAL")),resultado=_str(r.get("RESULTADO")),fase=_str(r.get("FASE")),mna=_str(r.get("MNA")),piaap=_bool(r.get("PIAAP")) is True,acoes_pactuadas=_str(r.get("ACOES_PACTUADAS")),ial_anterior=_float(r.get("IAL_ANTERIOR")),mcn_resumo=_str(r.get("MCN_RESUMO"))))
            count+=1
    elif base_type=="LEGADO_ITA_2025":
        # preserva apenas histórico de participação/resultado, sem converter ITA em IAL
        for _,r in df.iterrows():
            st=_get_or_create_student(session,r.get("GRR"),curso=_str(r.get("CURSO")),campus=_str(r.get("SETOR")))
            if not st:skipped+=1;continue
            session.add(EvaluationHistory(student_id=st.id,ciclo_codigo="LEGADO_ITA_2025",participou=True,resultado="REGISTRO_LEGADO",fase="LEGADO",ial_anterior=None,mcn_resumo=f"ITA legado informado: {_str(r.get('ITA'))}; não convertido em IAL."))
            count+=1
    else:
        raise ValueError(f"Importador não implementado para {base_type}")
    session.flush()
    return {"imported":count,"skipped":skipped,"warnings":warnings}
