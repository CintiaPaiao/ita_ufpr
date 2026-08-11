from __future__ import annotations

from copy import deepcopy
from pathlib import Path
import shutil
import yaml

from src.config.settings import ROOT, IAL_CONFIG, MCN_CONFIG, PRIORITY_CONFIG, FEATURE_FLAGS, load_yaml


def _dump_yaml(name: str, data: dict) -> None:
    path = ROOT / 'configs' / name
    backup = path.with_suffix(path.suffix + '.bak')
    if path.exists():
        shutil.copy2(path, backup)
    path.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding='utf-8')


def current_configuration() -> dict:
    return {
        'ial': deepcopy(load_yaml('ial.yaml')),
        'mcn': deepcopy(load_yaml('mcn.yaml')),
        'priorizacao': deepcopy(load_yaml('priorizacao.yaml')),
        'features': deepcopy(load_yaml('feature_flags.yaml')),
        'servidores': deepcopy(load_yaml('servidores.yaml')),
        'fatores_protecao': deepcopy(load_yaml('fatores_protecao.yaml')),
        'app': deepcopy(load_yaml('app.yaml')),
    }


def validate_configuration(cfg: dict) -> list[str]:
    errors: list[str] = []
    weights = cfg['ial'].get('weights', {})
    vals = [float(weights.get(k, 0)) for k in ('rendimento','frequencia','progressao')]
    if abs(sum(vals) - 100.0) > 1e-6:
        errors.append('Os pesos do IAL devem somar 100.')
    if any(v < 0 or v > 100 for v in vals):
        errors.append('Cada peso do IAL deve estar entre 0 e 100.')
    partial = float(cfg['ial'].get('coverage', {}).get('partial_minimum', 60))
    complete = float(cfg['ial'].get('coverage', {}).get('complete', 100))
    if not (0 <= partial <= complete <= 100):
        errors.append('Cobertura do IAL inválida: esperado 0 ≤ parcial ≤ completa ≤ 100.')
    bands = cfg['ial'].get('bands', [])
    if not bands:
        errors.append('Ao menos uma faixa do IAL deve existir.')
    else:
        ordered = sorted(bands, key=lambda x: float(x['min']))
        if float(ordered[0]['min']) != 0 or float(ordered[-1]['max']) != 100:
            errors.append('As faixas do IAL devem cobrir de 0 a 100.')
        for a,b in zip(ordered, ordered[1:]):
            if float(a['max']) >= float(b['min']):
                errors.append('As faixas do IAL não podem se sobrepor.')
                break
    art20 = float(cfg['mcn'].get('art20', {}).get('minimum_student_approval_pct', 50))
    if not 0 <= art20 <= 100:
        errors.append('Percentual mínimo do art. 20 deve ficar entre 0 e 100.')
    n = int(cfg['priorizacao'].get('selection', {}).get('n_cases', 300))
    prof = int(cfg['priorizacao'].get('selection', {}).get('n_professionals', 5))
    if n <= 0 or prof <= 0:
        errors.append('N de casos e número de profissionais devem ser positivos.')
    return errors


def save_configuration(cfg: dict) -> None:
    errors = validate_configuration(cfg)
    if errors:
        raise ValueError(' | '.join(errors))
    _dump_yaml('ial.yaml', cfg['ial'])
    _dump_yaml('mcn.yaml', cfg['mcn'])
    _dump_yaml('priorizacao.yaml', cfg['priorizacao'])
    _dump_yaml('feature_flags.yaml', cfg['features'])
    _dump_yaml('servidores.yaml', cfg['servidores'])
    _dump_yaml('fatores_protecao.yaml', cfg['fatores_protecao'])

    # Atualiza os objetos importados pelos módulos de domínio no processo atual.
    IAL_CONFIG.clear(); IAL_CONFIG.update(deepcopy(cfg['ial']))
    MCN_CONFIG.clear(); MCN_CONFIG.update(deepcopy(cfg['mcn']))
    PRIORITY_CONFIG.clear(); PRIORITY_CONFIG.update(deepcopy(cfg['priorizacao']))
    FEATURE_FLAGS.clear(); FEATURE_FLAGS.update(deepcopy(cfg['features'].get('features', {})))
