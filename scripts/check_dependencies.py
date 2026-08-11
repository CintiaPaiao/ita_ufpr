from __future__ import annotations
from pathlib import Path
import ast, re, sys

ROOT=Path(__file__).resolve().parents[1]
req=(ROOT/'requirements.txt').read_text(encoding='utf-8').lower()
required={'sqlalchemy':'sqlalchemy','pandas':'pandas','numpy':'numpy','yaml':'pyyaml','plotly':'plotly','openpyxl':'openpyxl','streamlit':'streamlit'}
missing=[]
for mod,pkg in required.items():
    if not re.search(rf'(?mi)^\s*{re.escape(pkg)}(?:\[.*?\])?\s*(?:[<>=!~]|$)',req):
        missing.append(pkg)
if missing:
    print('Dependências ausentes em requirements.txt:', ', '.join(sorted(missing)))
    raise SystemExit(1)
print('Dependências essenciais declaradas em requirements.txt.')
