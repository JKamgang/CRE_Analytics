import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import json
import os
from src.shared.utils.data_processor import load_all_cities
from src.features.growth_status.calculator import GrowthStatusCalculator
from src.shared.monetization.framework import MonetizationTier
from src.widgets.report_builder.generator import ReportBuilder

def main():
    st.header("🌍 Growth Dynamics — Interactive Geospatial Center")

    tier = st.session_state.get('tier', MonetizationTier.FREE)

    # 1. Configuration & Engine Choice
    with st.sidebar:
        st.header("🗺️ GIS Configuration")
        engine = st.selectbox(
            "Mapping Engine",
            ["Leaflet + OpenStreetMap (OSM)", "MapLibre GL", "QGIS Desktop Bridge"],
            help="Select the geospatial rendering engine."
        )

        st.divider()
        st.header("🎨 Temporal Colors")
        past_color = st.color_picker("Past Year Color", "#9E9E9E")  # Ghost Gray
        present_color = st.color_picker("Current Year Color", "#FF5252")  # Pulse Red
        future_color = st.color_picker("Future Year Color", "#2196F3")  # Horizon Blue

        st.divider()
        st.header("🫧 Bubble Settings")
        bubble_var = st.radio(
            "Bubble Size Variable",
            ["Project Count", "Total Sqft", "Est. Value ()"]
        )

        view_mode = st.radio("View Mode", ["Exact Points", "Aggregated Clustering"])

    # 2. Load Data
    df_raw = load_all_cities()
    if df_raw.empty:
        st.warning("No data available to visualize.")
        return

    calc = GrowthStatusCalculator()
    df = calc.calculate_growth_metrics(df_raw)

    # 3. Temporal Control
    min_year = int(df['report_year'].min()) if 'report_year' in df.columns and not df['report_year'].isna().all() else 2010
    max_year = int(df['report_year'].max()) if 'report_year' in df.columns and not df['report_year'].isna().all() else 2030
    current_year = st.slider("🕰️ Temporal Controller", min_year, max_year, 2024)

    # 4. Data Processing for Map
    df_map = df.copy()

    # Color logic: past, present, future
    def get_temporal_cat(year):
        if year < current_year: return "Past"
        if year == current_year: return "Present"
        return "Future"

    df_map['temporal_category'] = df_map['report_year'].apply(get_temporal_cat)

    if view_mode == "Aggregated Clustering":
        # Aggregate by City and Ward for simulation of clustering
        agg_cols = ['city', 'ward', 'temporal_category', 'growth_status']
        df_map = df_map.groupby(agg_cols).agg({
            'latitude': 'mean',
            'longitude': 'mean',
            'sqft': 'sum',
            'est_value_millions': 'sum',
            'project_name': 'count'
        }).reset_index()
        df_map.rename(columns={'project_name': 'project_count'}, inplace=True)
        hover_name = "city"
    else:
        df_map['project_count'] = 1
        hover_name = "project_name"

    # Size logic
    if bubble_var == "Project Count":
        df_map['bubble_size'] = df_map['project_count'] * 10
    elif bubble_var == "Total Sqft":
        df_map['bubble_size'] = df_map['sqft'].fillna(0) / 5000
    else:
        df_map['bubble_size'] = df_map['est_value_millions'].fillna(0) * 5

    df_map['bubble_size'] = np.clip(df_map['bubble_size'], 8, 60)

    # Rendering
    mapbox_style = "carto-positron" if "OSM" in engine else "dark"

    fig = px.scatter_mapbox(
        df_map,
        lat="latitude",
        lon="longitude",
        size="bubble_size",
        color="temporal_category",
        color_discrete_map={
            "Past": past_color,
            "Present": present_color,
            "Future": future_color
        },
        hover_name=hover_name,
        hover_data=["city", "growth_status", "project_count"] if view_mode == "Aggregated Clustering" else ["city", "sector", "report_year", "growth_status"],
        mapbox_style=mapbox_style,
        zoom=10,
        height=600
    )

    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    st.plotly_chart(fig, use_container_width=True)

    # Export options for paid users
    if tier != MonetizationTier.FREE:
        col_ex1, col_ex2 = st.columns(2)
        with col_ex1:
            st.download_button("💾 Export Map as HTML", data="<html></html>", file_name="growth_map.html")
        with col_ex2:
            if engine == "QGIS Desktop Bridge":
                rb = ReportBuilder()
                rb.export_qgis_script()

    # 5. Legend / Symbology Panel
    st.divider()
    col_l1, col_l2 = st.columns([2, 1])
    with col_l1:
        st.subheader("📊 Legend & Symbology")
        st.write(f"**Active Time Period:** {current_year}")
        st.latex(r"Z = \frac{x - \mu}{\sigma}")
        st.markdown(f"""
        - <span style='color:{past_color}'>●</span> **Past Year Color:** {past_color} (Growth already delivered)
        - <span style='color:{present_color}'>●</span> **Current Year Color:** {present_color} (Active construction/permits)
        - <span style='color:{future_color}'>●</span> **Future Year Color:** {future_color} (Projected horizon)
        """, unsafe_allow_html=True)

        st.info(f"**Growth Dynamics Mode:** Tracking Increase (Z>1), Stagnation (-1 to 1), and Decline (Z<-1)")

    with col_l2:
        if tier != MonetizationTier.FREE:
            rb = ReportBuilder()
            rb.render_ui()
        else:
            st.info("💡 Pro Tier unlocked: Branded PDF Report Builder & QGIS Desktop Bridge.")

if __name__ == "__main__":
    main()
