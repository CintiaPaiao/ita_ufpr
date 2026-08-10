from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import sys,os
mods=['streamlit','pandas','numpy','sqlalchemy','yaml','plotly','openpyxl','xlsxwriter','pytest'];bad=[]
for m in mods:
    try:__import__(m)
    except Exception as e:bad.append((m,str(e)))
print('Python:',sys.version);print('DATABASE_URL:',os.getenv('DATABASE_URL','sqlite:///database/pae.db'))
if bad:print('Dependências ausentes:',bad);raise SystemExit(1)
print('Ambiente validado.')
