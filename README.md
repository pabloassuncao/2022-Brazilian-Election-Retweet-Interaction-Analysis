# 🗳️ 2022 Brazilian Election Retweet Analysis

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Completed-success)

> **Social Network Analysis** project focused on identifying political polarization, filter bubbles, and echo chambers during the 2022 Brazilian Presidential Election using Retweet interaction graphs.

---

## 📖 About the Project

This repository contains a complete pipeline for analyzing the structure of political communities on Twitter/X. By processing a large-scale graph of retweet interactions, we apply various community detection algorithms to reveal how users cluster around political ideologies.

**Key Goals:**
-   Identify distinct political communities (Left, Right, etc.).
-   Measure polarization using modularity and conductance.
-   Visualize "bubbles" where information circulates in isolation.

## 📂 Project Structure

The project is organized as follows:

```
ARS_EP/
├── data/
│   ├── raw/            # Place your .gml dataset here
│   └── processed/      # Generated GCC graphs and caches
├── results/
│   ├── metrics/        # JSON/CSV files with algorithm performance
│   ├── partitions/     # CSV files mapping nodes to communities
│   └── visual/         # .gexf files for Gephi visualization
├── src/
│   ├── algorithms.py   # Community detection implementations
│   ├── data_loader.py  # Graph loading and preprocessing
│   ├── main.py         # Main pipeline execution
│   └── metrics.py      # Modularity and bubble metric calculations
└── requirements.txt    # Python dependencies
```

## 🚀 Getting Started

### 1. Prerequisites
-   Python 3.8 or higher
-   `pip` (Python Package Manager)

### 2. Installation
Clone the repository and install the dependencies:

```bash
git clone git@github.com:pabloassuncao/2022-Brazilian-Election-Retweet-Interaction-Analysis.git
cd 2022-Brazilian-Election-Retweet-Interaction-Analysis
pip install -r requirements.txt
```

### 3. Dataset Setup ⚠️ **IMPORTANT**
The dataset is **NOT** included in this repository due to size constraints. You must download it manually:

