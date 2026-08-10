from __future__ import annotations

from datetime import datetime, timezone
from src.models.models import Cycle


def _utcnow_naive() -> datetime:
    """Retorna horário UTC sem tzinfo, compatível com a coluna DateTime atual do modelo."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


def freeze_cycle(
    cycle: Cycle,
    *,
    hashes_bases: str,
    responsavel: str,
    code_version: str,
    mcn_version: str,
    ial_version: str,
    config_version: str,
) -> Cycle:
    """Congela a versão documental/técnica do ciclo após validação das bases.

    Esta função apenas atualiza o objeto ``Cycle`` recebido. A transação é
    controlada pelo serviço chamador/session scope, preservando atomicidade.
    """
    cycle.status = "DADOS_VALIDADOS"
    cycle.frozen_at = _utcnow_naive()
    cycle.hashes_bases = hashes_bases
    cycle.responsavel = responsavel
    cycle.code_version = code_version
    cycle.mcn_version = mcn_version
    cycle.ial_version = ial_version
    cycle.config_version = config_version
    return cycle
