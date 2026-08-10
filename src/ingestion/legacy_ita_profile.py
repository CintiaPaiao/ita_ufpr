from __future__ import annotations

import json
import math
import re
import unicodedata
from dataclasses import dataclass
from typing import Any


def _clean(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, float) and math.isnan(value):
        return None
    s = str(value).strip()
    if not s or s.lower() in {"nan", "none"}:
        return None
    return s


def _norm(value: Any) -> str:
    s = unicodedata.normalize("NFKD", str(value)).encode("ascii", "ignore").decode().lower().strip()
    return re.sub(r"[^a-z0-9]+", "", s)


def parse_raw_json(raw_json: str | None) -> dict[str, Any]:
    if not raw_json:
        return {}
    try:
        value = json.loads(raw_json)
        return value if isinstance(value, dict) else {}
    except Exception:
        return {}


def _find(raw: dict[str, Any], *candidates: str) -> Any:
    # Primeiro respeita o cabeçalho exato. Isso é indispensável no template ITA 2025,
    # que possui colunas cuja única diferença é espaço/sufixo gerado pelo Excel/Pandas.
    for candidate in candidates:
        if candidate in raw:
            return raw.get(candidate)
    # Só depois usa comparação normalizada, escolhendo a primeira ocorrência do workbook
    # para evitar que chaves semanticamente distintas se sobrescrevam silenciosamente.
    normalized = {}
    for key in raw:
        normalized.setdefault(_norm(key), key)
    for candidate in candidates:
        key = normalized.get(_norm(candidate))
        if key is not None:
            return raw.get(key)
    return None


@dataclass(frozen=True)
class EmbeddedServiceSpec:
    sector: str
    status_candidates: tuple[str, ...]
    observation_candidates: tuple[str, ...]
    reference_candidates: tuple[str, ...]


EMBEDDED_SERVICES = (
    EmbeddedServiceSpec(
        "SERVICO_SOCIAL_P4E",
        ("ATENDE AOS CRITÉRIOS?",),
        ("Observações",),
        ("Servidor de Referência", "Servidor de  Referência"),
    ),
    EmbeddedServiceSpec(
        "PSICOLOGIA_P4E",
        (" ATENDE AOS CRITÉRIOS?",),
        ("Observações.1",),
        ("Servidor de Referência.1", "Servidor de  Referência.1"),
    ),
    EmbeddedServiceSpec(
        "PEDAGOGIA_P4E",
        ("ATENDE AOS CRITÉRIOS? ",),
        ("Observações.2",),
        ("Servidor de Referência.2", "Servidor de  Referência.2"),
    ),
    EmbeddedServiceSpec(
        "CAISE_P4E",
        ("ATENDE AOS CRITÉRIOS? .1",),
        ("Observações.3",),
        ("Servidor de Referência_Coord Ac",),
    ),
    EmbeddedServiceSpec(
        "CPPOVOS_PROAFE",
        ("ATENDE AOS CRITÉRIOS? (Sim ou Não)_CPPovos", "ATENDE AOS CRITÉRIOS? (Sim\xa0ou\xa0Não)_CPPovos"),
        ("Observações CPPovos",),
        ("Servidor de Referência_CPPovos", "Servidor de  Referência_CPPovos"),
    ),
    EmbeddedServiceSpec(
        "CATRIM_ERI",
        ("ATENDE AOS CRITÉRIOS? CATRIM",),
        ("Observações CATRIM",),
        ("Servidor de Referência_CATRIM", "Servidor de  Referência_CATRIM"),
    ),
)


