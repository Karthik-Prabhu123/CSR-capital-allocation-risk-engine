import streamlit as st
import sqlite3
import pandas as pd
import numpy as np
import plotly.express as px
import os
import pickle

from src.database import DB_NAME as DB_PATH, BASE_DIR

st.set_page_config(page_title="CSR Grant Optimization Platform", layout="wide")

st.title("💼 CSR Grant Optimization & Risk Analytics Platform")
st.markdown("### Algorithmic Capital Allocation Modeling and Resource Risk Auditing")
st.markdown("---")

@st.cache_data
def load_data():
    if not os.path.exists(DB_PATH):
        return None
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM optimized_allocation_matrix", conn)
    conn.close()
    return df

df = load_data()

if df is None:
    st.error("❌ Pre-processed master allocation matrix not found. Run pipeline file first.")
else:
    total_requested = df['requested_funding_inr'].sum()
    avg_score = df['allocation_priority_index'].mean()
    high_priority_count = len(df[df['allocation_priority_index'] > 65])
    
    k1, k2, k3 = st.columns(3)
    k1.metric("Total Funding Demands Audited", f"₹ {total_requested:,.2f}")
    k2.metric("Mean Capital Optimization Index", f"{avg_score:.1f} / 100")
    k3.metric("High-Impact Targets Isolated", f"{high_priority_count} Proposals")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🎯 Risk Profile vs Sustainability Score Deployment Funnel")
        selected_theme = st.selectbox("Filter Portfolio by Focus Area:", ["All Portfolio Categories"] + list(df['thematic_area'].unique()))
        
        plot_df = df if selected_theme == "All Portfolio Categories" else df[df['thematic_area'] == selected_theme]
        
        fig_scatter = px.scatter(
            plot_df, x="governance_risk_rating", y="allocation_priority_index",
            size="requested_funding_inr", color="thematic_area",
            title="Capital Allocation Matrix (Bubble Size represents Funding Request)",
            labels={"governance_risk_rating": "Internal Governance Risk Factor", "allocation_priority_index": "Priority Index Score"}
        )
        st.plotly_chart(fig_scatter, use_container_width=True)
        
    with col2:
        st.subheader("📊 Sector Capital Request Distribution")
        sector_totals = df.groupby('thematic_area')['requested_funding_inr'].sum().reset_index()
        
        fig_bar = px.bar(
            sector_totals, x="thematic_area", y="requested_funding_inr",
            color="thematic_area", title="Aggregated Active Capital Under Review by Focus Area",
            labels={"requested_funding_inr": "Cumulative Funding Demand (INR)", "thematic_area": "Focus Area Domain"}
        )
        st.plotly_chart(fig_bar, use_container_width=True)
        
    st.markdown("---")
    
    st.subheader("🧮 Ingestion Pipeline Priority Simulator")
    st.markdown("Evaluate inbound funding applications on the fly to simulate optimization score ratings via the live Ridge model.")
    
    m1, m2, m3, m4, m5 = st.columns(5)
    in_funding = m1.number_input("Requested Capital (INR)", 100000, 10000000, 2500000)
    in_years = m2.number_input("Track Record Longevity (Years)", 1, 20, 5)
    in_env = m3.slider("Environmental Score Metric", 0.0, 100.0, 75.0)
    in_soc = m4.slider("Social Efficacy Rating Index", 0.0, 100.0, 80.0)
    in_gov = m5.slider("Governance Risk Assessment (Lower Is Safer)", 0.0, 50.0, 15.0)
    
    try:
        model_path = os.path.join(BASE_DIR, "output", "allocation_regressor.pkl")
        with open(model_path, "rb") as f:
            model = pickle.load(f)
            
        input_vector = pd.DataFrame(
            [[float(in_funding), int(in_years), float(in_env), float(in_soc), float(in_gov)]], 
            columns=['requested_funding_inr', 'track_record_years', 'environmental_score', 'social_efficacy_score', 'governance_risk_rating']
        )
        
        predicted_index = float(model.predict(input_vector)[0])
        st.success(f"🔮 **Predictive Algorithmic Capital Deployment Priority Score Rating:** `{predicted_index:.2f} / 100`")
        
    except Exception as e:
        st.error(f"Error executing predictive scoring module equations: {str(e)}")