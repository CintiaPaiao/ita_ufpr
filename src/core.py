from __future__ import annotations
import hashlib, json, sqlite3, datetime as dt
from pathlib import Path
from typing import Any
import pandas as pd
import yaml

ROOT=Path(__file__).resolve().parents[1]
DB=ROOT/'data'/'pae.db'
CFG=ROOT/'configs'/'settings.yaml'

DEFAULT={
 'app':{'version':'0.4.5.1','methodology_version':'2026-08','selection_n':300,'professionals':5},
 'ial':{'weights':{'rendimento':0.40,'frequencia':0.35,'progressao':0.25},'coverage_partial_min':0.60,
        'bands':[{'min':0,'max':19.9,'label':'Reduzida'},{'min':20,'max':34.9,'label':'Atenção'},{'min':35,'max':49.9,'label':'Relevante'},{'min':50,'max':64.9,'label':'Elevada'},{'min':65,'max':100,'label':'Intensiva'}]},
 'mcn':{'art20_min_approval':50,'art21_multiplier':1.5,'art19_limits':{'2':0,'4':1,'999':2}},
 'workflow':{'appeal_days':10,'monitoring_days':30},
 'features':{'art18_automatico':False,'art20_taxa_turma':False,'piaap':True,'crps':True,'comissao':True,'equity_audit':True},
 'ui':{'page_size':50,'show_help':True}
}

def load_config()->dict[str,Any]:
    if not CFG.exists(): save_config(DEFAULT)
    with open(CFG,encoding='utf-8') as f:return yaml.safe_load(f)

def save_config(cfg:dict[str,Any])->None:
    CFG.parent.mkdir(parents=True,exist_ok=True)
    with open(CFG,'w',encoding='utf-8') as f: yaml.safe_dump(cfg,f,allow_unicode=True,sort_keys=False)

def connect():
    DB.parent.mkdir(parents=True,exist_ok=True)
    c=sqlite3.connect(DB); c.row_factory=sqlite3.Row; return c

def init_db():
    con=connect(); cur=con.cursor()
    cur.executescript('''
    CREATE TABLE IF NOT EXISTS students(grr TEXT PRIMARY KEY,name TEXT,course TEXT,campus TEXT,curriculum TEXT);
    CREATE TABLE IF NOT EXISTS imports(id INTEGER PRIMARY KEY AUTOINCREMENT,cycle TEXT,filename TEXT,sha256 TEXT,rows_n INTEGER,grrs_n INTEGER,status TEXT,created_at TEXT);
    CREATE TABLE IF NOT EXISTS results(grr TEXT,cycle TEXT,art17 TEXT,art18 TEXT,art19 TEXT,art20 TEXT,art21 TEXT,ial REAL,coverage REAL,ial_band TEXT,priority_layer TEXT,selected INTEGER DEFAULT 0,professional TEXT,phase TEXT DEFAULT 'PRIMEIRA_ANALISE',PRIMARY KEY(grr,cycle));
    CREATE TABLE IF NOT EXISTS professional_records(id INTEGER PRIMARY KEY AUTOINCREMENT,grr TEXT,cycle TEXT,kind TEXT,status TEXT,summary TEXT,next_action TEXT,due_date TEXT,created_at TEXT);
    CREATE TABLE IF NOT EXISTS audit(id INTEGER PRIMARY KEY AUTOINCREMENT,actor TEXT,action TEXT,entity TEXT,entity_id TEXT,detail TEXT,created_at TEXT);
    CREATE TABLE IF NOT EXISTS cycle_freeze(cycle TEXT PRIMARY KEY,hash_bases TEXT,app_version TEXT,config_json TEXT,responsible TEXT,frozen_at TEXT);
    '''); con.commit(); con.close()

def sha(path:Path)->str:
    h=hashlib.sha256();
    with open(path,'rb') as f:
        for b in iter(lambda:f.read(65536),b''): h.update(b)
    return h.hexdigest()

