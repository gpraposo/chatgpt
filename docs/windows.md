# Instalar e usar o projeto no Windows

Este guia prepara o teu computador para o projeto **Custos e Disponibilidade Offshore**. Os dados são simulados: representam uma empresa fictícia e não pertencem à SBM Offshore.

Podemos avançar por etapas. Primeiro põe a aplicação a funcionar; depois importa os resultados para o Power BI. O Power BI não é necessário para iniciar o painel Python.

No teu caso já confirmámos **Windows 11 e Visual Studio Code de 64 bits instalado**. Os comandos de Python e Git não foram reconhecidos; precisamos de confirmar se estão ausentes ou se falta a configuração do PATH. A presença do Power BI ainda precisa de confirmação. Não é necessário voltar a instalar o Visual Studio Code.

## 1. O que vamos instalar e para que serve

| Ferramenta | Para que a usamos | Necessária agora? |
| --- | --- | --- |
| Python 3.13 | Executar o programa que prepara os dados e o painel | Sim |
| Visual Studio Code | Abrir a pasta do projeto e editar os ficheiros | Já instalado |
| Git | Guardar versões do trabalho e, mais tarde, enviá-las para o GitHub | Mais tarde |
| Power BI Desktop | Criar uma segunda versão do painel, útil para a entrevista | Depois do primeiro painel |
| SQLite | Guardar e consultar dados com SQL | Já incluído no Python |
| pandas e Streamlit | Preparar tabelas e apresentar o painel no navegador | Instalados pelo comando do projeto |

Não precisas de instalar um servidor SQL para esta primeira versão. Também não precisas de comprar Excel ou uma licença Power BI para trabalhar localmente com este projeto. A publicação e partilha no serviço Power BI são uma etapa separada e podem exigir licenças.

## 2. Verificar o que já existe, antes de instalar

Não precisas de saber onde cada programa está instalado. Faz esta verificação simples:

1. Prime **Windows+R**, escreve `winver` e prime Enter. A janela mostra se tens Windows 10 ou 11 e a versão.
2. Abre **Definições → Sistema → Acerca de** e procura **Tipo de sistema**. Os instaladores abaixo assumem um computador Intel/AMD de 64 bits; num equipamento ARM, precisamos de adaptar a escolha.
3. No menu Iniciar escreve **PowerShell** e abre-o. É uma janela onde podemos escrever instruções para o computador.
4. Escreve cada um destes comandos, um de cada vez, e prime Enter:

```powershell
py --version
```

```powershell
git --version
```

```powershell
code --version
```

5. Procura **Power BI Desktop** no menu Iniciar.

Se um comando mostrar uma versão, a ferramenta foi encontrada. Se disser “não é reconhecido”, pode estar por instalar ou instalada sem estar no **PATH**, a lista de locais onde o Windows procura programas. Não concluas imediatamente que precisas de reinstalar: procura também o programa no menu Iniciar e partilha a mensagem para verificarmos.

No caso do Python, podemos ver as versões disponíveis com:

```powershell
py -0p
```

Os comandos seguintes usam Python 3.13. O código também suporta Python 3.12; se já tiveres essa versão, podemos usar `py -3.12` para criar o ambiente, em vez de instalar outra. As bibliotecas fixadas neste projeto foram preparadas para estas versões. Num computador da empresa, segue as regras da equipa de informática.

## 3. Instalar Python, se necessário

No teu Windows, o `winget` já foi confirmado. É o gestor de instalações do Windows. Podes instalar Python a partir do catálogo com:

```powershell
winget install --id Python.Python.3.13 --exact --source winget
```

Espera pelo fim da instalação. Se aparecer uma falha, guarda a mensagem para a diagnosticarmos. O catálogo escolhe a versão disponível dessa série e o instalador adequado à máquina. Se pedirem aceitação de termos, lê-os antes de aceitar.

Como alternativa, podes usar o instalador oficial:

