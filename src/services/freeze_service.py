from __future__ import annotations
from sqlalchemy import select
from src.models.models import Cycle,ImportedFile
from src.services.base_status_service import required_ready
from src.services.cycle_service import freeze_cycle
from src.config.settings import IAL_CONFIG,MCN_CONFIG

def freeze_current_cycle(session,cycle_code: str,responsavel: str,code_version="0.3.0"):
    cycle=session.scalar(select(Cycle).where(Cycle.codigo==cycle_code))
    if not cycle:raise ValueError("Ciclo não cadastrado")
    ready,missing=required_ready(session,cycle_code)
    if not ready:raise ValueError("Não é possível congelar: bases obrigatórias pendentes: "+", ".join(missing))
    files=list(session.scalars(select(ImportedFile).where(ImportedFile.cycle_code==cycle_code)))
    hashes=";".join(sorted({f"{f.source}:{f.sha256}" for f in files}))
    return freeze_cycle(cycle,hashes_bases=hashes,responsavel=responsavel,code_version=code_version,mcn_version=MCN_CONFIG.get("version","MCN"),ial_version=IAL_CONFIG.get("version","IAL"),config_version="0.3.0")
