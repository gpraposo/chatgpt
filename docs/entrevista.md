# Preparar a apresentação para a entrevista

Este projeto é um exercício de portefólio com **dados simulados**, criado para praticar competências pedidas na vaga de Business Data Analyst. Não representa dados, processos internos ou resultados reais da SBM Offshore.

Um projeto pequeno pode mostrar raciocínio analítico e cuidado com os dados. Não substitui a experiência profissional pedida no anúncio; apresenta-o como aprendizagem e demonstração prática.

## A pergunta de negócio

> Como podemos identificar unidades que registam custos acima do orçamento e mais tempo de paragem, para ajudar operações e finanças a definir prioridades de investigação?

A pergunta orienta o trabalho: começamos pela decisão que alguém precisa de tomar e, depois, escolhemos dados, indicadores e gráficos.

Usamos unidades offshore fictícias. Cada registo representa **uma unidade num mês**. Esta unidade de registo chama-se **granularidade**. Conhecê-la evita juntar tabelas de forma errada e contar os mesmos custos ou horas várias vezes.

## Como o projeto corresponde à vaga

| Responsabilidade no anúncio | O que podemos demonstrar no projeto |
| --- | --- |
| Analisar dados para apoiar decisões | Comparar orçamento e despesa, localizar desvios e identificar períodos que merecem investigação. |
| Compreender necessidades de negócio | Explicar as perguntas que faríamos a finanças e operações para acordar definições e prioridades. |
| Desenvolver modelos, dashboards e relatórios | Organizar tabelas, consultar os dados com SQL e criar um painel em Python; criar a versão Power BI localmente. |
| Assegurar exatidão e qualidade | Validar campos, chaves, datas e valores e tornar visíveis os problemas encontrados. |
| Extrair, transformar e carregar dados | Reproduzir a preparação dos dados com uma pipeline Python. |
| Identificar tendências e anomalias | Comparar meses e unidades e destacar alterações para revisão humana. |
| Apresentar recomendações | Preparar um breve relatório com observações, limites e próximos passos. |
| Apoiar a utilização das ferramentas | Documentar instalação, execução e interpretação dos indicadores. |

As necessidades das equipas neste projeto são pressupostos de um cenário fictício. Não afirmes que colaboraste com equipas da empresa se essa colaboração não aconteceu.

## Indicadores que deves conseguir explicar

**Desvio de custos em euros:** custo real menos orçamento. Um número positivo significa que gastámos mais do que o previsto.

**Desvio de custos em percentagem:** desvio dividido pelo orçamento. Ajuda a comparar unidades com orçamentos diferentes. Se o orçamento for zero, a percentagem não é interpretável: precisamos de mostrar essa situação em vez de inventar um valor.

**Disponibilidade operacional nesta demonstração:** horas do período menos todas as horas de paragem, dividido pelas horas do período. Incluímos paragens planeadas e não planeadas. A fórmula teria de ser acordada com a equipa de operações para utilização real.

**Horas de paragem não planeada:** permitem distinguir interrupções inesperadas de atividades previstas. A sua existência, por si só, não nos diz a causa da interrupção nem o seu impacto financeiro.

Para agregar disponibilidade entre meses e unidades, calculamos a proporção a partir das somas de horas. Não fazemos uma média simples de percentagens.

## Perguntas que faríamos antes de usar dados reais

- Quem usa o relatório e que decisão precisa de tomar?
- De que sistemas vêm o orçamento, os custos e as horas de paragem?
- Quem é responsável por cada fonte e pela aprovação das definições?
- O orçamento é inicial ou revisto? Em que moeda e período são registados os custos?
- Custos de manutenção estão incluídos no custo total? Como evitamos contá-los duas vezes?
- Como se distinguem paragens planeadas e não planeadas? Eventos sobrepostos podem duplicar horas?
- Com que frequência precisamos de atualizar os dados e o que acontece quando uma fonte chega atrasada?
- Quem pode ver o detalhe e durante quanto tempo devemos conservar os dados?

Estas perguntas mostram atenção a finanças, operações e governação. Neste exercício não temos respostas de stakeholders reais; documentamos os pressupostos adotados.

## Contar a história em cerca de dois minutos

Depois de executares e compreenderes o projeto, podes adaptar este exemplo às partes que efetivamente completaste:

