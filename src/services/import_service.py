from __future__ import annotations
from sqlalchemy import select
from src.ingestion.readers import read_uploaded_bytes
from src.schemas.import_contracts import validate_import, canonicalize
from src.ingestion.file_registry import register_import
from src.ingestion.persistence import import_canonical
from src.models.models import Cycle
from src.logging.audit import log_action


def preview_import(*, filename: str, raw: bytes, base_type: str, sheet_name=0):
    df=read_uploaded_bytes(filename,raw,sheet_name=sheet_name)
    validation=validate_import(df,base_type)
    canonical=canonicalize(df,base_type,validation.mapping,preserve_raw=base_type in {"LEGADO_PLANILHA_COMPLETA","FORMULARIO_CONTEXTUALIZACAO"})
    return df,canonical,validation


def execute_import(session, *, filename: str, raw: bytes, base_type: str, cycle_code: str,
                   username: str, sheet_name=0, replace: bool=True):
    cycle=session.scalar(select(Cycle).where(Cycle.codigo==cycle_code))
    if not cycle: raise ValueError(f"Ciclo não cadastrado: {cycle_code}")
    if cycle.frozen_at is not None:
        raise ValueError("O ciclo está congelado. Crie nova versão/reative o ciclo antes de alterar bases.")
    raw_df,canonical,validation=preview_import(filename=filename,raw=raw,base_type=base_type,sheet_name=sheet_name)
    if not validation.valid:
        raise ValueError("Base inválida: "+"; ".join(validation.errors))
    result=import_canonical(session,base_type=base_type,df=canonical,cycle=cycle,replace=replace)
    reg=register_import(session,filename=filename,source=base_type,raw=raw,username=username,cycle_code=cycle_code,
                        row_count=validation.row_count,unique_grr=validation.unique_grr,schema_name=base_type,validation_status="VALIDADO_E_IMPORTADO")
    log_action(session,username=username,action="IMPORTAR_BASE",entity="arquivo_importado",entity_id=reg.id,cycle_code=cycle_code,new_value={"base_type":base_type,**result},reason="Importação validada pela interface")
    return validation,result,reg
