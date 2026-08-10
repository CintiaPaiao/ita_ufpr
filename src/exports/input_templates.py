from __future__ import annotations

from io import BytesIO
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import re
import pandas as pd

from src.config.base_registry import get_base_spec, list_base_types

# Metadados explicativos centralizados para que o modelo gerado seja também um
# dicionário operacional. Campos não listados aqui ainda aparecem no modelo,
# com descrição genérica baseada no nome técnico.
FIELD_METADATA = {
    "GRR": ("Identificador acadêmico do estudante.", "GRR20260001", "texto"),
    "NOME": ("Nome do estudante.", "Estudante Exemplo", "texto"),
    "CURSO": ("Nome do curso.", "Pedagogia", "texto"),
    "CODIGO_CURSO": ("Código institucional do curso/oferta.", "PED", "texto"),
    "CURRICULO": ("Código/ano da matriz curricular aplicável.", "2025", "texto"),
    "CAMPUS": ("Campus, setor ou localidade da oferta.", "Curitiba", "texto"),
    "INGRESSO": ("Período/ano de ingresso.", "2025/1", "texto"),
    "AUXILIOS": ("Modalidade(s) de auxílio. Quando houver mais de uma, separar por ponto e vírgula.", "Auxílio Permanência;Auxílio Refeição", "texto"),
    "STATUS_BENEFICIO": ("Situação do benefício no ciclo.", "ATIVO", "texto"),
    "RENDA_PER_CAPITA": ("Renda familiar per capita, quando disponível e pertinente à fonte.", "0.75", "número"),
    "DEFICIENCIA_ACESSIBILIDADE": ("Marcador institucional de deficiência/acessibilidade. Não gera score.", "SIM", "texto/booleano"),
    "PARENTALIDADE_CUIDADO": ("Marcador de parentalidade ou responsabilidades de cuidado. Não gera score.", "SIM", "texto/booleano"),
    "REFUGIO_MIGRACAO": ("Marcador de refúgio/migração. Não gera score.", "NAO", "texto/booleano"),
    "ACOLHIMENTO": ("Marcador de acolhimento/egresso de acolhimento.", "NAO", "texto/booleano"),
    "POVOS_COMUNIDADES": ("Marcador de povos/comunidades tradicionais, quando aplicável.", "NAO", "texto/booleano"),
    "PERIODO": ("Período acadêmico da ocorrência.", "2026/1", "texto"),
    "DISCIPLINA_CODIGO": ("Código da disciplina/componente curricular.", "ET208", "texto"),
    "DISCIPLINA_NOME": ("Nome da disciplina/componente curricular.", "Educação Ambiental", "texto"),
    "TURMA": ("Identificador da turma.", "A", "texto"),
    "CH": ("Carga horária da disciplina.", "60", "número"),
    "OBRIGATORIA": ("Indica se a disciplina é obrigatória no currículo.", "SIM", "booleano"),
    "SITUACAO": ("Situação final da matrícula/componente.", "APROVADO", "texto"),
    "APROVADO": ("Indica aprovação na disciplina.", "SIM", "booleano"),
    "REP_NOTA": ("Indica reprovação por nota.", "NAO", "booleano"),
    "REP_FREQ": ("Indica reprovação por frequência.", "NAO", "booleano"),
    "CANCELADO": ("Indica matrícula cancelada.", "NAO", "booleano"),
    "NOTA": ("Nota/conceito numérico quando disponível.", "75", "número"),
    "FREQUENCIA_PCT": ("Percentual de frequência.", "90", "percentual 0–100"),
    "ETAPA": ("Etapa/período curricular ao qual o parâmetro se aplica.", "3", "texto/número"),
    "DURACAO_REGULAR_PERIODOS": ("Duração regular do curso em períodos acadêmicos.", "8", "inteiro"),
    "CH_TOTAL": ("Carga horária total do currículo.", "3200", "número"),
    "CH_MINIMA_ART18": ("Carga mínima aplicável para análise do art. 18.", "240", "número"),
    "GRAU_EVIDENCIA": ("Grau de evidência do parâmetro: A/B/C/D conforme metodologia.", "A", "texto"),
    "FONTE": ("Fonte institucional do dado/parâmetro.", "SIGA/PPP/Resolução", "texto"),
    "ETAPA_RECOMENDADA": ("Etapa/período recomendado da disciplina.", "2", "texto/número"),
    "MATRICULADOS": ("Quantidade de estudantes matriculados na turma.", "40", "inteiro"),
    "APROVADOS": ("Quantidade de estudantes aprovados na turma.", "30", "inteiro"),
    "TAXA_APROVACAO_PCT": ("Taxa geral de aprovação da turma, em percentual.", "75", "percentual 0–100"),
    "VALIDADA": ("Indica se a taxa de turma foi validada institucionalmente.", "SIM", "booleano"),
    "CH_INTEGRALIZADA": ("Carga horária já integralizada pelo estudante.", "1200", "número"),
    "PERIODOS_VINCULO": ("Quantidade bruta de períodos de vínculo.", "6", "inteiro"),
    "PERIODOS_COMPUTAVEIS": ("Períodos efetivamente computáveis após tratamento de exceções.", "5", "inteiro"),
    "PERIODOS_REGULARES": ("Duração regular do currículo em períodos.", "8", "inteiro"),
    "MUDANCA_CURSO": ("Indica mudança de curso que possa afetar a leitura temporal.", "NAO", "booleano"),
    "RETORNO": ("Indica retorno/reingresso relevante à leitura temporal.", "NAO", "booleano"),
    "TRANCAMENTOS": ("Quantidade de períodos de trancamento identificados.", "1", "inteiro"),
    "PROCESSO_ACADEMICO": ("Número de processo acadêmico/SEI relacionado, quando aplicável.", "23075.000000/2026-00", "texto"),
    "POA_PLANO_ESTUDOS": ("Identificação/situação de POA ou Plano de Estudos.", "POA ativo", "texto"),
    "SETOR": ("Equipe/setor responsável pelo acompanhamento.", "PEDAGOGIA", "texto"),
    "ESTADO": ("Estado do acompanhamento.", "ATIVO", "texto"),
    "DATA_ULTIMO_REGISTRO": ("Data do último registro pertinente.", "2026-08-10", "data"),
    "OBJETIVO_SINTETICO": ("Síntese mínima e necessária do acompanhamento/objetivo.", "Acompanhamento acadêmico ativo", "texto"),
    "FATORES_PROTECAO": ("Fatores/barreiras identificados; não gera score.", "TRANSPORTE;PARENTALIDADE_CUIDADO", "texto"),
    "CICLO_CODIGO": ("Ciclo da avaliação anterior.", "2025/2", "texto"),
    "PARTICIPOU": ("Indica participação em avaliação de rendimento anterior.", "SIM", "booleano"),
    "PROFISSIONAL": ("Profissional de referência.", "Profissional 1", "texto"),
    "RESULTADO": ("Resultado registrado no ciclo anterior.", "MANUTENCAO_COM_ACOMPANHAMENTO", "texto"),
    "FASE": ("Fase do caso no registro anterior.", "PRIMEIRA_ANALISE", "texto"),
    "MNA": ("Modalidade/necessidade de acompanhamento anterior.", "ACOMPANHAMENTO_PEDAGOGICO", "texto"),
    "PIAAP": ("Indica existência de PIAAP anterior.", "SIM", "booleano"),
    "ACOES_PACTUADAS": ("Síntese das ações pactuadas no ciclo anterior.", "Organização de matrícula;monitoramento", "texto"),
    "IAL_ANTERIOR": ("IAL anterior quando já calculado pela metodologia nova. ITA legado deve ser tratado como histórico.", "58.5", "número"),
    "MCN_RESUMO": ("Resumo dos critérios normativos do ciclo anterior.", "ART19;ART20", "texto"),
    "ITA": ("Valor histórico do ITA legado. Não é convertido em IAL/CRPS.", "62.0", "número"),
    "APROVACAO_PCT": ("Percentual de aprovação no layout legado.", "40", "percentual 0–100"),
    "REP_FREQ_ATUAL": ("Quantidade de reprovações por frequência no período.", "2", "inteiro"),
    "HIST_FREQ": ("Percentual histórico de reprovação por frequência.", "25", "percentual 0–100"),
    "TEMPO_SEM": ("Tempo bruto de vínculo em semestres no layout legado.", "6", "inteiro"),
    "RENDA": ("Renda per capita no layout legado.", "0.75", "número"),
    "PROAFE": ("Marcador/registro PROAFE presente no layout legado.", "CAS", "texto"),
    "MOTIVO": ("Motivo/observação legado.", "Registro histórico", "texto"),
    "CLASSE_RENDA": ("Classe de renda do modelo legado; preservada apenas historicamente.", "B", "texto"),
    "NOTA_RENDA": ("Nota de renda legada; não entra no IAL.", "60", "número"),
    "ANO_INGRESSO": ("Ano/período de ingresso no layout legado.", "2024", "texto"),
    "CH_INTEGRALIZADA_PCT": ("Percentual/indicador de CH integralizada no layout legado, conforme fonte original.", "45", "número"),
    "CH_IDEAL": ("Indicador legado de CH ideal/esperada.", "240", "número"),
    "QTD_MATRICULADA": ("Quantidade de disciplinas matriculadas no semestre.", "5", "inteiro"),
    "QTD_REP_NOTA": ("Quantidade de reprovações por nota.", "1", "inteiro"),
    "QTD_REP_FREQ": ("Quantidade de reprovações por frequência.", "2", "inteiro"),
    "QTD_CANCELADA": ("Quantidade de cancelamentos.", "0", "inteiro"),
    "IRA_SEM": ("IRA/indicador acadêmico semestral legado.", "0.65", "número"),
    "CH_RECOMENDADA_SEM": ("CH recomendada do semestre no layout legado.", "240", "número"),
    "CH_MAT_TOTAL": ("CH total matriculada no semestre.", "300", "número"),
    "BAIXA_MAT": ("Marcador legado de baixa matrícula.", "NAO", "texto/booleano"),
    "HIST_RF_1": ("Taxa de reprovação por frequência de um período histórico.", "0.20", "número/proporção"),
    "HIST_RF_2": ("Taxa de reprovação por frequência de um período histórico.", "0.10", "número/proporção"),
    "HIST_RF_3": ("Taxa de reprovação por frequência de um período histórico.", "0.00", "número/proporção"),
    "HIST_RF_MEDIA": ("Média histórica de reprovação por frequência.", "0.10", "número/proporção"),
    "AVALIACAO_ANTERIOR": ("Marcador legado de avaliação anterior.", "SIM", "texto/booleano"),
    "RECEBEU_AUX_ANTERIOR": ("Marcador legado de recebimento anterior de auxílio.", "SIM", "texto/booleano"),
    "LEGACY_ITA": ("ITA legado. Preservado apenas como histórico.", "62", "número"),
    "LEGACY_CLASSIFICACAO": ("Classificação legada do ITA.", "RISCO ALTO", "texto"),
    "RESPONSAVEL_ANTERIOR": ("Responsável registrado no ciclo legado.", "Profissional 1", "texto"),
    "DATA_RESPOSTA": ("Data/hora da resposta ao formulário.", "2026-08-10 14:00", "data/hora"),
    "TRABALHO_SUBSISTENCIA": ("Situação de trabalho para subsistência informada pelo estudante.", "SIM", "texto/booleano"),
    "MORADIA": ("Informação estruturada sobre moradia/barreira habitacional.", "NAO", "texto/booleano"),
    "TRANSPORTE": ("Informação estruturada sobre transporte/deslocamento.", "SIM", "texto/booleano"),
    "SAUDE_REPERCUSSAO_ACADEMICA": ("Informação sobre saúde apenas quanto à repercussão acadêmica necessária à contextualização.", "SIM", "texto/booleano"),
}

