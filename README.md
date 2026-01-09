# Estimating the Causal Impact of Otis on Card Transactions in Acapulco

## Overview

This project estimates the **causal impact of the introduction of Otis** on card transaction activity in **Acapulco**, Mexico. Using transaction-level data aggregated at the municipality–month level, I apply a **Synthetic Control** approach to construct a counterfactual trajectory for Acapulco in the absence of Otis.

The goal of the project is to demonstrate an **industry-relevant data science workflow**:

* Data cleaning and aggregation from raw transactional data
* Application of a causal inference model
* Clear visualization and interpretation of results
* Reproducible, well-documented code

The project is designed as a **portfolio-quality case study**, emphasizing modeling, analysis, and data visualization rather than purely predictive performance.

---

## Motivation

Understanding the impact of new payment terminals or financial infrastructure on local economic activity is a common problem in fintech and applied data science. Simple before–after comparisons can be misleading due to seasonality, macroeconomic trends, or regional shocks.

To address this, I use **Synthetic Control**, which allows us to:

* Compare Acapulco to a weighted combination of similar municipalities
* Control for time-varying confounders
* Estimate a transparent and interpretable counterfactual

---

## Data

### Source

The dataset consists of **card transaction records at payment terminals** across multiple municipalities in Mexico.

Each observation corresponds to a transaction and includes:

* Date
* Municipality
* Terminal identifier
* Transaction amount

### Processing

Raw transaction data are cleaned and aggregated into a **balanced panel**:

* **Unit**: Municipality
* **Time**: Month
* **Outcome**: Total transaction revenue per municipality per month

Only municipalities with sufficient pre-treatment history are included in the donor pool.

Raw data are stored in `data/raw/` and are never modified directly. Cleaned and aggregated data are written to `data/processed/`.

---

## Treatment Definition

* **Treated unit**: Acapulco
* **Intervention**: Introduction of Otis
* **Treatment date**: Defined as the month in which Otis becomes operational in Acapulco

Municipalities that did not receive Otis during the study period form the **donor pool** used to construct the synthetic control.

---

## Methodology

### Synthetic Control

Synthetic Control constructs a counterfactual outcome for the treated unit by selecting non-negative weights on control units that minimize pre-treatment discrepancy.

Formally, weights (w) are chosen to solve:

[
\min_w |Y_{\text{Acapulco}}^{\text{pre}} - Y_{\text{controls}}^{\text{pre}} w|^2
\quad \text{subject to } w_j \ge 0, ; \sum_j w_j = 1.
]

The resulting weighted combination of control municipalities represents the estimated outcome trajectory for Acapulco **had Otis not been introduced**.

### Implementation

* Data preparation and aggregation are handled in `01_clean_data.py`
* Synthetic Control is implemented using **PyMC**, enabling a probabilistic formulation and transparent assumptions
* Visualizations are produced using `matplotlib` (final figures) and `seaborn` (EDA)

---

## Repository Structure

```
portfolio-synthetic-control/
│
├── data/
│   ├── raw/                  # Original transaction data
│   └── processed/            # Cleaned and aggregated panel data
│
├── notebooks/
│   └── eda.ipynb             # Exploratory data analysis
│
├── src/
│   ├── 01_clean_data.py      # Data cleaning and aggregation
│   ├── 02_synthetic_control.py  # Synthetic control estimation (PyMC)
│   ├── 03_streamlit_app.py   # Interactive Streamlit dashboard
│   └── utils.py              # Helper functions
│
├── outputs/
│   ├── figures/              # Plots and visualizations
│   └── tables/               # Summary tables
│
├── requirements.txt
├── README.md
└── .gitignore
```

---

## Results

The synthetic control closely matches Acapulco’s transaction trajectory in the **pre-treatment period**, indicating a good counterfactual fit.

After the introduction of Otis, Acapulco’s observed transaction volume diverges from its synthetic counterpart, suggesting a **causal effect attributable to the intervention**.

Key outputs include:

* Actual vs. synthetic revenue time series
* Pre/post treatment gaps
* Summary statistics of estimated treatment effects

All figures are saved in `outputs/figures/`.

---

## Streamlit App

An interactive Streamlit app allows users to:

* Visualize actual vs. synthetic outcomes
* Zoom into pre- and post-treatment periods
* Inspect treatment effects over time

To run the app:

```bash
streamlit run src/03_streamlit_app.py
```

---

## Environment Setup

This project uses **Python 3.11** and a virtual environment.

```bash
python3 -m venv env_sc_acapulco
source env_sc_acapulco/bin/activate
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
python -m ipykernel install --user --name env_sc_acapulco --display-name "Python (sc_acapulco)"
```

---

## Assumptions and Limitations

* Synthetic Control assumes that a weighted combination of control municipalities can approximate Acapulco’s counterfactual trend
* Results depend on the quality of the donor pool and pre-treatment fit
* Spillover effects or contemporaneous shocks affecting Acapulco but not controls may bias estimates

These limitations are discussed explicitly to emphasize transparency and responsible causal interpretation.

---

## Next Steps

Potential extensions include:

* Placebo and permutation tests
* Alternative donor pool definitions
* Comparison with Difference-in-Differences
* Incorporation of additional covariates

---

## Author

Juan Pablo López Escamilla
M.S. in Statistics (Duke University)

---

*This project is intended for educational and portfolio purposes and does not represent a definitive policy evaluation.*
