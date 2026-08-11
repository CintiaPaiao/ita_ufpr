from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]

def test_sqlalchemy_is_declared():
    req=(ROOT/'requirements.txt').read_text(encoding='utf-8').lower()
    assert 'sqlalchemy' in req

def test_import_journey_preserved():
    page=(ROOT/'pages'/'02_dados.py').read_text(encoding='utf-8')
    for token in ['Pacote da Calculadora ITA 2025','Importar base individual','Status das bases','Processar ciclo','Histórico','VALIDAR E REGISTRAR BASE','IMPORTAR PACOTE ITA 2025']:
        assert token in page

def test_new_ux_pages_exist():
    assert (ROOT/'pages'/'00_jornada_ciclo.py').exists()
    assert (ROOT/'pages'/'00a_central_configuracoes.py').exists()

def test_deprecated_use_container_width_removed():
    bad=[]
    deprecated='use_'+'container_'+'width'
    for p in ROOT.rglob('*.py'):
        if p == Path(__file__):
            continue
        if deprecated in p.read_text(encoding='utf-8'):
            bad.append(str(p.relative_to(ROOT)))
    assert not bad, bad
