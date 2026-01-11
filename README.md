# Estimating the Causal Impact of Hurricane Otis in Acapulco

The final product of this project can be explored in [this app](https://jp-lopezesc-sc-acapulco-src02-app-cwqm2c.streamlit.app).

## Overview

The goal is to illustrate the application of a synthetic control method to evaluate the impact of the hurricane Otis on the economy of Acapulco. Otis was a powerful Category 5 hurricane that made landfall near Acapulco, Mexico, in October 2023, causing significant damage to the city.

While it is obvious that such a natural disaster would have a negative impact on the local economy, quantifying this impact is crucial for understanding the extent of the damage. These results can be used by policymakers, businesses, and aid organizations to make informed decisions regarding recovery efforts and resource allocation.

---

## Methodology: Synthetic control

The synthetic control method is a causal inference technique that is widely used in several fields including economics, marketing, and public policy. For instance, it can be used to assess the effect of a marketing campaign on sales, the impact of a new policy on economic indicators, or the influence of the introduction of a new product on market share.

In the synthetic control method, a treatment unit (e.g., a geographic location) is exposed to an intervention and the goal is to estimate what would have happened to that treatment unit if the intervention had not occurred. This is achieved by constructing a synthetic control unit, which is a weighted combination of control units (e.g., other geographic locations) that were not exposed to the intervention. The weights are chosen such that the synthetic control unit closely resembles the treatment unit in the pre-intervention period. By comparing the outcomes of the treatment unit and the synthetic control unit in the post-intervention period, we can estimate the causal effect of the intervention.

In this project, we used the [tfp-causalimpact](https://github.com/google/tfp-causalimpact) library to implement the synthetic control method.

---

## Data Source
The dataset used shows monthly transactions at point-of-sale terminals in Acapulco and other locations in Mexico from 2011 to 2025. This data can be used as a proxy of economic activity in the region, but it is important to note that it does not capture all economic activity, such as cash transactions or transactions in areas without point-of-sale terminals. However, it provides a useful indicator of trends in formal economic activity.
                
 Data source: [Banco de México](https://www.banxico.org.mx/SieInternet/consultarDirectorioInternetAction.do?sector=19&accion=consultarCuadro&idCuadro=CF660&locale=es).

---

## Repository Structure

```
sc_acapulco/
│
├── data/
│   ├── raw/                  # Original transaction data
│   └── processed/            # Cleaned and aggregated panel data
│
├── src/
│   ├── 01_clean_data.py      # Data cleaning and aggregation
│   └── 02_app.py             # Interactive Streamlit app
│ 
├── notebooks/
│   └── sc_application.ipynb  # Shows how the synthetic control is applied
│
├── setup_env.sh              # Contains the steps to create the environment used
├── requirements.txt          # Modules installed in the environment
├── README.md
└── .gitignore
```

---

## Results

Prior to the hurricane, the synthetic control closely matches Acapulco’s transaction trajectory, indicating a good pre-treatment fit. Immediately after the hurricane, observed transactions experience a sharp decline relative to the counterfactual. Moreover, observed transactions never converge back to the counterfactual, suggesting that, at least until June 2025, Acapulco continues to experience persistent economic effects from the hurricane.

Plots and results can be found in notebooks/sc_application.ipynb.

---

## Streamlit App

It can be of interest to see the impact over different time horizons after the hurricane, such as the immediate aftermath of the hurricane, as well as the longer-term effects on economic activity in Acapulco. I built a streamlit app to allow users to select different post-hurricane periods to analyze the impact over various time frames.

The code used to build the app is in src/02_app.py

---

## Assumptions and Limitations

* Synthetic Control assumes no other municipality was affected by the hurricane.
* It is also assumed that, in the absence of the intervention, the treated unit would have continued to follow the same relationship with the synthetic control observed in the pre-intervention period.
* We assume that the volume of point-of-sale (POS) transactions is a reasonable proxy for formal economic activity. However, this measure does not capture all economic activity, such as cash transactions or activity in areas without POS terminal coverage. As a result, economic recovery in Acapulco may have occurred through informal channels, which would not be reflected in the data used for this analysis.

---

*This project is intended only for educational and portfolio purposes.*
