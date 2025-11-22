# 🗳️ Análise de Retweets - Eleições Brasileiras de 2022

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Concluído-success)

> Projeto de **Análise de Redes Sociais** focado na identificação de polarização política, bolhas de filtro e câmaras de eco durante a Eleição Presidencial Brasileira de 2022, utilizando grafos de interação de Retweets.

---

## 📖 Sobre o Projeto

Este repositório contém um pipeline completo para analisar a estrutura de comunidades políticas no Twitter/X. Ao processar um grafo de interações de retweet em larga escala, aplicamos diversos algoritmos de detecção de comunidades para revelar como os usuários se agrupam em torno de ideologias políticas.

**Principais Objetivos:**
-   Identificar comunidades políticas distintas (Esquerda, Direita, etc.).
-   Medir a polarização usando modularidade e condutância.
-   Visualizar "bolhas" onde a informação circula isoladamente.

## 📂 Estrutura do Projeto

O projeto está organizado da seguinte forma:

```
ARS_EP/
├── data/
│   ├── raw/            # Coloque seu dataset .gml aqui
│   └── processed/      # Grafos GCC gerados e caches
├── results/
│   ├── metrics/        # Arquivos JSON/CSV com desempenho dos algoritmos
│   ├── partitions/     # Arquivos CSV mapeando nós para comunidades
│   └── visual/         # Arquivos .gexf para visualização no Gephi
├── src/
│   ├── algorithms.py   # Implementações de detecção de comunidades
│   ├── data_loader.py  # Carregamento e pré-processamento de grafos
│   ├── main.py         # Execução principal do pipeline
│   └── metrics.py      # Cálculos de modularidade e métricas de bolha
└── requirements.txt    # Dependências Python
```

## 🚀 Começando

### 1. Pré-requisitos
-   Python 3.8 ou superior
-   `pip` (Gerenciador de Pacotes Python)

### 2. Instalação
Clone o repositório e instale as dependências:

```bash
git clone git@github.com:pabloassuncao/2022-Brazilian-Election-Retweet-Interaction-Analysis.git
cd 2022-Brazilian-Election-Retweet-Interaction-Analysis
pip install -r requirements.txt
```

### 3. Configuração do Dataset ⚠️ **IMPORTANTE**
O dataset **NÃO** está incluído neste repositório devido ao tamanho. Você deve baixá-lo manualmente:

