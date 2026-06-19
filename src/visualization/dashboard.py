# src/visualization/dashboard.py
"""
Streamlit dashboard for ICES v2.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from src.models.ices_model import MinimalICESModel

st.set_page_config(page_title="ICES v2 Dashboard", layout="wide")

st.title("🏛️ ICES v2 Dashboard")
st.markdown("Islamic Civilizational Economic Simulator")

# Sidebar
st.sidebar.header("Simulation Settings")
n_agents = st.sidebar.slider("Number of Agents", 10, 100, 50)
use_zakat = st.sidebar.checkbox("Enable Zakat", value=True)
use_waqf = st.sidebar.checkbox("Enable Waqf", value=True)
use_crd = st.sidebar.checkbox("Enable CRD", value=True)
monetary_system = st.sidebar.selectbox("Monetary System", ["dinar", "fiat"])
n_steps = st.sidebar.slider("Steps", 10, 200, 100)

if st.sidebar.button("Run Simulation"):
    with st.spinner("Running simulation..."):
        model = MinimalICESModel(
            n_agents=n_agents,
            use_zakat=use_zakat,
            use_waqf=use_waqf,
            use_crd=use_crd,
            monetary_system=monetary_system
        )
        df = model.run(n_steps)
        st.session_state.df = df

if "df" in st.session_state:
    st.subheader("Simulation Results")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Final Avg Wealth", f"{st.session_state.df['Avg_Wealth'].iloc[-1]:.1f}")
    with col2:
        st.metric("Final Avg Trust", f"{st.session_state.df['Avg_Trust'].iloc[-1]:.1f}")
    with col3:
        st.metric("Final Gini", f"{st.session_state.df['Gini'].iloc[-1]:.3f}")
    
    fig = px.line(
        st.session_state.df,
        x=st.session_state.df.index,
        y=["Avg_Wealth", "Avg_Trust", "Gini"],
        title="Civilization Metrics Over Time"
    )
    st.plotly_chart(fig, use_container_width=True)
