"""API pública dos componentes de interface.

Mantém compatibilidade com ``from src.ui import setup, next_action`` e também
permite imports explícitos de ``src.ui.helpers``.
"""
from .helpers import next_action, setup

__all__ = ["setup", "next_action"]
