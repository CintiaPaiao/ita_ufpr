from __future__ import annotations
from dataclasses import dataclass, field
import pandas as pd
from src.config.base_registry import get_base_spec
from src.ingestion.legacy_ita_profile import profile_workbook_columns

@dataclass
class ImportValidation:
    valid: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    mapping: dict[str,str] = field(default_factory=dict)
    row_count: int = 0
    unique_grr: int | None = None


def _norm(s: str) -> str:
    import unicodedata, re
    s=unicodedata.normalize("NFKD",str(s)).encode("ascii","ignore").decode().lower().strip()
    return re.sub(r"[^a-z0-9]+","",s)


def resolve_mapping(columns, aliases: dict) -> dict[str,str]:
    normalized={_norm(c):c for c in columns}
    out={}
    for canonical, opts in (aliases or {}).items():
        for opt in opts:
            key=_norm(opt)
            if key in normalized:
                out[canonical]=normalized[key]
                break
    return out


def validate_import(df: pd.DataFrame, base_type: str) -> ImportValidation:
    spec=get_base_spec(base_type)
    mapping=resolve_mapping(df.columns, spec.get("aliases",{}))
    errors=[]; warnings=[]
    normalized_cols={_norm(c) for c in df.columns}
    for alternatives in spec.get("required_any",[]):
        if not any(_norm(a) in normalized_cols for a in alternatives):
            errors.append("Ausência de coluna obrigatória compatível com: "+" / ".join(alternatives))
    if df.empty:
        errors.append("A planilha não possui registros.")
    unique_grr=None
    if "GRR" in mapping:
        series=df[mapping["GRR"]]
        unique_grr=int(series.dropna().astype(str).nunique())
        if series.isna().any(): warnings.append("Existem linhas com GRR ausente; elas não serão importadas em tabelas por estudante.")
    if base_type=="LEGADO_PLANILHA_COMPLETA":
        if "QTD_REP_FREQ" not in mapping:
            warnings.append("Quantidade de reprovações por frequência não reconhecida. Art. 19 e componente F poderão ficar pendentes.")
        if "APROVACAO_PCT" not in mapping:
            warnings.append("Percentual de aprovação não reconhecido. Rendimento/IAL poderão ficar pendentes.")
        profile=profile_workbook_columns(list(df.columns))
        if profile["looks_like_ita_2025_unified"]:
            warnings.append(f"Perfil ITA 2025 reconhecido: cobertura nuclear {profile['core_coverage']:.0%}; {profile['embedded_service_blocks']} blocos multiprofissionais detectados.")
        warnings.append("A planilha legada é agregada por estudante. Arts. 17 e 20 podem exigir bases complementares ou conferência profissional.")
    return ImportValidation(not errors,errors,warnings,mapping,len(df),unique_grr)


def canonicalize(df: pd.DataFrame, base_type: str, mapping: dict[str,str]|None=None, preserve_raw: bool=False) -> pd.DataFrame:
    spec=get_base_spec(base_type)
    mapping=mapping or resolve_mapping(df.columns,spec.get("aliases",{}))
    out=pd.DataFrame(index=df.index)
    for canonical, source in mapping.items():
        out[canonical]=df[source]
    if preserve_raw:
        import json
        out["RAW_JSON"]=[json.dumps({str(k): (None if pd.isna(v) else v) for k,v in row.items()},ensure_ascii=False,default=str) for row in df.to_dict("records")]
    return out
