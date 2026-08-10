from __future__ import annotations
TEMPLATES={
"CONVOCACAO":"""Assunto: Avaliação de Rendimento PAE/UFPR – convite para contextualização e atendimento\n\nPrezado(a) {nome},\n\nNo âmbito da Avaliação de Rendimento do PAE/UFPR referente ao ciclo {ciclo}, solicitamos sua participação na etapa de contextualização da trajetória acadêmica. Esta etapa integra o acompanhamento institucional e não constitui sanção automática.\n\nOrientações/prazo: {prazo}\n\nAtenciosamente,\nEquipe responsável""",
"MANUTENCAO":"""Assunto: Avaliação de Rendimento PAE/UFPR – registro de manutenção\n\nPrezado(a) {nome},\n\nInformamos o registro de manutenção no ciclo {ciclo}, conforme análise individualizada realizada. Próximo marco/orientação: {prazo}.\n\nAtenciosamente,\nEquipe responsável""",
"DILIGENCIA":"""Assunto: Avaliação de Rendimento PAE/UFPR – diligência\n\nPrezado(a) {nome},\n\nPara continuidade da análise do ciclo {ciclo}, solicita-se o seguinte esclarecimento/documentação: {prazo}.\n\nAtenciosamente,\nEquipe responsável""",
"POSSIVEL_SUSPENSAO":"""Assunto: Avaliação de Rendimento PAE/UFPR – comunicação para exercício do contraditório\n\nPrezado(a) {nome},\n\nApós as etapas de análise individualizada previstas para o ciclo {ciclo}, foi identificada situação que requer manifestação antes de eventual decisão administrativa. Esta comunicação não corresponde, por si só, à suspensão do auxílio.\n\nPrazo/orientações para manifestação: {prazo}\n\nAtenciosamente,\nEquipe responsável""",
}

def render_template(kind:str, *, nome:str, ciclo:str, prazo:str="conforme comunicação institucional") -> str:
    if kind not in TEMPLATES: raise KeyError(kind)
    return TEMPLATES[kind].format(nome=nome,ciclo=ciclo,prazo=prazo)
