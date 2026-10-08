# Custos e disponibilidade offshore

Um primeiro projeto de portefólio para praticar o trabalho de um Business Data Analyst: definir perguntas de negócio, preparar dados, consultar SQL, criar um painel e apresentar recomendações.

**Todos os ativos e dados são fictícios. Não são dados da SBM Offshore.** O exercício usa três unidades offshore durante janeiro a junho de 2025, com erros deliberados para demonstrar controlo de qualidade.

## Começar no Windows

Segue o [guia de instalação Windows](docs/windows.md). Explica como descobrir o que já está instalado, obter as ferramentas através das fontes oficiais, extrair o projeto e abrir o painel. A instalação no teu computador será validada contigo; os testes aqui executam no ambiente Linux da nuvem.

## O que vais aprender

1. **Pergunta de negócio:** que unidade ultrapassa o orçamento e onde investigar as paragens?
2. **Python e ETL:** transformar um CSV de entrada num conjunto validado, guardando os problemas encontrados.
3. **SQL e modelação:** consultar uma base SQLite com dimensões de ativo e mês e uma tabela de factos mensais.
4. **Visualização:** filtrar os indicadores e comparar custos, orçamento e disponibilidade.
5. **Comunicação:** explicar recomendações e limites, seguindo o [guia para a entrevista](docs/entrevista.md).

Começa por instalar e abrir a demonstração. Depois explora os dados, as consultas e os indicadores, por esta ordem. Não precisas de estudar todos os ficheiros de uma vez.

## Arranque na nuvem / Linux

Python 3.12 ou 3.13. Cada tarefa já tem um ambiente isolado; utiliza este checkout existente.

```bash
cd /workspace/chatgpt
bash scripts/setup.sh
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python -m streamlit run app.py --server.address 127.0.0.1 --server.port 8501 --server.headless true --browser.gatherUsageStats false
```

O processo do painel tem de arrancar de novo em cada máquina; ficheiros e dependências não mantêm processos vivos. Na nuvem, o painel é validado internamente. No Windows, o navegador abre o painel local.

## Ficheiros principais

| Ficheiro | Para que serve |
| --- | --- |
| `offshore_demo/pipeline.py` | Gerar os dados de demonstração, validar e preparar CSV e SQLite |
| `sql/analysis.sql` | Consultas de análise para estudar e executar |
| `scripts/run_sql.py` | Executar essas consultas com o SQLite incluído no Python |
| `app.py` | Painel interativo |
| `data/raw/operations.csv` | Entrada gerada na primeira execução; preservada nas seguintes |
| `data/processed/operations.csv` | Dados aceites, para o painel e para importar no Power BI |
| `data/processed/offshore.sqlite` | Base de dados local, sem servidor separado |
| `data/processed/quality_report.json` | Contagens e indicadores da execução de preparação |
| `requirements.txt` | Dependências fixas com hashes para verificar os downloads |

Os dados gerados e o ambiente `.venv` estão excluídos do Git. A pipeline volta a gerá-los. Se mudares o CSV de entrada, volta a executar `python -m offshore_demo.pipeline` com o Python do ambiente virtual; as saídas serão atualizadas e a entrada será preservada.

## Definições dos indicadores

- **Desvio (€)** = despesa real − orçamento. Um valor positivo significa despesa acima do previsto.
- **Desvio (%)** = desvio / orçamento × 100. Sem orçamento, a percentagem não é calculada.
- **Disponibilidade (%)** = (horas do período − horas de paragem) / horas do período × 100. Inclui paragens planeadas e não planeadas, consideradas sem sobreposição.
- Para juntar unidades e meses, primeiro somamos custos e horas. Não fazemos a média das percentagens individuais.
- Cada registo aceite representa **uma unidade num mês**, com custos em EUR. As horas do período correspondem ao mês de calendário completo.

Estes indicadores são definições do exercício. Numa empresa real, seriam acordados com operações e finanças antes de construir o relatório. Horas disponíveis não equivalem a volume produzido; o exercício não estima receitas, perdas de produção ou causalidade das paragens.

## Validação

```bash
.venv/bin/python -m unittest discover -s tests -v
```

Os testes incluem qualidade dos dados, consultas/indicadores, repetibilidade e execução do painel com filtros. A demonstração não contém um ficheiro Power BI `.pbix`; o guia ensina a criá-lo no Power BI Desktop com o CSV preparado.
