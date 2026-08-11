import streamlit as st, pandas as pd, datetime as dt
from src.core import connect,init_db
from src.ui.helpers import setup,next_action
setup('Fila profissional e ficha do estudante');init_db(); con=connect();rows=con.execute('SELECT * FROM results ORDER BY selected DESC, ial DESC').fetchall();df=pd.DataFrame([dict(r) for r in rows]);con.close()
if df.empty: st.info('Ainda não há resultados processados. Use os dados sintéticos ou importe/processa um ciclo.')
else:
 st.dataframe(df,use_container_width=True);grr=st.selectbox('Abrir ficha',df.grr.tolist());r=df[df.grr==grr].iloc[0];next_action(r.phase,'Conferir pendências e registrar a etapa profissional adequada.')
 tabs=st.tabs(['Resumo','MCN','IAL','Contextualização','Atendimentos','MAIC/MNA','PIAAP','Manutenção','Monitoramento','Reavaliação','CRPS/Recursos','Timeline'])
 with tabs[0]:st.json(r.to_dict())
 for t in tabs[1:-1]:
  with t: st.caption('Módulo transacional conectado ao registro profissional. A conclusão é humana.');kind=t.label if hasattr(t,'label') else 'REGISTRO'
 with tabs[-1]:
  con=connect(); rr=con.execute('SELECT * FROM professional_records WHERE grr=? ORDER BY created_at',(grr,)).fetchall();con.close();st.dataframe(pd.DataFrame([dict(x) for x in rr]),use_container_width=True)
 st.subheader('Novo registro profissional')
 kind=st.selectbox('Tipo',['CONTEXTUALIZACAO','ATENDIMENTO','MAIC','MNA','PIAAP','MANUTENCAO','MONITORAMENTO','REAVALIACAO','PARECER','RECURSO']);summary=st.text_area('Síntese mínima necessária');action=st.text_input('Próxima ação');
 if st.button('Salvar registro'):
  con=connect();con.execute('INSERT INTO professional_records(grr,cycle,kind,status,summary,next_action,created_at) VALUES(?,?,?,?,?,?,?)',(grr,r.cycle,kind,'REGISTRADO',summary,action,dt.datetime.now().isoformat()));con.commit();con.close();st.success('Registro salvo.')