1.  Go to the **2022 Brazilian election Twitter dataset** on Mendeley: [Link to Dataset](https://data.mendeley.com/datasets/x7ypgrzr3m/2)
2.  Download the `.gml` file (e.g., `eleicoes_2022.gml`).
3.  Place it in the `data/raw/` folder.
4.  Ensure the filename matches the configuration in `src/main.py` (default: `data/raw/eleicoes_2022.gml`).

### 4. Running the Analysis
To run the full pipeline (Load -> Detect -> Measure -> Export):

```bash
python -m src.main
```

## ⚙️ Configuration (`src/main.py`)

You can customize the analysis by modifying the variables at the top of `src/main.py`:

| Variable | Description | Default |
| :--- | :--- | :--- |
| `ALGORITHMS_TO_RUN` | List of algorithms to execute. Options: `"louvain"`, `"leiden"`, `"label_propagation"`, `"greedy_modularity"`, `"hierarchical_greedy"`. | `["leiden"]` |
| `EXPORT_TOP_50K` | If `True`, exports a graph with the top 50k degree nodes for visualization. | `True` |
| `TOP_50K_LIMIT` | Number of nodes to include in the exported visualization graph. | `5000` |
| `USE_SUBGRAPH` | If `True`, runs algorithms on a smaller subgraph (useful for slow algorithms like Girvan-Newman). | `False` |
| `RAW_DATA_PATH` | Path to the input `.gml` file. | `"data/raw/eleicoes_2022.gml"` |

## 🧠 Implemented Algorithms

We compare multiple approaches to community detection:

| Algorithm | Type | Best For |
| :--- | :--- | :--- |
| **Louvain** | Modularity Optimization | Large networks, general purpose |
| **Leiden** | Modularity Optimization | Faster, guarantees connected communities |
| **Label Propagation** | Diffusion | Very fast, finding dense local clusters |
| **Greedy Modularity** | Agglomerative | Hierarchical structure analysis |
| **Hierarchical** | Hybrid (Coarsening) | Massive graphs (reduces size before detection) |

## 📏 Metrics Explained

The pipeline calculates several metrics to measure filter bubble strength and community isolation:

### Modularity
Measures how well-defined communities are. Higher values (0.3+) indicate strong community structure with more edges within communities than expected by chance.

### Community-Level Metrics

For each community with 10+ members, we calculate:

| Metric | Range | Interpretation |
| :--- | :--- | :--- |
| **Conductance** | 0.0 - 1.0 | **Lower = Stronger Bubble**. Measures the fraction of edges leaving the community. Low conductance (< 0.3) indicates an echo chamber where information rarely flows out. |
| **Internal Density** | 0.0 - 1.0 | **Higher = More Cohesive**. Measures how many possible connections within the community actually exist. High density (> 0.5) indicates tight-knit groups. |

### Network-Wide Metrics

To summarize the entire network:

-   **Weighted Avg Conductance**: Average conductance across all communities, weighted by community size. Larger communities have more influence on this value, providing a realistic measure of overall network isolation.
-   **Weighted Avg Internal Density**: Average internal density weighted by community size. Indicates overall network cohesion, with emphasis on larger communities that affect more users.

**Why Weighted?** A network with one large isolated bubble (1000 users) and many small open groups (10 users each) should reflect the isolation experienced by the majority. Weighted averages ensure larger communities appropriately influence the overall metric.

## 📊 Visualization Guide (Gephi)

The pipeline exports `.gexf` files to `results/visual/`. Follow these exact steps to achieve high-quality visualizations:

### Step 1: Import
1.  Open **Gephi**.
2.  Select **"Open Graph File"** and choose a file from `results/visual/` (e.g., `leiden_top5000.gexf`).
3.  In the import report, just click **"OK"**.

### Step 2: Layout (Force Atlas 2)
This layout algorithm simulates physical repulsion between nodes to reveal clusters.

1.  In the **Layout** pane (usually on the left), select **"Force Atlas 2"**.
2.  **Configuration**:
    -   **Scaling**: Set to `2.0` (or higher if nodes are too close). Controls the spread of the graph.
    -   **Gravity**: Keep default (`1.0`).
    -   **Dissuade Hubs**: ✅ **Check this**. Pushes high-degree nodes to the periphery, clarifying the structure.
    -   **LinLog Mode**: Optional. Check for more clustered, less "spidery" shapes.
    -   **Prevent Overlap**: ✅ **Check this**. Ensures nodes don't sit on top of each other.
3.  Click **"Run"**.
4.  Wait for the graph to stabilize (movement slows down), then click **"Stop"**.

### Step 3: Appearance (Color & Size)
Color nodes by their detected community to visualize the "bubbles".

1.  In the **Appearance** pane (usually on the left):
2.  **Color (Paint Palette Icon)**:
    -   Select **Nodes**.
    -   Select **Partition** (not Unique or Ranking).
    -   Choose **"community"** from the dropdown.
    -   Click **"Apply"**. (You can click the "Palette" link to change the color scheme).
3.  **Size (Concentric Circles Icon)**:
    -   Select **Nodes**.
    -   Select **Ranking**.
    -   Choose **"degree"** (or "Weighted Degree").
    -   Set **Min size**: `10`, **Max size**: `50`.
    -   Click **"Apply"**.

### Step 4: Export
1.  Go to the **"Preview"** tab (top bar).
2.  In **Presets**, select **"Default Curved"**.
3.  Click **"Refresh"** to render the final image.
4.  Click **"Export"** (bottom left) to save as PNG, SVG, or PDF.

## 💻 Hardware Specifications

The results presented were generated using the following hardware:

-   **CPU**: AMD Ryzen 7 5800X 8-Core Processor
-   **RAM**: 16GB
-   **GPU**: RTX 3060 12GB
-   **OS**: Linux

---
*Developed for the Social Network Analysis course.*
