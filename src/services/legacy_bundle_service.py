from __future__ import annotations
from io import BytesIO
from datetime import date
import json, re
import pandas as pd
from sqlalchemy import select, delete
from src.ingestion.readers import choose_legacy_main_sheet, list_excel_sheets, normalize_sector_from_sheet
from src.services.import_service import execute_import
from src.models.models import Cycle, Student, Accompaniment, ProtectionFactor, Contextualization, Benefit, LegacyAcademicSnapshot
from src.validation.normalization import padronizar_grr, validar_grr
from src.logging.audit import log_action
from src.ingestion.file_registry import register_import


def _norm(s):
    import unicodedata
    s=unicodedata.normalize("NFKD",str(s)).encode("ascii","ignore").decode().lower().strip()
    return re.sub(r"[^a-z0-9]+","",s)


def _find_col(df, candidates):
    idx={_norm(c):c for c in df.columns}
    for c in candidates:
        if _norm(c) in idx: return idx[_norm(c)]
    return None


def _get_student(session, grr):
    g=padronizar_grr(grr)
    if not validar_grr(g): return None
    return session.scalar(select(Student).where(Student.grr==g))


def _status_from_raw(value):
    if value is None or (isinstance(value,float) and pd.isna(value)): return "REGISTRO_IDENTIFICADO"
    s=str(value).strip().lower()
    if not s: return "REGISTRO_IDENTIFICADO"
    if s in {"sim","s","1","ativo","em acompanhamento"}: return "ATIVO"
    if s in {"não","nao","n","0"}: return "REGISTRO_IDENTIFICADO"
    return "REGISTRO_IDENTIFICADO"


def import_criteria_workbook(session, *, filename:str, raw:bytes, cycle_code:str, username:str, replace:bool=True):
    cycle=session.scalar(select(Cycle).where(Cycle.codigo==cycle_code))
    if not cycle: raise ValueError("Ciclo não cadastrado")
    if cycle.frozen_at is not None: raise ValueError("Ciclo congelado")
    sheets=list_excel_sheets(filename,raw)
    imported=0; details=[]
    for sheet in sheets:
        df=pd.read_excel(BytesIO(raw),sheet_name=sheet)
        grr_col=_find_col(df,["GRR","grr","MATRICULA"])
        if not grr_col: continue
        sector=normalize_sector_from_sheet(sheet)
        if replace:
            session.execute(delete(Accompaniment).where(Accompaniment.cycle_id==cycle.id,Accompaniment.setor==sector))
        status_col=_find_col(df,["A/O ESTUDANTE ATENDE AOS CRITÉRIOS? (Sim ou Não)","ATENDE AOS CRITÉRIOS?","ATENDE AOS CRITERIOS?","status","ACOMPANHAMENTO"])
        obs_col=_find_col(df,["Observações","Observacoes","observação","sintese","síntese"])
        ref_col=_find_col(df,["Servidor de  Referência","Servidor de Referência","responsável","responsavel"])
        date_col=_find_col(df,["Data","data atendimento","DATA_ULTIMO_REGISTRO"])
        sheet_count=0
        for _,row in df.iterrows():
            st=_get_student(session,row.get(grr_col))
            if not st: continue
            raw_status=row.get(status_col) if status_col else None
            obs=None if not obs_col or pd.isna(row.get(obs_col)) else str(row.get(obs_col)).strip()
            ref=None if not ref_col or pd.isna(row.get(ref_col)) else str(row.get(ref_col)).strip()
            dt=None
            if date_col and not pd.isna(row.get(date_col)):
                try: dt=pd.to_datetime(row.get(date_col)).date()
                except Exception: dt=None
            objective=" | ".join(x for x in [f"Status original: {raw_status}" if raw_status is not None and not pd.isna(raw_status) else None, f"Referência: {ref}" if ref else None, obs] if x)
            session.add(Accompaniment(student_id=st.id,cycle_id=cycle.id,setor=sector,estado=_status_from_raw(raw_status),data_ultimo_registro=dt,fonte=f"{filename}::{sheet}",objetivo_sintetico=objective or None))
            sheet_count+=1; imported+=1
        details.append({"sheet":sheet,"sector":sector,"rows":sheet_count})
    reg=register_import(session,filename=filename,source="LEGADO_CRITERIOS_ITA_2025",raw=raw,username=username,cycle_code=cycle_code,row_count=imported,unique_grr=None,schema_name="WORKBOOK_CRITERIOS_LEGADO",validation_status="VALIDADO_E_IMPORTADO")
    log_action(session,username=username,action="IMPORTAR_PACOTE_CRITERIOS_LEGADO",entity="arquivo_importado",entity_id=reg.id,cycle_code=cycle_code,new_value=details,reason="Compatibilidade com planilhas da Calculadora ITA 2025")
    return {"imported":imported,"details":details,"record_id":reg.id}


def import_legacy_bundle(session, *, main_filename:str, main_raw:bytes, cycle_code:str, username:str,
                         criteria_filename:str|None=None, criteria_raw:bytes|None=None,
                         form_filename:str|None=None, form_raw:bytes|None=None, replace:bool=True):
    main_sheet=choose_legacy_main_sheet(main_filename,main_raw)
    v,res,reg=execute_import(session,filename=main_filename,raw=main_raw,base_type="LEGADO_PLANILHA_COMPLETA",cycle_code=cycle_code,username=username,sheet_name=main_sheet,replace=replace)
    out={"main":{"sheet":main_sheet,"imported":res["imported"],"record_id":reg.id},"criteria":None,"form":None}
    if criteria_raw and criteria_filename:
        out["criteria"]=import_criteria_workbook(session,filename=criteria_filename,raw=criteria_raw,cycle_code=cycle_code,username=username,replace=replace)
    if form_raw and form_filename:
        sheets=list_excel_sheets(form_filename,form_raw)
        form_sheet="Sheet1" if "Sheet1" in sheets else (sheets[0] if sheets else 0)
        v2,res2,reg2=execute_import(session,filename=form_filename,raw=form_raw,base_type="FORMULARIO_CONTEXTUALIZACAO",cycle_code=cycle_code,username=username,sheet_name=form_sheet,replace=replace)
        out["form"]={"sheet":form_sheet,"imported":res2["imported"],"record_id":reg2.id}
    return out