def extract_embedded_accompaniments(raw: dict[str, Any]) -> list[dict[str, str | None]]:
    """Extrai apenas registros efetivamente preenchidos no bloco multiprofissional legado.

    A resposta SIM/NÃO é preservada como informação original e NÃO é convertida em adesão,
    risco ou consequência. A existência de colunas constantes com o nome do serviço não cria
    acompanhamento por si só.
    """
    records: list[dict[str, str | None]] = []
    for spec in EMBEDDED_SERVICES:
        # Nos blocos multiprofissionais do workbook legado existem cabeçalhos quase idênticos.
        # Aqui usamos correspondência exata para impedir que a coluna de uma equipe seja atribuída a outra.
        status = _clean(next((raw[c] for c in spec.status_candidates if c in raw), None))
        observation = _clean(next((raw[c] for c in spec.observation_candidates if c in raw), None))
        reference = _clean(next((raw[c] for c in spec.reference_candidates if c in raw), None))
        if not any((status, observation, reference)):
            continue
        parts = []
        if status:
            parts.append(f"Resposta original no levantamento: {status}")
        if reference:
            parts.append(f"Profissional de referência: {reference}")
        if observation:
            parts.append(observation)
        records.append({
            "sector": spec.sector,
            "state": "REGISTRO_IDENTIFICADO",
            "reference": reference,
            "observation": observation,
            "raw_status": status,
            "summary": " | ".join(parts) if parts else None,
        })
    return records


def extract_proafe_protection_factors(raw_value: Any) -> list[dict[str, str]]:
    """Mapeia somente marcadores explícitos da coluna PROAFE da base legada.

    Não atribui peso, gravidade ou risco. O texto original é sempre preservado como observação.
    """
    raw = _clean(raw_value)
    if not raw or raw in {"-", "—"}:
        return []
    normalized = _norm(raw)
    factors: set[str] = set()
    if "refugi" in normalized or "migr" in normalized:
        factors.add("REFUGIO_MIGRACAO")
    if "indigena" in normalized or "quilomb" in normalized or "povos" in normalized:
        factors.add("POVOS_COMUNIDADES")
    accessibility_terms = (
        "tea", "deficiencia", "baixavisao", "cegueira", "auditiva", "fisica", "intelectual"
    )
    if any(term in normalized for term in accessibility_terms):
        factors.add("DEFICIENCIA_ACESSIBILIDADE")
    if not factors and "naoseenquadra" not in normalized:
        factors.add("PRIORIDADE_PROAFE_REGISTRADA")
    return [{"factor": f, "observation": raw} for f in sorted(factors)]


def extract_legacy_process(raw: dict[str, Any]) -> dict[str, str | None] | None:
    # Também aqui a correspondência é exata: `Observações.2` é o bloco da Pedagogia e
    # não pode ser confundido com `observações 2` do fluxo de parecer/recurso.
    def exact(*names: str):
        return _clean(next((raw[n] for n in names if n in raw), None))
    values = {
        "responsavel_2024": exact("responsavel 2024"),
        "responsavel_2025_1": exact("responsavel 2025/1"),
        "observacoes_1": exact("observações 1", "observacoes 1"),
        "parecer_1": exact("1º parecer", "1o parecer"),
        "situacao_1": exact("situação 1", "situacao 1"),
        "respondeu_recurso_final": exact("respondeu o recurso final?"),
        "observacoes_2": exact("observações 2", "observacoes 2"),
        "parecer_2": exact("2º parecer", "2o parecer"),
        "situacao_2": exact("situação 2", "situacao 2"),
    }
    return values if any(values.values()) else None


def profile_workbook_columns(columns: list[str]) -> dict[str, Any]:
    """Diagnóstico de compatibilidade com a planilha final/unificada do ITA 2025."""
    normalized = {_norm(c) for c in columns}
    core = ["GRR", "qtd-matriculada", "porcentagem-aprovacao", "qtd-rep-frequencia", "TEMPO UFPR - SEM"]
    found = {c: _norm(c) in normalized for c in core}
    service_hits = 0
    for spec in EMBEDDED_SERVICES:
        if any(_norm(c) in normalized for c in spec.status_candidates + spec.observation_candidates + spec.reference_candidates):
            service_hits += 1
    return {
        "core_fields": found,
        "core_coverage": sum(found.values()) / len(found),
        "embedded_service_blocks": service_hits,
        "looks_like_ita_2025_unified": found["GRR"] and sum(found.values()) >= 3,
    }
