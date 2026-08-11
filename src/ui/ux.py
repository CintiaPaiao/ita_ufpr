from __future__ import annotations
import streamlit as st


def inject_app_css():
    st.markdown('''
    <style>
    .block-container {padding-top: 1.4rem; padding-bottom: 3rem; max-width: 1500px;}
    [data-testid="stMetric"] {background: rgba(31,78,120,.06); border: 1px solid rgba(31,78,120,.15); padding: .7rem; border-radius: .65rem;}
    .pae-card {border:1px solid #D9E2F3; border-radius:12px; padding:16px 18px; margin:8px 0 14px 0; background:#F8FAFD;}
    .pae-card h4 {margin:0 0 4px 0;color:#1F4E78;}
    .pae-step {font-size:.91rem; padding:.45rem .65rem; border-radius:.55rem; margin:.15rem; display:inline-block; border:1px solid #D9E2F3;}
    .pae-done {background:#E2F0D9;}
    .pae-current {background:#DDEBF7;font-weight:700;border-color:#5B9BD5;}
    .pae-pending {background:#F3F3F3;color:#666;}
    </style>
    ''', unsafe_allow_html=True)


def info_card(title: str, body: str, *, icon: str = 'ℹ️'):
    st.markdown(f'<div class="pae-card"><h4>{icon} {title}</h4><div>{body}</div></div>', unsafe_allow_html=True)


def step_strip(steps: list[tuple[str,str]]):
    html=[]
    for label,status in steps:
        cls='pae-done' if status=='done' else ('pae-current' if status=='current' else 'pae-pending')
        html.append(f'<span class="pae-step {cls}">{label}</span>')
    st.markdown(''.join(html), unsafe_allow_html=True)