1. Abre a [página oficial de downloads Python para Windows](https://www.python.org/downloads/windows/).
2. Procura a versão mais recente da série **Python 3.13** que disponibilize **Windows installer (64-bit)** e escolhe esse instalador, se o teu computador for Intel/AMD de 64 bits. A página pode mostrar versões de outras séries: a referência deste guia é 3.13.
3. Abre o instalador. Mantém o lançador Python selecionado e assinala **Add python.exe to PATH**, se essa opção aparecer.
4. Escolhe a instalação para o teu utilizador, quando disponível. Não desinstales outras versões de Python: podemos escolher a versão desejada pelo comando.
5. Fecha o instalador e abre uma nova janela de **PowerShell** através do menu Iniciar.

Escreve e prime Enter:

```powershell
py -3.13 --version
```

Deves obter uma versão que começa por `Python 3.13`. O comando `py` escolhe uma instalação de Python e `-3.13` indica a versão pretendida.

Se `py` não for reconhecido, fecha e volta a abrir o PowerShell. Se o problema continuar, volta ao instalador oficial e confirma que o lançador Python foi instalado. Se já tiveres Python 3.13, basta esta verificação; não precisas de o reinstalar.

## 4. Instalar o editor e o Git, se necessário

O Visual Studio Code já está instalado. Abre-o e, no painel de extensões, procura **Python**, publicado pela **Microsoft**, e instala essa extensão se ainda não existir.

Para alguém que siga este guia noutro computador e ainda não tenha o editor:

1. Abre a [página oficial do Visual Studio Code](https://code.visualstudio.com/download).
2. Escolhe o instalador Windows adequado ao teu computador. A instalação por utilizador, quando disponível, é suficiente.
3. Depois de instalar, abre o editor e instala a extensão **Python**, publicada pela **Microsoft**.

Para o Git:

Com o `winget`, executa:

```powershell
winget install --id Git.Git --exact --source winget
```

Ou instala através do site oficial:

1. Abre a [página oficial do Git para Windows](https://git-scm.com/downloads/win).
2. Descarrega o instalador adequado ao teu computador e usa as opções predefinidas.
3. Abre uma nova janela de PowerShell e verifica:

```powershell
git --version
```

O GitHub é o serviço online onde poderemos guardar o repositório. O Git é a ferramenta no computador que acompanha as alterações. Ainda não vamos publicar ficheiros nem configurar credenciais.

## 5. Descarregar e abrir o projeto

O repositório remoto começou vazio. Os passos seguintes só funcionam **depois de autorizares o envio do código e de esse envio estar concluído**. Preparar os ficheiros neste ambiente não significa que já estejam no GitHub.

1. Abre [o teu repositório no GitHub](https://github.com/gpraposo/chatgpt). Se o repositório for privado, inicia sessão na conta com acesso a ele.
2. Confirma que está selecionada a branch **main** e que aparecem `app.py` e `requirements.txt` na lista de ficheiros. Se o repositório ainda estiver vazio, o envio ainda não foi concluído.
3. Clica no botão verde **Code** e escolhe **Download ZIP**. O navegador descarrega normalmente um ficheiro chamado `chatgpt-main.zip`.
4. Cria uma pasta chamada **Projetos** dentro de **Documentos**.
5. Clica com o botão direito no ZIP e escolhe **Extrair Tudo**. Escolhe **Documentos\Projetos** como destino da extração.
6. Na pasta extraída, localiza a pasta **chatgpt-main** que contém diretamente `app.py` e `requirements.txt`. Renomeia essa pasta para **chatgpt**. O resultado deve ser **Documentos\Projetos\chatgpt\app.py**, com `requirements.txt` ao lado. Se a extração tiver criado duas pastas umas dentro das outras, usa a pasta interior que contém esses ficheiros.
7. No Visual Studio Code, escolhe **File → Open Folder** e abre a pasta `chatgpt`.

Os ficheiros são o código do projeto. Abrir a pasta no editor permite vê-los; ainda não executa a aplicação.

## 6. Criar um ambiente separado para o projeto

No PowerShell, entra na pasta do projeto:

```powershell
Set-Location (Join-Path ([Environment]::GetFolderPath('MyDocuments')) 'Projetos\chatgpt')
```

Este comando procura a tua pasta Documentos, incluindo quando está associada ao OneDrive. Se extraíste o projeto para outro local, entra nesse local. No editor também podes abrir **Terminal → New Terminal**; confirma que o terminal é PowerShell e que está na pasta com `requirements.txt`.

Cria o ambiente Python:

```powershell
py -3.13 -m venv .venv
```

Um **ambiente virtual** é uma pasta com um Python e bibliotecas dedicados a este projeto. Ajuda a evitar conflitos com outros trabalhos. A pasta chama-se `.venv` e não precisa de ser enviada para o GitHub.

Instala as bibliotecas:

```powershell
.\.venv\Scripts\python.exe -m pip install --require-hashes -r requirements.txt
```

O `pip` instala bibliotecas; `requirements.txt` identifica as versões usadas no projeto. `--require-hashes` verifica que os ficheiros descarregados correspondem aos identificadores de integridade guardados nessa lista. Espera até o comando terminar e o terminal voltar a aceitar instruções. Usa sempre a ligação normal e a verificação de certificados do instalador; não acrescentes opções para desativar a verificação HTTPS.

Não precisamos de ativar o ambiente com um script. Invocamos diretamente o Python da pasta `.venv`, evitando alterações à política de execução do Windows.

No Visual Studio Code, usa **Ctrl+Shift+P → Python: Select Interpreter** e escolhe o Python dentro de `.venv`, se quiseres que o editor também use esse ambiente.

## 7. Preparar os dados e iniciar o painel

Executa a preparação dos dados:

```powershell
.\.venv\Scripts\python.exe -m offshore_demo.pipeline
```

A **pipeline** é uma sequência de tarefas: recolhe os dados simulados, valida-os, prepara as tabelas e exporta os resultados. Uma linha de dados descreve uma unidade offshore num mês.

Verifica o projeto:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Este comando executa testes automáticos. Se todos passarem, termina com `OK`. Um teste não substitui a revisão do significado dos indicadores; ajuda a detetar erros na preparação e nos cálculos.

Inicia o painel:

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py
```

O Streamlit cria uma aplicação local e mostra um endereço no terminal, normalmente **http://localhost:8501**. Abre esse endereço no navegador. `localhost` significa o teu próprio computador; este passo não publica o painel na Internet.

Mantém o terminal aberto enquanto usas a aplicação. Para a parar, volta ao terminal e prime **Ctrl+C**. Da próxima vez, basta entrar na pasta e repetir o comando do Streamlit; só precisas de instalar as bibliotecas novamente se criares outro ambiente ou alterares os requisitos.

## 8. Criar uma versão no Power BI

Antes do Power BI, podes praticar SQL sem instalar outra ferramenta. Abre `sql\analysis.sql` no editor para ler as quatro consultas e executa-as com:

```powershell
.\.venv\Scripts\python.exe scripts\run_sql.py
```

O resultado aparece no terminal. A base de dados é aberta apenas para leitura; estudar as consultas não altera os dados. Podemos explicar cada consulta linha a linha depois de abrir o primeiro painel.

Instala o **Power BI Desktop** a partir da Microsoft Store ou dos links na [documentação oficial de instalação](https://learn.microsoft.com/en-us/power-bi/fundamentals/desktop-get-the-desktop). Evita instaladores de sites terceiros.

Depois de executar a pipeline:

1. Abre o Power BI Desktop.
2. Escolhe **Obter dados → Texto/CSV**.
3. Seleciona `data\processed\operations.csv` dentro da pasta do projeto.
4. Confirma que a pré-visualização mostra várias colunas. O separador do ficheiro é a vírgula e a codificação é UTF-8.
5. Escolhe **Transformar dados**. Dá à tabela o nome `operations`.
6. Mantém `month` como **Texto**: contém ano e mês, sem dia. `budget_eur`, `actual_eur` e as colunas de horas devem ser numéricas. `asset_id` e `asset_name` são texto.
7. Se os números com ponto decimal forem interpretados incorretamente, usa **Alterar tipo → Utilizar região** e escolhe o formato numérico **Inglês (Estados Unidos)** para as colunas numéricas. Isto afeta a leitura do CSV, não obriga a apresentar euros em formato americano.
8. Antes de fechar, escolhe **Adicionar coluna → Coluna personalizada**, dá-lhe o nome `DataMes` e usa esta fórmula para criar explicitamente o primeiro dia do mês:

```powerquery
Date.FromText([month] & "-01", [Format="yyyy-MM-dd", Culture="en-US"])
```

Define `DataMes` como tipo **Data**. Depois escolhe **Fechar e Aplicar**. Usa `DataMes` no eixo temporal dos gráficos; `month` continua útil como rótulo.

Cria estas **medidas**, uma de cada vez, em **Modelação → Nova medida**. Uma medida calcula um resultado para os filtros selecionados no relatório.

```dax
Orçamento EUR = SUM(operations[budget_eur])
```

```dax
Custo real EUR = SUM(operations[actual_eur])
```

```dax
Desvio EUR = [Custo real EUR] - [Orçamento EUR]
```

```dax
Desvio % = DIVIDE([Desvio EUR], [Orçamento EUR])
```

```dax
Horas de paragem =
    SUM(operations[planned_downtime_hours])
    + SUM(operations[unplanned_downtime_hours])
```

```dax
Disponibilidade % =
    DIVIDE(
        SUM(operations[period_hours]) - [Horas de paragem],
        SUM(operations[period_hours])
    )
```

As fórmulas usam vírgulas entre argumentos. Se o Power BI estiver configurado para usar separadores DAX locais e pedir outro separador, substitui essas vírgulas por ponto e vírgula.

Formata os valores EUR como moeda e as duas medidas `%` como percentagens. Não multipliques uma medida por 100 quando usas a formatação percentagem.

Nesta demonstração, **disponibilidade = horas sem paragem / horas do período**. Inclui paragens planeadas e não planeadas. É uma definição para este projeto: numa empresa real precisamos de acordar com operações quais as paragens incluídas e como tratar os períodos de referência.

Quando juntamos unidades e meses, somamos primeiro as horas e só depois calculamos a percentagem. Fazer a média simples das percentagens mensais daria o mesmo peso a períodos com durações diferentes e pode produzir um resultado errado.

Para a primeira página do relatório, acrescenta:

- Cartões para orçamento, custo real, desvio EUR e disponibilidade.
- Um gráfico de colunas com orçamento e custo real por unidade.
- Um gráfico de linhas com a disponibilidade por mês.
- Uma tabela com unidade, mês, desvio e horas de paragem.
- Filtros, ou **segmentações de dados**, para unidade e mês.

Um desvio positivo significa custo acima do orçamento; um valor negativo significa custo abaixo. A apresentação deve tornar este sentido claro. Não interpretes automaticamente uma poupança como melhoria: pode haver trabalho adiado ou uma redução da atividade.

Guarda o relatório como um ficheiro `.pbix` no teu computador. Esse ficheiro só existe depois de construíres e guardares o relatório no Power BI Desktop; a aplicação Python não gera um PBIX.

## 9. Se algo falhar

| Mensagem ou comportamento | Próximo passo |
| --- | --- |
| `py` não é reconhecido | Abre um novo PowerShell e confirma a instalação do lançador Python. |
| `No suitable Python runtime found` | Confirma que Python 3.13 está instalado; podes listar as instalações com `py -0p`. |
| `requirements.txt` não encontrado | Estás na pasta errada. Usa `Get-ChildItem` e entra na pasta que contém esse ficheiro. |
| Python dentro de `.venv` não encontrado | Confirma a pasta atual e volta a executar o comando que cria o ambiente virtual. |
| Erro de ligação ou certificado no `pip` | Guarda a mensagem e verifica a ligação, proxy ou certificados com a equipa de informática. Não desatives a verificação. |
| O terminal fica ocupado durante o painel | É esperado: o servidor está a correr. Abre outro terminal para novos comandos ou usa Ctrl+C para o parar. |
| A porta 8501 já está em uso | Usa `.\.venv\Scripts\python.exe -m streamlit run app.py --server.port 8502` e abre o endereço mostrado. |
| O Power BI mostra todos os dados numa coluna | Confirma o separador vírgula na importação. |
| Os números no Power BI parecem demasiado grandes ou pequenos | Revê os tipos e a região usada para interpretar o ponto decimal. |

Quando precisares de ajuda, partilha a mensagem de erro e o comando que a provocou. Oculta tokens, palavras-passe e outros dados privados antes de copiar uma imagem ou texto.

## Fontes e limites

- [Python: instalação e utilização no Windows](https://docs.python.org/3.13/using/windows.html)
- [Python: downloads oficiais para Windows](https://www.python.org/downloads/windows/)
- [Visual Studio Code: instalação no Windows](https://code.visualstudio.com/docs/setup/windows)
- [Git para Windows](https://git-scm.com/downloads/win)
- [Power BI Desktop: instalação oficial](https://learn.microsoft.com/en-us/power-bi/fundamentals/desktop-get-the-desktop)
- [Power BI: função DIVIDE](https://learn.microsoft.com/en-us/dax/divide-function-dax)

Não temos acesso ao teu computador Windows através deste ambiente na nuvem. A execução aqui valida a parte Python em Linux com Python 3.12; o código é compatível com 3.12/3.13, mas a instalação Windows e o relatório Power BI precisam de ser executados e verificados no teu computador. Os links acima são fontes oficiais; a consulta às páginas foi bloqueada pelo proxy deste ambiente durante a preparação, por isso os ecrãs atuais dos instaladores não foram confirmados.
