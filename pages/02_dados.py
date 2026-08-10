import streamlit as st, pandas as pd
from sqlalchemy import select
from src.ui.common import page_setup, safe_exception
from src.db.session import session_scope
from src.models.models import Cycle,ImportedFile
from src.config.base_registry import list_base_types,get_base_spec
from src.ingestion.readers import list_excel_sheets,choose_legacy_main_sheet
from src.services.import_service import preview_import,execute_import
from src.services.legacy_bundle_service import import_legacy_bundle
from src.services.base_status_service import base_status,required_ready
from src.services.processing_service import process_cycle
from src.services.freeze_service import freeze_current_cycle
from src.services.bootstrap_service import ensure_default_cycles

user=page_setup("Bases, Importação e Processamento do Ciclo – v0.4.2", allowed_roles=('ADMIN', 'CHEFIA'))
with session_scope() as s:
    ensure_default_cycles(s)
    cycles=list(s.scalars(select(Cycle).order_by(Cycle.codigo)))
if not cycles:
    st.error("Não foi possível criar ou localizar ciclos. Verifique a configuração de banco e configs/ciclos.yaml."); st.stop()
cycle_codes=[c.codigo for c in cycles]
cycle_code=st.selectbox("Ciclo de trabalho",cycle_codes,index=len(cycle_codes)-1)
cycle_obj=next(c for c in cycles if c.codigo==cycle_code)
if cycle_obj.status == "ENCERRADO":
    st.error("Este ciclo está ENCERRADO. Novas importações e processamento estão bloqueados.")
elif cycle_obj.frozen_at:
    st.warning(f"Ciclo congelado em {cycle_obj.frozen_at}. Novas importações estão bloqueadas.")

t0,t1,t2,t3,t4=st.tabs(["0. Pacote da Calculadora ITA 2025","1. Importar base individual","2. Status das bases","3. Processar ciclo","4. Histórico"])
with t0:
    st.subheader("Importação compatível com as bases reais da Calculadora ITA 2025")
    st.markdown("Carregue a mesma estrutura usada pela calculadora antiga: **Planilha rendimento/vulnerabilidade (PLANILHA COMPLETA)**, **planilha de atendimentos por equipe** e, opcionalmente, **formulário**. O sistema importa os dados, mas não reproduz o score ITA antigo.")
    main=st.file_uploader("1. Planilha rendimento/vulnerabilidade (obrigatória)",type=["xlsx","xls"],key="legacy_main")
    criteria=st.file_uploader("2. Planilha de atendimentos – Serviço Social/Psicologia/Pedagogia (opcional)",type=["xlsx","xls"],key="legacy_criteria")
    form=st.file_uploader("3. Planilha do formulário de estudantes (opcional)",type=["xlsx","xls","csv"],key="legacy_form")
    if main:
        raw=main.getvalue(); chosen=choose_legacy_main_sheet(main.name,raw)
        st.info(f"Aba principal detectada: {chosen}")
        try:
            _,can,val=preview_import(filename=main.name,raw=raw,base_type="LEGADO_PLANILHA_COMPLETA",sheet_name=chosen)
            c1,c2,c3=st.columns(3); c1.metric("Linhas",val.row_count); c2.metric("GRRs",val.unique_grr or 0); c3.metric("Campos reconhecidos",len(val.mapping))
            for w in val.warnings: st.warning(w)
            for e in val.errors: st.error(e)
            st.dataframe(pd.DataFrame([{"campo":k,"coluna encontrada":v} for k,v in val.mapping.items()]),use_container_width=True,hide_index=True)
            st.dataframe(can.head(30),use_container_width=True,hide_index=True)
            replace=st.checkbox("Substituir dados importados anteriormente para este ciclo",True,key="legacy_replace")
            if st.button("IMPORTAR PACOTE ITA 2025 → MODELO PAE",type="primary",disabled=not val.valid or cycle_obj.frozen_at is not None or cycle_obj.status == "ENCERRADO"):
                with session_scope() as s:
                    out=import_legacy_bundle(s,main_filename=main.name,main_raw=main.getvalue(),criteria_filename=criteria.name if criteria else None,criteria_raw=criteria.getvalue() if criteria else None,form_filename=form.name if form else None,form_raw=form.getvalue() if form else None,cycle_code=cycle_code,username=user["username"],replace=replace)
                st.success(f"Planilha principal importada: {out['main']['imported']} estudantes.")
                if out['criteria']: st.success(f"Acompanhamentos importados: {out['criteria']['imported']} registros em {len(out['criteria']['details'])} abas.")
                if out['form']: st.success(f"Contextualizações importadas: {out['form']['imported']} respostas.")
        except Exception as e: safe_exception(e)
