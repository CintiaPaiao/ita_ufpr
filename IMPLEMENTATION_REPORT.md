# Implementation Report — v0.4.5.1

## Síntese
A v0.4.5.1 concentra a evolução em usabilidade, configuração centralizada, explicabilidade, rastreabilidade e travas de segurança metodológica.

## Implementado
Jornada do ciclo; importação manual; validação acionável; hash/congelamento; SQLite; central de configurações; IAL configurável; MCN demonstrável; fila/ficha; registros profissionais; timeline básica; CRPS com checklist; recursos como fluxo; painel QA; dados sintéticos; testes; Docker.

## Parcial / dependente de pactuação
Arts. 17, 18 e 21 exigem fontes curriculares/temporais completas. Art. 20 depende da fonte oficial de taxa de turma para exclusões. RBAC/SSO institucional não está habilitado neste pacote local. PIAAP e Comissão permanecem sujeitos a protocolo institucional. Auditoria de equidade exige desenho de agregação/supressão antes de dados reais.

## Critérios de aceite
- aplicação importa módulos e inicia com Streamlit;
- banco SQLite é criado;
- sample data carrega;
- art. 19, art. 20 e IAL possuem testes;
- E=0 retorna NAO_CALCULAVEL;
- IAL respeita [0,100] e cobertura;
- pesos somam 1 na UI;
- fatores protegidos não compõem IAL;
- CRPS-3 é bloqueada sem checklist;
- configuração fica fora da regra principal;
- ciclo pode ser congelado com hash/configuração;
- nenhum dado real/credencial é incluído.

## Segurança
Não usar este MVP com dados reais antes de autenticação/RBAC institucional, política de retenção, revisão de logs e implantação persistente segura.
