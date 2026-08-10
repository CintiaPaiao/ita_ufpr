import streamlit as st
import pandas as pd
from src.ui.common import page_setup
from src.db.session import session_scope, database_backend, DATABASE_URL
from src.services.readiness_service import production_readiness, readiness_score
from src.services.backup_service import institutional_backup_zip
from src.services.retention_service import purge_technical_logs
from src.services.bootstrap_service import bootstrap_application

page_setup("Produção e Prontidão – v0.4.2", allowed_roles=("ADMIN","CHEFIA"))
bootstrap=bootstrap_application()
st.info(f"Bootstrap automático: banco={bootstrap.database_backend}; ciclos criados nesta execução={', '.join(bootstrap.cycles_created) if bootstrap.cycles_created else 'nenhum (já existentes)'}.")
with session_scope() as s:
    checks=production_readiness(s); score,ready=readiness_score(checks)
    col1,col2=st.columns(2); col1.metric("Prontidão",f"{score}%"); col2.metric("Críticos atendidos","SIM" if ready else "NÃO")
    df=pd.DataFrame(checks); st.dataframe(df,hide_index=True,use_container_width=True)
    if ready: st.success("Nenhuma falha crítica de configuração foi detectada pelo checklist automático. O sistema está tecnicamente pronto para homologação/produção conforme a infraestrutura configurada.")
    else: st.error("Há falhas críticas. Não utilizar dados reais em produção até corrigi-las. Em Streamlit Community Cloud, SQLite local é considerado falha crítica de persistência para produção.")
    st.subheader("Backup institucional")
    st.caption("O ZIP pode conter dados pessoais/sensíveis. Faça download apenas em equipamento/armazenamento institucional autorizado.")
    backup=institutional_backup_zip(s)
    st.download_button("Gerar e baixar backup institucional",backup,"backup_pae.zip","application/zip")
    st.subheader("Retenção de logs técnicos")
    days=st.number_input("Dias mínimos a preservar",min_value=30,max_value=3650,value=730)
    dry=purge_technical_logs(s,older_than_days=int(days),dry_run=True)
    st.write(dry)
    confirm=st.checkbox("Confirmo que a política institucional autoriza a exclusão dos logs acima do prazo informado")
    if st.button("Executar expurgo técnico",disabled=not confirm):
        result=purge_technical_logs(s,older_than_days=int(days),dry_run=False); st.success(str(result))
st.caption(f"Backend atual: {database_backend()}. A URL completa do banco não é exibida por segurança.")
