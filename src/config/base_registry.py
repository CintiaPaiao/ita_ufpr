from __future__ import annotations
from src.config.settings import load_yaml

BASES = load_yaml("bases.yaml").get("base_types", {})

def get_base_spec(base_type: str) -> dict:
    if base_type not in BASES:
        raise KeyError(f"Tipo de base não cadastrado: {base_type}")
    return BASES[base_type]

def list_base_types() -> list[tuple[str,str]]:
    return [(k, v.get("label", k)) for k,v in BASES.items()]
