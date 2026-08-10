from __future__ import annotations
import os
import subprocess
import sys
from pathlib import Path


def test_blank_database_direct_page_pattern_creates_schema_and_cycles(tmp_path):
    """Regression: page 02 used to query Cycle before the schema existed."""
    db = tmp_path / "blank" / "pae.db"
    env = os.environ.copy()
    env["DATABASE_URL"] = f"sqlite:///{db}"
    code = r"""
from sqlalchemy import select
from src.db.session import session_scope
from src.models.models import Cycle
from src.services.bootstrap_service import ensure_default_cycles

# Exact operational pattern used by pages/02_dados.py.
with session_scope() as session:
    ensure_default_cycles(session)
    cycles = list(session.scalars(select(Cycle).order_by(Cycle.codigo)))
assert [c.codigo for c in cycles] == ['2025/2', '2026/1']
print('DIRECT_PAGE_BOOTSTRAP_OK')
"""
    proc = subprocess.run(
        [sys.executable, "-c", code],
        cwd=Path(__file__).resolve().parents[2],
        env=env,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert proc.returncode == 0, proc.stdout + "\n" + proc.stderr
    assert "DIRECT_PAGE_BOOTSTRAP_OK" in proc.stdout
    assert db.exists()