1.  Acesse o **2022 Brazilian election Twitter dataset** no Mendeley: [Link para o Dataset](https://data.mendeley.com/datasets/x7ypgrzr3m/2)
2.  Baixe o arquivo `.gml` (ex: `eleicoes_2022.gml`).
3.  Coloque-o na pasta `data/raw/`.
4.  Certifique-se de que o nome do arquivo corresponda à configuração em `src/main.py` (padrão: `data/raw/eleicoes_2022.gml`).

### 4. Executando a Análise
Para rodar o pipeline completo (Carregar -> Detectar -> Medir -> Exportar):

```bash
python -m src.main
```

## ⚙️ Configuração (`src/main.py`)

Você pode personalizar a análise modificando as variáveis no topo de `src/main.py`:

| Variável | Descrição | Padrão |
| :--- | :--- | :--- |
| `ALGORITHMS_TO_RUN` | Lista de algoritmos para executar. Opções: `"louvain"`, `"leiden"`, `"label_propagation"`, `"greedy_modularity"`, `"hierarchical_greedy"`. | `["leiden"]` |
| `EXPORT_TOP_50K` | Se `True`, exporta um grafo com os top 50k nós (por grau) para visualização. | `True` |
| `TOP_50K_LIMIT` | Número de nós a incluir no grafo exportado para visualização. | `5000` |
| `USE_SUBGRAPH` | Se `True`, executa algoritmos em um subgrafo menor (útil para algoritmos lentos como Girvan-Newman). | `False` |
| `RAW_DATA_PATH` | Caminho para o arquivo `.gml` de entrada. | `"data/raw/eleicoes_2022.gml"` |

## 🧠 Algoritmos Implementados

Comparamos várias abordagens para detecção de comunidades:

| Algoritmo | Tipo | Melhor Para |
| :--- | :--- | :--- |
| **Louvain** | Otimização de Modularidade | Grandes redes, uso geral |
| **Leiden** | Otimização de Modularidade | Mais rápido, garante comunidades conectadas |
| **Label Propagation** | Difusão | Muito rápido, encontrar clusters locais densos |
| **Greedy Modularity** | Aglomerativo | Análise de estrutura hierárquica |
| **Hierarchical** | Híbrido (Coarsening) | Grafos massivos (reduz tamanho antes da detecção) |

## 📊 Guia de Visualização (Gephi)

O pipeline exporta arquivos `.gexf` para `results/visual/`. Siga estes passos exatos para obter visualizações de alta qualidade:

### Passo 1: Importação
1.  Abra o **Gephi**.
2.  Selecione **"Open Graph File"** (Abrir Arquivo de Grafo) e escolha um arquivo em `results/visual/` (ex: `leiden_top5000.gexf`).
3.  No relatório de importação, apenas clique em **"OK"**.

### Passo 2: Layout (Force Atlas 2)
Este algoritmo de layout simula repulsão física entre nós para revelar clusters.

1.  No painel **Layout** (geralmente à esquerda), selecione **"Force Atlas 2"**.
2.  **Configuração**:
    -   **Scaling** (Escala): Defina como `2.0` (ou maior se os nós estiverem muito próximos). Controla o espaçamento do grafo.
    -   **Gravity** (Gravidade): Mantenha o padrão (`1.0`).
    -   **Dissuade Hubs** (Dissuadir Hubs): ✅ **Marque isto**. Empurra nós de alto grau para a periferia, clarificando a estrutura.
    -   **LinLog Mode**: Opcional. Marque para formas mais agrupadas e menos "aracnídeas".
    -   **Prevent Overlap** (Evitar Sobreposição): ✅ **Marque isto**. Garante que os nós não fiquem uns sobre os outros.
3.  Clique em **"Run"** (Executar).
4.  Aguarde o grafo estabilizar (o movimento diminui), então clique em **"Stop"** (Parar).

### Passo 3: Aparência (Cor e Tamanho)
Colorir nós pela comunidade detectada para visualizar as "bolhas".

1.  No painel **Appearance** (Aparência) (geralmente à esquerda):
2.  **Cor (Ícone da Paleta de Pintura)**:
    -   Selecione **Nodes** (Nós).
    -   Selecione **Partition** (Partição) (não Unique ou Ranking).
    -   Escolha **"community"** no menu suspenso.
    -   Clique em **"Apply"** (Aplicar). (Você pode clicar no link "Palette" para mudar o esquema de cores).
3.  **Tamanho (Ícone de Círculos Concêntricos)**:
    -   Selecione **Nodes** (Nós).
    -   Selecione **Ranking**.
    -   Escolha **"degree"** (ou "Weighted Degree").
    -   Defina **Min size**: `10`, **Max size**: `50`.
    -   Clique em **"Apply"** (Aplicar).

### Passo 4: Exportação
1.  Vá para a aba **"Preview"** (Visualização) (barra superior).
2.  Em **Presets**, selecione **"Default Curved"**.
3.  Clique em **"Refresh"** (Atualizar) para renderizar a imagem final.
4.  Clique em **"Export"** (Exportar) (canto inferior esquerdo) para salvar como PNG, SVG ou PDF.

## 💻 Especificações de Hardware

Os resultados apresentados foram gerados utilizando o seguinte hardware:

-   **CPU**: AMD Ryzen 7 5800X 8-Core Processor
-   **RAM**: 16GB
-   **GPU**: RTX 3060 12GB
-   **SO**: Linux

---
*Desenvolvido para a disciplina de Análise de Redes Sociais.*
