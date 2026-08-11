# PAE/UFPR — Avaliação de Rendimento v0.4.5.1

Aplicação Streamlit de apoio técnico-operacional à Avaliação de Rendimento e acompanhamento das trajetórias. **Não automatiza parecer, CRPS final, suspensão ou decisão administrativa.**

## Novidades 0.4.5.1
- Jornada guiada do ciclo e indicação de situação/próxima ação.
- Central de Configurações para N, equipe, IAL, parâmetros normativos/operacionais e feature flags.
- Validação de entrada orientada à correção.
- Congelamento do ciclo com hash, versão e snapshot de configuração.
- MCN/IAL explicáveis.
- Fila/ficha profissional e registros transacionais.
- Trava explícita para CRPS-3.
- Painel de qualidade/auditoria.
- UX mais simples, com menos exposição à estrutura interna das planilhas.

## Executar
```bash
python scripts/load_sample_data.py
streamlit run app.py
```
Testes: `pytest -q`.

## Central de configurações
Parâmetros mapeáveis ficam em `configs/settings.yaml` e podem ser alterados pela tela administrativa. Mudanças metodológicas devem ser pactuadas e congeladas em nova versão do ciclo.

## Dependências institucionais
Art. 18 automático, fonte de taxa de turma do art. 20, regras finais do art. 21, protocolo PIAAP, Comissão e pesos/faixas finais do IAL devem permanecer configuráveis/bloqueáveis quando não pactuados.

## Segurança
Este pacote contém apenas dados sintéticos. Para produção, integrar autenticação institucional/RBAC e banco persistente adequado antes de carregar dados reais.
