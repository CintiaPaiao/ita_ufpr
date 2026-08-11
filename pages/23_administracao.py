import streamlit as st
import pandas as pd
from sqlalchemy import select

from src.ui.common import page_setup, safe_exception
from src.security.auth import require_role, bootstrap_user
from src.db.session import session_scope
from src.exports.unified_excel import export_unified_workbook
from src.config.settings import IAL_CONFIG, MCN_CONFIG, PRIORITY_CONFIG, FEATURE_FLAGS
from src.models.models import User, Cycle
from src.services.bootstrap_service import (
    ALLOWED_CYCLE_STATUSES,
    ensure_default_cycles,
    create_cycle,
    activate_cycle,
    close_cycle,
    reopen_cycle,
)

require_role("ADMIN", "CHEFIA")
current = page_setup("Administração e Configuração", allowed_roles=("ADMIN", "CHEFIA"))

t1, t2, t3, t4 = st.tabs(["Configurações", "Ciclos", "Usuários", "Exportações"])

with t1:
    st.json({"IAL": IAL_CONFIG, "MCN": MCN_CONFIG, "PRIORIZACAO": PRIORITY_CONFIG, "FEATURE_FLAGS": FEATURE_FLAGS})
    st.caption("Alterações metodológicas devem ser feitas em configuração versionada e submetidas à validação institucional.")

with t2:
    st.subheader("Gestão dos ciclos semestrais")
    st.caption(
        "Os ciclos básicos definidos em configs/ciclos.yaml são criados automaticamente no primeiro acesso. "
        "Esta tela permite cadastrar ciclos futuros e controlar sua situação administrativa."
    )
    with session_scope() as s:
        ensure_default_cycles(s)
        cycles = list(s.scalars(select(Cycle).order_by(Cycle.codigo)))
        data = [
            {
                "id": c.id,
                "ciclo": c.codigo,
                "status": c.status,
                "congelado_em": c.frozen_at,
                "responsavel": c.responsavel,
                "versao_codigo": c.code_version,
                "versao_mcn": c.mcn_version,
                "versao_ial": c.ial_version,
            }
            for c in cycles
        ]
    st.dataframe(pd.DataFrame(data), hide_index=True, width="stretch")

    if current["role"] == "ADMIN":
        st.markdown("#### Criar novo ciclo")
        with st.form("create_cycle_form"):
            codigo = st.text_input("Código do ciclo", placeholder="Ex.: 2026/2")
            status = st.selectbox("Status inicial", sorted(ALLOWED_CYCLE_STATUSES), index=sorted(ALLOWED_CYCLE_STATUSES).index("PREPARACAO_DADOS"))
            create_ok = st.form_submit_button("Criar ciclo")
        if create_ok:
            try:
                with session_scope() as s:
                    create_cycle(s, codigo=codigo, status=status)
                st.success(f"Ciclo {codigo.strip()} criado.")
                st.rerun()
            except Exception as exc:
                safe_exception(exc)

        st.markdown("#### Alterar situação do ciclo")
        if cycles:
            options = {f"{c.codigo} — {c.status}": c.id for c in cycles}
            selected_label = st.selectbox("Ciclo", list(options), key="admin_cycle_select")
            selected_id = options[selected_label]
            c1, c2, c3 = st.columns(3)
            if c1.button("Ativar ciclo", width="stretch"):
                try:
                    with session_scope() as s:
                        activate_cycle(s, selected_id)
                    st.success("Ciclo ativado.")
                    st.rerun()
                except Exception as exc:
                    safe_exception(exc)
            if c2.button("Encerrar ciclo", width="stretch"):
                try:
                    with session_scope() as s:
                        close_cycle(s, selected_id)
                    st.success("Ciclo encerrado. Novas importações ficam bloqueadas.")
                    st.rerun()
                except Exception as exc:
                    safe_exception(exc)
            if c3.button("Reabrir ciclo", width="stretch"):
                try:
                    with session_scope() as s:
                        reopen_cycle(s, selected_id)
                    st.success("Ciclo reaberto como ATIVO. O histórico de congelamento foi preservado.")
                    st.rerun()
                except Exception as exc:
                    safe_exception(exc)
    else:
        st.info("A CHEFIA pode consultar os ciclos. Criação/alteração de status é restrita ao ADMIN.")

with t3:
    st.subheader("Usuários do banco")
    with session_scope() as s:
        users = list(s.scalars(select(User).order_by(User.username)))
        data = [{"username": u.username, "nome": u.display_name, "perfil": u.role, "ativo": u.active} for u in users]
    st.dataframe(pd.DataFrame(data), hide_index=True, width="stretch")
    if current["role"] == "ADMIN":
        st.subheader("Criar/atualizar usuário")
        with st.form("user_admin"):
            username = st.text_input("Usuário")
            display = st.text_input("Nome de exibição")
            role = st.selectbox("Perfil", ["ADMIN", "PROFISSIONAL", "CHEFIA", "COMISSAO", "AUDITOR"])
            password = st.text_input("Senha", type="password")
            overwrite = st.checkbox("Atualizar se já existir")
            ok = st.form_submit_button("Salvar usuário")
        if ok:
            if len(password) < 10:
                st.error("Use senha com pelo menos 10 caracteres.")
            else:
                with session_scope() as s:
                    bootstrap_user(s, username=username, display_name=display or username, role=role, password=password, overwrite=overwrite)
                st.success("Usuário salvo com hash PBKDF2; a senha não é armazenada em texto claro.")

with t4:
    with session_scope() as s:
        data = export_unified_workbook(s)
    st.download_button(
        "Exportar Planilha Unificada (19 abas)",
        data=data,
        file_name="planilha_unificada_pae.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
