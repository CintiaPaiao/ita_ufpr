# Calculadora ITA - Índice de Trajetória Acadêmica

Aplicação web para cálculo do ITA a partir de planilhas do Google Sheets.

obs: para cintribuir para o projeto, crie uma nova branch para rastreabilidade

## Estrutura do Projeto

- `app.py`: Interface do usuário (Streamlit).
- `ita_calc.py`: Lógica de cálculo e processamento de dados.
- `requirements.txt`: Dependências do projeto.
- `Dockerfile`: Configuração para containerização.

## Como Executar Localmente

1.  Instale as dependências:
    ```bash
    pip install -r requirements.txt
    ```
2.  Execute a aplicação:
    ```bash
    streamlit run app.py
    ```

## Como Executar com Docker

1.  Construa a imagem:
    ```bash
    docker build -t ita-app .
    ```
2.  Execute o container:
    ```bash
    docker run -p 8501:8501 ita-app
    ```
3.  Acesse `http://localhost:8501` no navegador.

## Uso

1.  Insira os links públicos (ou com permissão de acesso) das planilhas:
    - Planilha Completa
    - Planilha Critérios
    - Planilha Formulário
2.  Clique em "Calcular ITA".
3.  Visualize os resultados e baixe a planilha final.
