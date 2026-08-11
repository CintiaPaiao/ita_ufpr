"""Teste de regressão para o erro observado no Streamlit Cloud.

Usa um stub de streamlit porque a suíte de CI pode testar importabilidade sem
subir a interface gráfica.
"""
import importlib
import sys
import types


def test_src_ui_exports_setup_and_next_action(monkeypatch):
    stub = types.ModuleType("streamlit")
    # As funções não são executadas neste teste; basta o módulo existir.
    monkeypatch.setitem(sys.modules, "streamlit", stub)
    for name in ["src.ui.helpers", "src.ui"]:
        sys.modules.pop(name, None)
    mod = importlib.import_module("src.ui")
    assert callable(mod.setup)
    assert callable(mod.next_action)


def test_explicit_helpers_import(monkeypatch):
    stub = types.ModuleType("streamlit")
    monkeypatch.setitem(sys.modules, "streamlit", stub)
    sys.modules.pop("src.ui.helpers", None)
    mod = importlib.import_module("src.ui.helpers")
    assert callable(mod.setup)
    assert callable(mod.next_action)
