import streamlit as st
import pandas as pd
import numpy as np
import tensorflow as tf
import causalimpact
import plotly.graph_objects as go

# ------------------------
# Page setup
# ------------------------
st.set_page_config(page_title="Impact of Hurricane Otis on Acapulco", layout="wide")
st.title("Impact of Hurricane Otis on Acapulco")

with st.info("About this app"):
    st.write(
    """
    ### What are we doing here?
    This app illustrates the application of a synthetic control method to evaluate the 
    impact of the hurricane Otis on the economy of Acapulco. Otis was a powerful Category 5
    hurricane that made landfall near Acapulco, Mexico, in October 2023, causing significant damage
    to the city.

    While it is obvious that such a natural disaster would have a negative impact on the local economy,
    quantifying this impact is crucial for understanding the extent of the damage. These results can be 
    used by policymakers, businesses, and aid organizations to make informed decisions regarding recovery
    efforts and resource allocation.

    It can be of interest to see the impact over different time horizons, such as the immediate aftermath
    of the hurricane, as well as the longer-term effects on economic activity in Acapulco. This app allows
    users to select different post-hurricane periods to analyze the impact over various time frames.
    """)

with st.expander("About the synthetic control method"):
    st.markdown("""
    The synthetic control method  is a causal inference technique that is widely used in several fields 
    including economics, marketing, and public policy. For instance, it can be used to assess the effect 
    of a marketing campaign on sales, the impact of a new policy on economic indicators, or the influence 
    of the introduction of a new product on market share.

    In the synthetic control method, a treatment unit (e.g., a geographic location) is
    exposed to an intervention and the goal is to estimate what would have happened to that treatment unit
    if the intervention had not occurred. This is achieved by constructing a synthetic control unit,
    which is a weighted combination of control units (e.g., other geographic locations) that were
    not exposed to the intervention. The weights are chosen such that the synthetic control unit closely
    resembles the treatment unit in the pre-intervention period. By comparing the outcomes of the treatment 
    unit and the synthetic control unit in the post-intervention period, we can estimate the causal effect 
    of the intervention.
                
    In this project, we used the [tfp-causalimpact](https://github.com/google/tfp-causalimpact) library to
    implement the synthetic control method.
    """)

# ------------------------
# Load cleaned transactions data
# ------------------------
@st.cache_data
def load_data():
    # Ensure this path matches your file structure
    df = pd.read_csv("data/processed/transactions_clean.csv")
    df["Date"] = pd.to_datetime(df["Date"])
    df = df.set_index("Date")
    return df
    
try:
    df = load_data()

    # Add a descriptive block
    with st.expander("Data Overview"):
        st.markdown("""
        The dataset used shows monthly transactions at point-of-sale terminals in Acapulco and other locations in Mexico 
        from 2011 to 2025.
        This data can be used as a proxy of economic activity in the region, but it is important to note that it does not
        capture all economic activity, such as cash transactions or transactions in areas without point-of-sale terminals.
        However, it provides a useful indicator of trends in formal economic activity.
                 
        * **Target:** Transactions in Acapulco de Juárez.
        * **Controls:** Transactions in other locations unaffected by the hurricane, used to predict the counterfactual 
                    (what would have happened without the hurricane).
        * **Frequency:** Monthly data.
                
        Data source: [Banco de México](https://www.banxico.org.mx/SieInternet/consultarDirectorioInternetAction.do?sector=19&accion=consultarCuadro&idCuadro=CF660&locale=es).
        """)
        # Display the data with a better UI than st.write
        st.dataframe(df, use_container_width=True)

except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()

# ------------------------
# Sidebar: Post period selection
# ------------------------
with st.sidebar:
    
    pre_start_val = pd.to_datetime('2011-04-11')
    pre_end_val = pd.to_datetime('2023-09-01')
    st.header("Analysis Period")

    # 1. Select Post-Period (Input)
    st.info("The hurricane occurred in October 2023. Please select a post-hurricane period to analyze its impact on Acapulco’s transactions. " \
    "The synthetic control model will use data prior to October 2023 to construct a counterfactual scenario for the selected post-hurricane period.")
    post_start = st.date_input(
        "Analysis period start",
        value=pd.to_datetime('2023-10-01'),
        min_value=pd.to_datetime('2023-10-01'),
        max_value=pd.to_datetime('2025-06-01')
    )
    
    post_end = st.date_input(
        "Analysis period end",
        value=pd.to_datetime('2025-06-01'),
        min_value=pd.to_datetime('2023-11-01'),
        max_value=pd.to_datetime('2025-06-01')
    )

    # Formalize the periods for CausalImpact
    post_period = (pd.to_datetime(post_start), pd.to_datetime(post_end))
    pre_period = (pre_start_val, pre_end_val)

    st.divider()

    # 2. Custom Styled Button
    st.markdown("""
        <style>
        /* Target the button specifically in the sidebar */
        section[data-testid="stSidebar"] div.stButton > button {
            width: 100%;
            height: 3.5em;
            background-color: #FF6600;
            color: white;
            font-size: 18px;
            font-weight: bold;
            border-radius: 10px;
            border: none;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
            transition: all 0.3s ease;
        }
        section[data-testid="stSidebar"] div.stButton > button:hover {
            background-color: #FF8533;
            transform: translateY(-2px);
            box-shadow: 0 6px 12px rgba(255, 102, 0, 0.4);
            color: white;
        }
        section[data-testid="stSidebar"] div.stButton > button:active {
            transform: translateY(0);
        }
        </style>
    """, unsafe_allow_html=True)

    run_analysis = st.button("🚀 Run Synthetic Control")