> “Construí um projeto de portefólio com dados simulados de operações offshore. A pergunta foi perceber onde os custos ultrapassam o orçamento e como variam as horas de paragem, para apoiar a priorização de uma investigação por operações e finanças.
>
> Defini o registo ao nível da unidade e do mês, preparei os dados em Python e consultei as tabelas com SQL. Validei a qualidade dos dados antes de calcular os indicadores. Documentei as definições, incluindo a forma de calcular a disponibilidade a partir das horas, para evitar uma média incorreta de percentagens.
>
> Criei um painel que permite comparar unidades e períodos e preparar recomendações. Os resultados são ilustrativos: não concluo que as paragens causam um desvio de custos apenas porque os dois aparecem no mesmo período. Num contexto real confirmaria as definições com as equipas, investigaria os eventos de manutenção e validaria o efeito de qualquer ação.”

Acrescenta a versão Power BI à apresentação apenas depois de a construíres e verificares. Faz o mesmo com qualquer função ou teste: fala do que compreendes e consegues demonstrar.

## Preparar uma página para um gestor

Quando o painel estiver a funcionar, escreve uma página com estas cinco partes:

1. **Objetivo:** a decisão ou investigação que o relatório pretende apoiar.
2. **Observação:** unidade, período e valor calculado, com indicação do filtro utilizado.
3. **Interpretação:** o que os dados sugerem e o que ainda não permitem concluir.
4. **Recomendação:** uma ação concreta, como rever ordens de manutenção, confirmar a classificação das despesas ou verificar o orçamento aprovado.
5. **Validação:** quem deve confirmar a hipótese e qual o indicador a acompanhar depois.

Exemplo de estrutura, sem números inventados:

> “No período selecionado, a unidade [nome] apresenta um desvio de [valor] face ao orçamento e [valor] horas de paragem não planeada. Recomendo rever os principais lançamentos de custos e os eventos de manutenção desse período com finanças e operações. A ocorrência simultânea não estabelece uma relação de causa e efeito. Depois da investigação, acompanharíamos o desvio e as horas de paragem para avaliar as ações tomadas.”

Preenche os campos a partir dos resultados reais do exercício. Um achado sobre dados simulados continua a ser um achado ilustrativo, não uma poupança comprovada.

## Perguntas prováveis na entrevista

**“Porque escolheste estes indicadores?”**

Porque ligam duas necessidades de negócio: controlo de custos e acompanhamento das operações. Explica quem usaria cada indicador e que decisão pode apoiar.

**“Como garantiste a qualidade dos dados?”**

Mostra as verificações implementadas e os respetivos resultados. Distingue registos excluídos, erros que interrompem a execução e problemas que exigem revisão. Não digas apenas “limpei os dados”.

**“Como evitarias indicadores inconsistentes entre departamentos?”**

Acordaria a definição, granularidade, fonte, regra de cálculo, frequência de atualização e responsável. Guardaria essas regras numa documentação acessível e validaria exemplos com os utilizadores.

**“Uma unidade com mais paragens tem sempre custos mais altos?”**

Não. Os custos podem refletir manutenção planeada, preços, contratos, atividade ou despesas reconhecidas noutro período. O painel localiza situações para investigar; a causa exige dados e contexto adicionais.

**“O que falta para isto ser uma solução de produção?”**

Fontes reais aprovadas, validação com as equipas, controlo de acessos, atualização automatizada, monitorização das execuções e qualidade, tratamento de alterações nos dados e procedimentos de suporte. Neste exercício executamos localmente e documentamos os pressupostos.

**“Como medes o sucesso do relatório?”**

Definiria a medida com os utilizadores: tempo necessário para preparar o reporte, consistência dos indicadores, utilização do painel e rapidez de identificação e resolução de problemas. Só atribuiria poupanças ao projeto com uma avaliação apropriada.

## O que levar para a entrevista

- Uma imagem ou demonstração curta do painel com indicação “dados simulados”.
- A página de recomendações baseada nos resultados do exercício.
- Uma consulta SQL que saibas explicar linha a linha.
- Um exemplo de validação de dados e a razão de existir.
- As definições dos indicadores e as limitações do projeto.
- O código e a documentação que consegues explicar, num repositório publicável quando decidires partilhá-lo.

A clareza da explicação é parte da demonstração. Se uma escolha técnica não estiver clara, usa-a como próxima oportunidade de aprendizagem antes da entrevista.