def _safe_name(value: str) -> str:
    s = re.sub(r"[^A-Za-z0-9_-]+", "_", value).strip("_").lower()
    return s or "modelo"

def _canonical_required(spec: dict) -> set[str]:
    aliases = spec.get("aliases", {})
    required = set()
    for group in spec.get("required_any", []) or []:
        group_norm = {str(x).strip().lower() for x in group}
        for canonical, accepted in aliases.items():
            candidates = {str(x).strip().lower() for x in ([canonical] + list(accepted or []))}
            if group_norm.intersection(candidates):
                required.add(canonical)
                break
    return required

def _preferred_header(canonical: str, accepted: list[str]) -> str:
    # O primeiro alias é garantidamente reconhecido pelo importador atual.
    return str((accepted or [canonical])[0])

def _field_meta(canonical: str):
    if canonical in FIELD_METADATA:
        return FIELD_METADATA[canonical]
    label = canonical.replace("_", " ").title()
    return (f"Campo {label}. Consulte a fonte institucional aplicável.", "", "texto")

def _instructions_rows(base_type: str, spec: dict):
    required = "SIM" if spec.get("required") else "NÃO"
    return [
        ["TIPO_DA_BASE", base_type],
        ["NOME", spec.get("label", base_type)],
        ["OBRIGATÓRIA_NO_FLUXO_FORMAL", required],
        ["GRANULARIDADE", spec.get("grain", "conforme dicionário de dados")],
        ["COMO_USAR", "Preencha a aba MODELO sem alterar os nomes da primeira linha. Apague a linha de exemplo antes do uso real, se desejar."],
        ["ALIASES", "A aplicação também aceita os aliases listados na aba DICIONARIO, mas o cabeçalho do MODELO é a opção recomendada."],
        ["DADOS_AUSENTES", "Não preencher dado desconhecido com zero. Deixe em branco quando a informação não estiver disponível."],
        ["LGPD", "Incluir somente dados necessários à finalidade da Avaliação de Rendimento. Não inserir diagnósticos ou informações sensíveis não requeridas."],
        ["CICLO", "O ciclo é selecionado na aplicação; não é inferido do nome do arquivo."],
    ]