# ------------------------
# Helper to plot CI correctly
# ------------------------
def add_ci_band(fig, x, mean, lower, upper, color, name):
    """
    Plot mean line and confidence interval band.
    Filtering the data before passing it here prevents 'triangle' artifacts.
    """
    # Lower bound (invisible)
    fig.add_trace(go.Scatter(
        x=x, y=lower,
        line=dict(color='rgba(0,0,0,0)'),
        showlegend=False,
        hoverinfo='skip',
        connectgaps=False
    ))
    # Upper bound (fill to previous)
    fig.add_trace(go.Scatter(
        x=x, y=upper,
        fill='tonexty',
        fillcolor=color,
        line=dict(color='rgba(0,0,0,0)'),
        showlegend=False,
        hoverinfo='skip',
        connectgaps=False
    ))
    # Mean line
    fig.add_trace(go.Scatter(
        x=x, y=mean,
        line=dict(color=color.replace('0.2','1.0'), width=2),
        name=name,
        connectgaps=False
    ))

# ------------------------
# Run CausalImpact
# ------------------------
if run_analysis:
    # Set global seeds for reproducibility
    seed = 0
    np.random.seed(seed)
    tf.random.set_seed(seed)

    with st.spinner("Running causalimpact Model..."):
        try:
            impact = causalimpact.fit_causalimpact(df, pre_period, post_period)
            series = impact.series
            # Create a specific slice for the post-period to fix the "triangle" fill bug
            post_series = series.loc[post_start:]

            # Extract values from the summary dataframe
            summary_df = impact.summary

            # Total transactions observed 
            total_observed = summary_df.loc['cumulative', 'actual'] 
            # Total transactions predicted (counterfactual)
            total_predicted = summary_df.loc['cumulative', 'predicted']
            # Cumulative absolute effect (The total loss)
            total_loss = summary_df.loc['cumulative', 'abs_effect']
            # Total transactions observed 
            avg_observed = summary_df.loc['average', 'actual'] 
            # Total transactions predicted (counterfactual)
            avg_predicted = summary_df.loc['average', 'predicted']
            # Cumulative absolute effect (The total loss)
            avg_loss = summary_df.loc['average', 'abs_effect']
            # Relative effect (The percentage)
            pct_impact = summary_df.loc['average', 'rel_effect'] * 100
            # P-value for significance
            p_val = summary_df.loc['average', 'p_value']

            st.write("### Key results")

            m1, m2, m3 = st.columns(3)
            with m1:
                st.metric(label="Monthly Average Observed Transactions", 
                          value=f"{avg_observed/1e6:.2f}M",
                          help="Monthly average observed transactions during the selected post-hurricane period")

            with m2:
                st.metric(label="Monthly Average Counterfactual Transactions", 
                          value=f"{avg_predicted/1e6:.2f}M",
                          help="Predicted monthly average transactions if the hurricane had not occurred and its 95% interval")
                st.caption(f"95% Interval: ({summary_df.loc['average', 'predicted_lower']/1e6:.2f}M, {summary_df.loc['average', 'predicted_upper']/1e6:.2f}M)")

            with m3:
                st.metric(label="Monthly Averge Transaction Impact", 
                          value=f"{avg_loss/1e6:.2f}M",
                          help="Average monthly volume difference between observed and counterfactual transactions during the selected post-hurricane period and its 95% interval")
                st.caption(f"95% Interval: ({summary_df.loc['average', 'abs_effect_lower']/1e6:.2f}M, {summary_df.loc['average', 'abs_effect_upper']/1e6:.2f}M)")

            m1, m2, m3 = st.columns(3)
            with m1:
                st.metric(label="Total Observed Transactions", 
                          value=f"{total_observed/1e6:.2f}M",
                          help="Total observed transactions during the selected post-hurricane period")

            with m2:
                st.metric(label="Total Counterfactual Transactions", 
                          value=f"{total_predicted/1e6:.2f}M",
                          help="Predicted total transactions during the selected post-hurricane period if the hurricane had not occurred and its 95% interval")
                st.caption(f"95% Interval: ({summary_df.loc['cumulative', 'predicted_lower']/1e6:.2f}M, {summary_df.loc['cumulative', 'predicted_upper']/1e6:.2f}M)")

            with m3:
                st.metric(label="Total Transaction Impact", 
                          value=f"{total_loss/1e6:.2f}M",
                          help="Total volume difference between observed and counterfactual transactions during the selected post-hurricane period and its 95% interval")
                st.caption(f"95% Interval: ({summary_df.loc['cumulative', 'abs_effect_lower']/1e6:.2f}M, {summary_df.loc['cumulative', 'abs_effect_upper']/1e6:.2f}M)")


            m1, m2, m3 = st.columns(3)
            with m1:
                st.metric(
                    label="Relative Impact on transactions", 
                    value=f"{pct_impact:.2f}%", 
                    help="Relative difference between observed and counterfactual transactions during the selected post-hurricane period")
                st.caption(f"95% Interval: ({summary_df.loc['cumulative', 'rel_effect_lower']*100:.2f}%, {summary_df.loc['cumulative', 'rel_effect_upper']*100:.2f}%)")
                

            with m2:
                st.metric(
                    label="P-value", 
                    value=f"{p_val:.4f}", 
                    help="The bayesian p-value quantifies the probability that the counterfactual model would generate an outcome as extreme as the one observed."
                )

            # Place the detailed explanation in a full-width box immediately below the metrics
            st.markdown("---")
            if p_val < 0.05:
                st.success(f"✅ **Conclusion:** There is **strong evidence** of a causal impact of the hurricane Otis on transactions in Acapulco during the selected post-hurricane period (p={p_val:.3f}).")
            else:
                st.warning(f"⚠️ **Conclusion:** There is **no strong evidence** of a causal impact of the hurricane Otis on transactions in Acapulco during the selected post-hurricane period (p={p_val:.3f}). The observed changes could be due to random fluctuations.") 
            
            st.divider()

            # --- Plot 1: Observed vs Posterior ---
            st.subheader("1. Observed vs. Counterfactual")
            with st.info("plot 1"):
                st.write(
                """
                This plot shows the observed transactions in Acapulco (white line) against the counterfactual
                predictions (blue line) generated by the synthetic control model, allowing you to see how the 
                observed data diverges from the counterfactual after Hurricane Otis. The counterfactual shows what
                would have been expected if Hurricane Otis had not occurred. The vertical dashed red line marks the 
                month of the hurricante, while the yellow dashed lines mark the start and end of the analyzed post-hurricane 
                period.
                """)
            fig1 = go.Figure()
            add_ci_band(fig1, series.index, series['posterior_mean'],
                        series['posterior_lower'], series['posterior_upper'],
                        color='rgba(0,123,255,0.2)', name='Counterfactual')
            fig1.add_trace(go.Scatter(
                x=series.index, 
                y=series['observed'],
                mode='lines', 
                line=dict(color='white', width=2), 
                name='Observed'
            ))
            fig1.add_vline(x=post_start, line=dict(color='#FFFF00', dash='dash', width=1.5))
            fig1.add_vline(x=post_end, line=dict(color='#FFFF00', dash='dash', width=1.5))
            fig1.add_vline(x='2023-10-01', line=dict(color="#FF0000", dash='dash', width=1.5))
            fig1.update_layout(
                template="plotly_dark", 
                xaxis_title="Date", 
                yaxis_title="Transactions", 
                hovermode="x unified",
                legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01)
            )

            st.plotly_chart(fig1, use_container_width=True)

            # --- Plot 2: Point Effects ---
            st.subheader("2. Impact per month")
            with st.info("plot 2"):
                st.write(
                """
                This plot shows the estimated transaction loss per month caused by Hurricane Otis.
                """)
            fig2 = go.Figure()
            # ONLY use post_series to prevent the triangle artifact
            add_ci_band(fig2, post_series.index, post_series['point_effects_mean'],
                        post_series['point_effects_lower'], post_series['point_effects_upper'],
                        color='rgba(40,167,69,0.2)', name='Point Effect')
            fig2.add_hline(y=0, line=dict(color='black', width=1))
            fig2.update_layout(xaxis_title="Date", yaxis_title="Effect Size", hovermode="x unified")
            st.plotly_chart(fig2, use_container_width=True)

            # --- Plot 3: Cumulative Effects ---
            st.subheader("3. Cumulative Impact")
            with st.info("plot 3"):
                st.write(
                """
                This plot shows the estimated cumulative transaction loss caused by Hurricane Otis.
                """)
            fig3 = go.Figure()
            # ONLY use post_series to prevent the triangle artifact
            add_ci_band(fig3, post_series.index, post_series['cumulative_effects_mean'],
                        series.loc[post_start:, 'cumulative_effects_lower'], 
                        series.loc[post_start:, 'cumulative_effects_upper'],
                        color='rgba(255,193,7,0.2)', name='Cumulative Effect')
            fig3.add_hline(y=0, line=dict(color='black', width=1))
            fig3.update_layout(xaxis_title="Date", yaxis_title="Cumulative Effect", hovermode="x unified")
            st.plotly_chart(fig3, use_container_width=True)

        except Exception as e:
            st.error(f"An error occurred during modeling: {e}")

else:
    st.info("Adjust the dates in the sidebar and click 'Run Causal Impact Analysis' to start.")