def norm_grr(x:Any)->str|None:
    if pd.isna(x): return None
    s=str(x).strip().upper().replace(' ','')
    return s if s.startswith('GRR') and len(s)>=7 else None

def validate_df(df:pd.DataFrame)->list[dict]:
    issues=[]
    if 'GRR' not in df.columns:return [{'severity':'CRITICO','row':'-','column':'GRR','message':'Coluna GRR ausente','action':'Use o modelo oficial.'}]
    for i,v in df['GRR'].items():
        if norm_grr(v) is None:issues.append({'severity':'CRITICO','row':i+2,'column':'GRR','message':f'GRR inválido: {v}','action':'Corrija o identificador.'})
    if df['GRR'].astype(str).duplicated().any(): issues.append({'severity':'ALERTA','row':'-','column':'GRR','message':'Há GRRs repetidos.','action':'Confirme se a granularidade permite repetição.'})
    return issues

def art19(n:int|None,rf:int|None)->str:
    if n is None or rf is None:return 'DADO_PENDENTE'
    lim=0 if n<=2 else 1 if n<=4 else 2
    return 'ATENDE' if rf<=lim else 'NAO_ATENDE'

def art20(approved:int|None,eligible:int|None,min_pct:float=50)->str:
    if approved is None or eligible is None:return 'DADO_PENDENTE'
    if eligible==0:return 'NAO_CALCULAVEL'
    return 'ATENDE' if approved/eligible*100>=min_pct else 'MENOR_50_CONTEXTUALIZAR'

def ial(r:float|None,f:float|None,p:float|None,cfg=None):
    cfg=cfg or load_config(); vals={'rendimento':r,'frequencia':f,'progressao':p}; w=cfg['ial']['weights']
    available={k:v for k,v in vals.items() if v is not None and pd.notna(v)}
    coverage=sum(w[k] for k in available)
    if coverage<cfg['ial']['coverage_partial_min']: return None,coverage,'NAO_CALCULAVEL'
    score=sum(float(available[k])*w[k] for k in available)/coverage*100
    score=max(0,min(100,score)); status='COMPLETO' if abs(coverage-1)<1e-9 else 'PARCIAL_REQUER_CONFERENCIA'
    return round(score,2),round(coverage,2),status

def band(score:float|None,cfg=None)->str:
    if score is None:return 'N/A'
    cfg=cfg or load_config()
    for b in cfg['ial']['bands']:
        if b['min']<=score<=b['max']:return b['label']
    return 'N/A'

def priority(row)->str:
    mcn_bad=sum(str(row.get(k,'')) in ('NAO_ATENDE','MENOR_50_CONTEXTUALIZAR') for k in ['art17','art18','art19','art20','art21'])
    s=row.get('ial')
    if mcn_bad and s is not None and s>=50:return 'A'
    if str(row.get('phase'))=='REAVALIACAO':return 'B'
    if s is not None and s>=50:return 'C'
    if row.get('protection_priority',False):return 'D'
    return 'E'

def freeze_cycle(cycle:str,responsible:str):
    cfg=load_config(); con=connect(); hashes=[r['sha256'] for r in con.execute('SELECT sha256 FROM imports WHERE cycle=? AND status="VALIDO"',(cycle,))]
    digest=hashlib.sha256(''.join(sorted(hashes)).encode()).hexdigest()
    con.execute('INSERT OR REPLACE INTO cycle_freeze VALUES(?,?,?,?,?,?)',(cycle,digest,cfg['app']['version'],json.dumps(cfg,ensure_ascii=False),responsible,dt.datetime.now().isoformat(timespec='seconds')))
    con.commit(); con.close(); return digest

def crps3_allowed(checks:dict[str,bool])->tuple[bool,list[str]]:
    required=['mcn_validada','maic_concluida','escuta_realizada','apoios_verificados','responsabilidade_institucional','justificativas_analisadas']
    missing=[k for k in required if not checks.get(k,False)]
    return not missing,missing
