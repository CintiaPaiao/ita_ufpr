import sys,random
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from src.core import *
init_db();cfg=load_config();con=connect();random.seed(45)
for i in range(1,31):
 grr=f'GRR2026{i:04d}';con.execute('INSERT OR REPLACE INTO students VALUES(?,?,?,?,?)',(grr,f'Estudante Sintético {i}',random.choice(['Pedagogia','Geografia','Agronomia']),random.choice(['Curitiba','Palotina']),'2026'))
 n=random.randint(2,7);rf=random.randint(0,3);approved=random.randint(0,n);r=random.random();f=random.random();p=random.random();score,cov,status=ial(r,f,p,cfg);a19=art19(n,rf);a20=art20(approved,n,cfg['mcn']['art20_min_approval']);phase='REAVALIACAO' if i%7==0 else 'PRIMEIRA_ANALISE';row={'art17':'ATENDE','art18':'PARAMETRO_NAO_CONFIRMADO','art19':a19,'art20':a20,'art21':'REQUER_CONFERENCIA','ial':score,'phase':phase};layer=priority(row)
 con.execute('INSERT OR REPLACE INTO results(grr,cycle,art17,art18,art19,art20,art21,ial,coverage,ial_band,priority_layer,selected,professional,phase) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)',(grr,'2025/2',row['art17'],row['art18'],a19,a20,row['art21'],score,cov,band(score,cfg),layer,1 if i<=20 else 0,f'Profissional {(i-1)%5+1}',phase))
con.commit();con.close();print('30 estudantes sintéticos carregados')