def build_base_template(base_type: str) -> bytes:
    spec = get_base_spec(base_type)
    aliases = spec.get("aliases", {}) or {}
    required = _canonical_required(spec)
    headers = []
    example = {}
    dict_rows = []
    for canonical, accepted in aliases.items():
        header = _preferred_header(canonical, list(accepted or []))
        headers.append(header)
        desc, ex, dtype = _field_meta(canonical)
        example[header] = ex
        dict_rows.append({
            "campo_canonico": canonical,
            "cabecalho_recomendado": header,
            "obrigatorio_minimo": "SIM" if canonical in required else "NÃO",
            "tipo_esperado": dtype,
            "descricao": desc,
            "aliases_aceitos": " | ".join(dict.fromkeys([canonical] + list(accepted or []))),
            "exemplo": ex,
        })
    model = pd.DataFrame([example], columns=headers)
    dictionary = pd.DataFrame(dict_rows)
    instructions = pd.DataFrame(_instructions_rows(base_type, spec), columns=["item", "orientacao"])

    out = BytesIO()
    with pd.ExcelWriter(out, engine="xlsxwriter") as writer:
        model.to_excel(writer, sheet_name="MODELO", index=False)
        dictionary.to_excel(writer, sheet_name="DICIONARIO", index=False)
        instructions.to_excel(writer, sheet_name="INSTRUCOES", index=False)
        wb = writer.book
        wrap = wb.add_format({"text_wrap": True, "valign": "top"})
        header_fmt = wb.add_format({"bold": True, "text_wrap": True, "valign": "top"})
        for sheet_name, frame in [("MODELO", model), ("DICIONARIO", dictionary), ("INSTRUCOES", instructions)]:
            ws = writer.sheets[sheet_name]
            ws.freeze_panes(1, 0)
            ws.autofilter(0, 0, max(1, len(frame)), max(0, len(frame.columns)-1))
            for col_idx, col in enumerate(frame.columns):
                width = min(45, max(14, len(str(col))+2))
                if sheet_name == "DICIONARIO" and col in {"descricao","aliases_aceitos"}:
                    width = 40
                if sheet_name == "INSTRUCOES" and col == "orientacao":
                    width = 70
                ws.set_column(col_idx, col_idx, width, wrap)
            for col_idx, col in enumerate(frame.columns):
                ws.write(0, col_idx, col, header_fmt)
    return out.getvalue()