with t1:
    options=dict(list_base_types()); base_type=st.selectbox("Tipo da base",list(options),format_func=lambda x:options[x])
    spec=get_base_spec(base_type); st.caption(f"Granularidade: {spec.get('grain','conforme dicionário')} • {'OBRIGATÓRIA' if spec.get('required') else 'opcional'}")
    uploaded=st.file_uploader("Selecione XLSX, XLS ou CSV",type=["xlsx","xls","csv"],key="operational_upload")
    if uploaded:
        raw=uploaded.getvalue(); sheets=list_excel_sheets(uploaded.name,raw); sheet=st.selectbox("Aba",sheets) if sheets else 0
        try:
            raw_df,canonical,val=preview_import(filename=uploaded.name,raw=raw,base_type=base_type,sheet_name=sheet)
            c1,c2,c3=st.columns(3);c1.metric("Linhas",val.row_count);c2.metric("GRRs únicos",val.unique_grr or 0);c3.metric("Campos reconhecidos",len(val.mapping))
            for e in val.errors:st.error(e)
            for x in val.warnings:st.warning(x)
            st.dataframe(pd.DataFrame([{"campo padrão":k,"coluna encontrada":v} for k,v in val.mapping.items()]),use_container_width=True,hide_index=True)
            st.dataframe(canonical.head(100),use_container_width=True,hide_index=True)
            replace=st.checkbox("Substituir a versão anterior desta base",value=True)
            if st.button("VALIDAR E REGISTRAR BASE",type="primary",disabled=(not val.valid or cycle_obj.frozen_at is not None or cycle_obj.status == "ENCERRADO")):
                with session_scope() as s: validation,result,reg=execute_import(s,filename=uploaded.name,raw=raw,base_type=base_type,cycle_code=cycle_code,username=user["username"],sheet_name=sheet,replace=replace)
                st.success(f"Base registrada: {result['imported']} registros; {result['skipped']} ignorados.")
        except Exception as e:safe_exception(e)
with t2:
    with session_scope() as s: status=base_status(s,cycle_code);ready,missing=required_ready(s,cycle_code)
    st.dataframe(pd.DataFrame(status),use_container_width=True,hide_index=True)
    st.info("Na v0.3, a PLANILHA COMPLETA da calculadora antiga pode substituir temporariamente SIGA + histórico detalhado + integralização para o processamento compatível. Arts. 17/20/21 permanecem protegidos quando faltam evidências detalhadas.")
    if ready:st.success("Todas as bases obrigatórias formais estão registradas.")
    else:st.warning("Bases formais pendentes: "+", ".join(missing))
with t3:
    st.markdown("O processamento gera/regera **MCN, IAL e priorização preliminar**, utilizando dados detalhados quando existirem e fallback seguro para a PLANILHA COMPLETA legada.")
    n=st.number_input("Quantidade N para priorização preliminar",min_value=1,max_value=10000,value=300,step=10)
    allow=st.checkbox("Permitir homologação com outras bases pendentes",False)
    if st.button("PROCESSAR CICLO",type="primary",disabled=cycle_obj.status == "ENCERRADO"):
        try:
            with session_scope() as s:result=process_cycle(s,cycle_code=cycle_code,username=user["username"],n_cases=int(n),allow_incomplete=allow)
            st.success(f"Processamento concluído: {result['universo']} estudantes; {result['priorizados']} pré-priorizados.")
            if result.get('legacy_mode'): st.info("Modo de compatibilidade com PLANILHA COMPLETA ITA 2025 utilizado. Resultados sem evidência detalhada foram marcados para conferência, não inventados.")
            if result['missing_bases']:st.warning("Pendências efetivas: "+", ".join(result['missing_bases']))
        except Exception as e:safe_exception(e)
    st.divider(); st.subheader("Congelamento")
    confirm=st.checkbox("Confirmo conferência das bases e resultados.")
    if st.button("CONGELAR CICLO",disabled=not confirm or cycle_obj.frozen_at is not None or cycle_obj.status == "ENCERRADO"):
        try:
            with session_scope() as s:freeze_current_cycle(s,cycle_code,user["username"])
            st.success("Ciclo congelado.")
        except Exception as e:safe_exception(e)
with t4:
    with session_scope() as s: rows=list(s.scalars(select(ImportedFile).where(ImportedFile.cycle_code==cycle_code).order_by(ImportedFile.imported_at.desc())))
    data=[{c.name:getattr(x,c.name) for c in x.__table__.columns} for x in rows]
    st.dataframe(pd.DataFrame(data),use_container_width=True,hide_index=True)
