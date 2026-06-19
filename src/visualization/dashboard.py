# src/visualization/dashboard.py
"""
Streamlit dashboard for ICES v2.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from src.models.ices_model import ICESModel
import time

st.set_page_config(page_title="ICES v2 Dashboard", layout="wide")

st.title("🏛️ ICES v2 Dashboard")
st.markdown("### Islamic Civilizational Economic Simulator")

# Sidebar
st.sidebar.header("Simulation Settings")

n_households = st.sidebar.slider("Number of Households", 20, 100, 60)
n_merchants = st.sidebar.slider("Number of Merchants", 10, 50, 20)
n_farmers = st.sidebar.slider("Number of Farmers", 10, 50, 20)

st.sidebar.subheader("Institutions")
use_zakat = st.sidebar.checkbox("Enable Zakat", value=True)
use_waqf = st.sidebar.checkbox("Enable Waqf", value=True)
use_crd = st.sidebar.checkbox("Enable CRD", value=True)

st.sidebar.subheader("Monetary System")
monetary_system = st.sidebar.selectbox("System", ["dinar", "fiat", "bitcoin"])

n_steps = st.sidebar.slider("Simulation Steps", 50, 500, 200)

if st.sidebar.button("▶️ Run Simulation"):
    with st.spinner("Running simulation..."):
        model = ICESModel(
            n_households=n_households,
            n_merchants=n_merchants,
            n_farmers=n_farmers,
            use_zakat=use_zakat,
            use_waqf=use_waqf,
            use_crd=use_crd,
            monetary_system=monetary_system,
            seed=42
        )
        df = model.run(n_steps)
        st.session_state.df = df
        st.session_state.config = {
            "n_households": n_households,
            "n_merchants": n_merchants,
            "n_farmers": n_farmers,
            "use_zakat": use_zakat,
            "use_waqf": use_waqf,
            "use_crd": use_crd,
            "monetary_system": monetary_system,
            "n_steps": n_steps
        }
    st.success(f"✅ Simulation completed! {n_steps} steps.")

# Display results
if "df" in st.session_state:
    df = st.session_state.df
    
    # Metrics
    st.subheader("📊 Civilization Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Civilization Index", f"{df['Civilization_Index'].iloc[-1]:.3f}", 
                  delta=f"{df['Civilization_Index'].iloc[-1] - df['Civilization_Index'].iloc[0]:.3f}")
    with col2:
        st.metric("Average Wealth", f"{df['Avg_Wealth'].iloc[-1]:.1f}")
    with col3:
        st.metric("Average Trust", f"{df['Avg_Trust'].iloc[-1]:.1f}")
    with col4:
        st.metric("Gini Coefficient", f"{df['Gini'].iloc[-1]:.3f}")
    
    # Time series
    st.subheader("📈 Time Series")
    
    metrics_to_plot = st.multiselect(
        "Select metrics to display",
        options=["Civilization_Index", "Avg_Wealth", "Avg_Trust", "Gini"],
        default=["Civilization_Index", "Gini"]
    )
    
    if metrics_to_plot:
        fig = px.line(
            df,
            x=df.index,
            y=metrics_to_plot,
            title="Civilization Metrics Over Time",
            labels={"index": "Step", "value": "Value"},
            color_discrete_map={
                "Civilization_Index": "blue",
                "Avg_Wealth": "green",
                "Avg_Trust": "red",
                "Gini": "orange"
            }
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Configuration
    with st.expander("⚙️ Configuration Details"):
        st.json(st.session_state.config)
    
    # Download
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Results (CSV)",
        data=csv,
        file_name="ices_simulation_results.csv",
        mime="text/csv"
    )

else:
    st.info("👈 Adjust settings and click 'Run Simulation' to begin.")
    
    # Show example
    st.subheader("📖 About ICES v2")
    st.markdown("""
    **ICES v2** is a calibrated agent-based computational laboratory for studying 
    how institutional portfolios shape long-run resilience, collapse, and attractor formation.
    
    **4-Layer Architecture:**
    1. **Agent Physics** - Households, merchants, farmers with endogenous morality
    2. **Economic Mechanisms** - Bimetallism, CRD, Islamic contracts
    3. **Institutions** - Zakat, Waqf, Hisba, Shura
    4. **Metrics** - Civilization Index, Wealth, Trust, Justice, Ecology
    
    **Key Features:**
    - Hierarchical Bayesian calibration
    - Global sensitivity analysis (Sobol)
    - Out-of-sample prediction
    - Falsifiability criteria
    """)