def build_criteria_workbook_template() -> bytes:
    # Compatibilidade com o workbook de atendimentos utilizado no pacote legado.
    sectors = ["Serviço Social", "Psicologia", "Pedagogia", "CAISE", "CPPOVOS", "CATRIM", "PROAFE-CAS"]
    headers = ["GRR", "ATENDE AOS CRITÉRIOS?", "Observações", "Servidor de Referência", "Data"]
    example = [["GRR20260001", "Sim", "Registro sintético de acompanhamento; não inserir diagnóstico desnecessário.", "Profissional 1", "2026-08-10"]]
    out = BytesIO()
    with pd.ExcelWriter(out, engine="xlsxwriter") as writer:
        for sector in sectors:
            pd.DataFrame(example, columns=headers).to_excel(writer, sheet_name=sector[:31], index=False)
        pd.DataFrame([
            ["GRR", "Obrigatório. Identificador acadêmico."],
            ["ATENDE AOS CRITÉRIOS?", "Campo legado opcional; será preservado como status original e não vira score."],
            ["Observações", "Síntese mínima do acompanhamento."],
            ["Servidor de Referência", "Profissional de referência."],
            ["Data", "Data do registro."],
        ], columns=["campo","orientacao"]).to_excel(writer, sheet_name="DICIONARIO", index=False)
        pd.DataFrame([
            ["Estrutura", "Uma aba por equipe/setor. O sistema reconhece o setor pelo nome da aba."],
            ["Abas reconhecidas", "Serviço Social, Psicologia, Pedagogia, CAISE, CPPOVOS, CATRIM e CAS/PROAFE, além de variações de nome já previstas."],
            ["Obrigatório", "Somente GRR é indispensável por aba. Os demais campos enriquecem o registro."],
            ["LGPD", "Registrar apenas informação necessária; evitar dados sensíveis excessivos."],
        ], columns=["item","orientacao"]).to_excel(writer, sheet_name="INSTRUCOES", index=False)
        for ws in writer.sheets.values():
            ws.freeze_panes(1,0)
            ws.set_column(0,0,24)
            ws.set_column(1,4,42)
    return out.getvalue()

def build_all_templates_zip() -> bytes:
    out = BytesIO()
    with ZipFile(out, "w", ZIP_DEFLATED) as z:
        for base_type, _label in list_base_types():
            z.writestr(f"{base_type}__modelo.xlsx", build_base_template(base_type))
        z.writestr("PACOTE_LEGADO__02_acompanhamentos_por_equipe.xlsx", build_criteria_workbook_template())
        manifest = ["MODELOS DE INPUT – PAE/UFPR", "",
                    "Cada XLSX contém MODELO, DICIONARIO e INSTRUCOES.",
                    "Use os cabeçalhos da aba MODELO para evitar dúvidas de mapeamento.",
                    "A linha preenchida é apenas um exemplo sintético."]
        z.writestr("LEIA-ME.txt", "\n".join(manifest).encode("utf-8"))
    return out.getvalue()
