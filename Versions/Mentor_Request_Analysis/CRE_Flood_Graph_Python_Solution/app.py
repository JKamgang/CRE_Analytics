"""
CRE Flood Graph — Interactive Streamlit Dashboard
===================================================
Main application entry point.  Run with:
    streamlit run app.py
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import logging
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

from config import (
    APP_TITLE, APP_ICON, DEFAULT_PAGE_LAYOUT,
    SECTORS, SECTOR_COLORS, FLOOD_COLOR_SCALE,
    DC_CONFIG, ATLANTA_CONFIG, MAPBOX_STYLE,
)
from utils.data_processor import (
    load_all_cities, generate_sample_data, get_summary_metrics,
    get_yearly_sector_summary, get_multifamily_deep_dive,
    compute_flood_intensity,
)

logging.basicConfig(level=logging.INFO, format="%(levelname)s | %(message)s")
logger = logging.getLogger(__name__)

# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  PAGE CONFIG                                                            ║
# ╚══════════════════════════════════════════════════════════════════════════╝
st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout=DEFAULT_PAGE_LAYOUT,
    initial_sidebar_state="expanded",
)

# Custom CSS
st.markdown("""
<style>
    .main .block-container { padding-top: 1rem; }
    div[data-testid="stMetricValue"] { font-size: 1.8rem; }
    h1 { color: #08306b; }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] {
        padding: 8px 20px;
        border-radius: 4px 4px 0 0;
    }
</style>
""", unsafe_allow_html=True)


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  DATA LOADING (cached)                                                  ║
# ╚══════════════════════════════════════════════════════════════════════════╝
@st.cache_data(ttl=3600, show_spinner="Fetching development pipeline data…")
def load_data(use_live: bool = True) -> pd.DataFrame:
    """Try live API first; fall back to sample data."""
    if use_live:
        try:
            df = load_all_cities(force_refresh=False)
            if not df.empty and len(df) > 5:
                return df
        except Exception as e:
            logger.warning("Live data fetch failed: %s — using sample data", e)
    return generate_sample_data()


# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  SIDEBAR                                                                ║
# ╚══════════════════════════════════════════════════════════════════════════╝
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/city-buildings.png", width=64)
    st.title("🌊 CRE Flood Graph")
    st.caption("Development Pipeline Visualizer")
    st.divider()

    data_source = st.radio(
        "Data source",
        ["Live API + Sample Fallback", "Sample Data Only"],
        index=0,
        help="Live API fetches from Open Data DC & Atlanta portals. Sample data is always available for demo.",
    )
    use_live = data_source == "Live API + Sample Fallback"

    if st.button("🔄 Refresh Data", use_container_width=True):
        st.cache_data.clear()

    st.divider()

    # Load data
    df_all = load_data(use_live=use_live)

    # City filter
    available_cities = sorted(df_all["city"].unique().tolist())
    city_labels = {"DC": "Washington, DC", "ATL": "Atlanta, GA"}
    selected_cities = st.multiselect(
        "Cities",
        available_cities,
        default=available_cities,
        format_func=lambda x: city_labels.get(x, x),
    )

    # Sector filter
    available_sectors = sorted(df_all["sector"].unique().tolist())
    selected_sectors = st.multiselect(
        "Sectors",
        available_sectors,
        default=available_sectors,
    )

    # Year range
    if "report_year" in df_all.columns and df_all["report_year"].notna().any():
        min_yr = int(df_all["report_year"].min())
        max_yr = int(df_all["report_year"].max())
        year_range = st.slider("Year range", min_yr, max_yr, (min_yr, max_yr))
    else:
        year_range = (2018, 2026)

    # Status filter
    available_statuses = sorted(df_all["status"].dropna().unique().tolist())
    if available_statuses:
        selected_statuses = st.multiselect(
            "Status",
            available_statuses,
            default=available_statuses,
        )
    else:
        selected_statuses = []

    st.divider()
    st.caption("Built for Project REAP · CoStar-Ready Architecture")
    st.caption("© 2026 Jean Baptiste K.")

# ── Apply filters ────────────────────────────────────────────────────────────
df = df_all.copy()
df = df[df["city"].isin(selected_cities)] if selected_cities else df
df = df[df["sector"].isin(selected_sectors)] if selected_sectors else df
if "report_year" in df.columns:
    df = df[(df["report_year"] >= year_range[0]) & (df["report_year"] <= year_range[1])]
if selected_statuses:
    df = df[df["status"].isin(selected_statuses)]

# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  HEADER                                                                 ║
# ╚══════════════════════════════════════════════════════════════════════════╝
st.title(f"{APP_ICON} {APP_TITLE}")
st.markdown(
    "Visualizing commercial real estate development growth over time — "
    "**the \"flood\" of development rising across the map.**"
)

# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  EXECUTIVE SUMMARY METRICS                                              ║
# ╚══════════════════════════════════════════════════════════════════════════╝
metrics = get_summary_metrics(df)
cols = st.columns(6)
cols[0].metric("Total Projects", f"{metrics['total_projects']:,}")
cols[1].metric("Total Sq Ft", f"{metrics['total_sqft']:,.0f}")
cols[2].metric("Total Units", f"{metrics['total_units']:,}")
cols[3].metric("Est. Value ($M)", f"${metrics['total_value_m']:,.1f}")
cols[4].metric("Sectors", metrics["sectors"])
cols[5].metric("Cities", metrics["cities"])

st.divider()

# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  TABS                                                                   ║
# ╚══════════════════════════════════════════════════════════════════════════╝
tab_flood, tab_geo, tab_trends, tab_mf, tab_data = st.tabs([
    "🌊 Flood Rising Map",
    "📍 Geointelligence Map",
    "📈 Time Series Trends",
    "🏢 Multifamily Deep-Dive",
    "📋 Data Explorer",
])

# ──────────────────────────────────────────────────────────────────────────
# TAB 1: ANIMATED FLOOD-RISING MAP
# ──────────────────────────────────────────────────────────────────────────
with tab_flood:
    st.subheader("🌊 Animated Flood-Rising Map")
    st.markdown(
        "Watch development activity **rise like a flood** across the map over time. "
        "Bubble size = square footage; color intensity = cumulative development level."
    )

    if df.empty:
        st.warning("No data to display. Adjust filters in the sidebar.")
    else:
        flood_df = compute_flood_intensity(df)
        flood_df = flood_df.dropna(subset=["latitude", "longitude", "report_year"])

        if not flood_df.empty:
            # Determine center based on selected cities
            if len(selected_cities) == 1 and selected_cities[0] == "DC":
                center = {"lat": DC_CONFIG["center_lat"], "lon": DC_CONFIG["center_lon"]}
                zoom = DC_CONFIG["default_zoom"]
            elif len(selected_cities) == 1 and selected_cities[0] == "ATL":
                center = {"lat": ATLANTA_CONFIG["center_lat"], "lon": ATLANTA_CONFIG["center_lon"]}
                zoom = ATLANTA_CONFIG["default_zoom"]
            else:
                center = {"lat": flood_df["latitude"].mean(), "lon": flood_df["longitude"].mean()}
                zoom = 5

            flood_df["report_year_int"] = flood_df["report_year"].astype(int)
            flood_df["sqft_display"] = flood_df["sqft"].apply(lambda x: f"{x:,.0f}" if pd.notna(x) else "N/A")
            flood_df["bubble_size"] = np.clip(flood_df["sqft"].fillna(0) / 5000, 3, 60)

            fig_flood = px.scatter_mapbox(
                flood_df.sort_values("report_year_int"),
                lat="latitude",
                lon="longitude",
                size="bubble_size",
                color="flood_level",
                color_continuous_scale=[c[1] for c in FLOOD_COLOR_SCALE],
                animation_frame="report_year_int",
                hover_name="project_name",
                hover_data={
                    "sector": True,
                    "city": True,
                    "sqft_display": True,
                    "status": True,
                    "flood_level": ":.2f",
                    "bubble_size": False,
                    "latitude": False,
                    "longitude": False,
                    "report_year_int": False,
                },
                labels={
                    "flood_level": "Flood Level",
                    "report_year_int": "Year",
                    "sqft_display": "Square Feet",
                },
                mapbox_style=MAPBOX_STYLE,
                zoom=zoom,
                center=center,
                height=650,
                opacity=0.75,
            )
            fig_flood.update_layout(
                margin={"r": 0, "t": 30, "l": 0, "b": 0},
                coloraxis_colorbar_title="Flood Level",
            )
            st.plotly_chart(fig_flood, use_container_width=True)

            # Flood level line chart
            flood_summary = (
                flood_df.groupby("report_year_int")
                .agg(cumulative_sqft=("sqft", "sum"), flood_level=("flood_level", "first"))
                .reset_index()
            )
            fig_level = go.Figure()
            fig_level.add_trace(go.Scatter(
                x=flood_summary["report_year_int"],
                y=flood_summary["flood_level"],
                mode="lines+markers",
                fill="tozeroy",
                fillcolor="rgba(8,48,107,0.15)",
                line=dict(color="#08306b", width=3),
                marker=dict(size=8),
                name="Flood Level",
            ))
            fig_level.update_layout(
                title="Development Flood Level Over Time (Cumulative)",
                xaxis_title="Year", yaxis_title="Flood Level (0–1)",
                height=350, template="plotly_white",
            )
            st.plotly_chart(fig_level, use_container_width=True)
        else:
            st.info("No geocoded records available for the flood map.")

# ──────────────────────────────────────────────────────────────────────────
# TAB 2: GEOINTELLIGENCE MAP
# ──────────────────────────────────────────────────────────────────────────
with tab_geo:
    st.subheader("📍 Geointelligence — Interactive Project Map")

    if df.empty:
        st.warning("No data to display. Adjust filters.")
    else:
        geo_df = df.dropna(subset=["latitude", "longitude"]).copy()
        if not geo_df.empty:
            geo_df["bubble_size"] = np.clip(geo_df["sqft"].fillna(0) / 8000, 4, 40)
            geo_df["sqft_display"] = geo_df["sqft"].apply(lambda x: f"{x:,.0f}" if pd.notna(x) else "N/A")
            geo_df["value_display"] = geo_df["est_value_millions"].apply(
                lambda x: f"${x:,.1f}M" if pd.notna(x) else "N/A"
            )

            if len(selected_cities) == 1 and selected_cities[0] == "DC":
                center = {"lat": DC_CONFIG["center_lat"], "lon": DC_CONFIG["center_lon"]}
                zoom = DC_CONFIG["default_zoom"]
            elif len(selected_cities) == 1 and selected_cities[0] == "ATL":
                center = {"lat": ATLANTA_CONFIG["center_lat"], "lon": ATLANTA_CONFIG["center_lon"]}
                zoom = ATLANTA_CONFIG["default_zoom"]
            else:
                center = {"lat": geo_df["latitude"].mean(), "lon": geo_df["longitude"].mean()}
                zoom = 5

            fig_geo = px.scatter_mapbox(
                geo_df,
                lat="latitude",
                lon="longitude",
                color="sector",
                color_discrete_map=SECTOR_COLORS,
                size="bubble_size",
                hover_name="project_name",
                hover_data={
                    "developer": True,
                    "sector": True,
                    "city": True,
                    "sqft_display": True,
                    "value_display": True,
                    "status": True,
                    "report_year": True,
                    "bubble_size": False,
                    "latitude": False,
                    "longitude": False,
                },
                labels={"sqft_display": "Sq Ft", "value_display": "Est. Value", "report_year": "Year"},
                mapbox_style=MAPBOX_STYLE,
                zoom=zoom,
                center=center,
                height=650,
                opacity=0.8,
            )
            fig_geo.update_layout(margin={"r": 0, "t": 30, "l": 0, "b": 0})
            st.plotly_chart(fig_geo, use_container_width=True)

            # Sector breakdown side-by-side
            col1, col2 = st.columns(2)
            with col1:
                sector_counts = geo_df["sector"].value_counts().reset_index()
                sector_counts.columns = ["sector", "count"]
                fig_pie = px.pie(
                    sector_counts, names="sector", values="count",
                    color="sector", color_discrete_map=SECTOR_COLORS,
                    title="Projects by Sector",
                    hole=0.4,
                )
                st.plotly_chart(fig_pie, use_container_width=True)

            with col2:
                sector_sqft = geo_df.groupby("sector")["sqft"].sum().reset_index()
                fig_bar = px.bar(
                    sector_sqft.sort_values("sqft", ascending=True),
                    x="sqft", y="sector", orientation="h",
                    color="sector", color_discrete_map=SECTOR_COLORS,
                    title="Total Square Footage by Sector",
                    labels={"sqft": "Square Feet"},
                )
                fig_bar.update_layout(showlegend=False)
                st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.info("No geocoded records available.")

# ──────────────────────────────────────────────────────────────────────────
# TAB 3: TIME SERIES TRENDS
# ──────────────────────────────────────────────────────────────────────────
with tab_trends:
    st.subheader("📈 Development Trends Over Time")

    if df.empty:
        st.warning("No data to display.")
    else:
        yearly = get_yearly_sector_summary(df)
        if not yearly.empty:
            # Area chart — projects by sector over time
            fig_area = px.area(
                yearly, x="report_year", y="projects", color="sector",
                color_discrete_map=SECTOR_COLORS,
                title="Number of Projects by Sector Over Time",
                labels={"report_year": "Year", "projects": "Projects"},
            )
            fig_area.update_layout(template="plotly_white", height=450)
            st.plotly_chart(fig_area, use_container_width=True)

            # Line chart — sqft by sector
            fig_line = px.line(
                yearly, x="report_year", y="total_sqft", color="sector",
                color_discrete_map=SECTOR_COLORS,
                title="Total Square Footage by Sector Over Time",
                labels={"report_year": "Year", "total_sqft": "Total Sq Ft"},
                markers=True,
            )
            fig_line.update_layout(template="plotly_white", height=450)
            st.plotly_chart(fig_line, use_container_width=True)

            # Stacked bar — value by sector
            fig_val = px.bar(
                yearly, x="report_year", y="total_value_m", color="sector",
                color_discrete_map=SECTOR_COLORS,
                title="Estimated Value ($M) by Sector Over Time",
                labels={"report_year": "Year", "total_value_m": "Value ($M)"},
                barmode="stack",
            )
            fig_val.update_layout(template="plotly_white", height=450)
            st.plotly_chart(fig_val, use_container_width=True)

            # City comparison
            if df["city"].nunique() > 1:
                st.subheader("City Comparison")
                city_yearly = (
                    df.groupby(["report_year", "city"])
                    .agg(projects=("project_name", "count"), total_sqft=("sqft", "sum"))
                    .reset_index()
                )
                col1, col2 = st.columns(2)
                with col1:
                    fig_cc = px.line(
                        city_yearly, x="report_year", y="projects", color="city",
                        title="Projects: DC vs Atlanta",
                        markers=True, labels={"report_year": "Year"},
                    )
                    fig_cc.update_layout(template="plotly_white", height=350)
                    st.plotly_chart(fig_cc, use_container_width=True)
                with col2:
                    fig_cs = px.line(
                        city_yearly, x="report_year", y="total_sqft", color="city",
                        title="Square Footage: DC vs Atlanta",
                        markers=True, labels={"report_year": "Year"},
                    )
                    fig_cs.update_layout(template="plotly_white", height=350)
                    st.plotly_chart(fig_cs, use_container_width=True)
        else:
            st.info("Not enough data for time series analysis.")

# ──────────────────────────────────────────────────────────────────────────
# TAB 4: MULTIFAMILY DEEP-DIVE
# ──────────────────────────────────────────────────────────────────────────
with tab_mf:
    st.subheader("🏢 Multifamily Deep-Dive")
    st.markdown(
        "Focused analysis of multifamily development — unit counts, "
        "density trends, and geographic distribution."
    )

    mf_df = get_multifamily_deep_dive(df)
    if mf_df.empty:
        st.warning("No multifamily records in current selection.")
    else:
        # KPIs
        mf_cols = st.columns(4)
        mf_cols[0].metric("MF Projects", f"{len(mf_df):,}")
        mf_cols[1].metric("Total Units", f"{int(mf_df['units'].sum()):,}")
        mf_cols[2].metric("Total Sq Ft", f"{int(mf_df['sqft'].sum()):,.0f}")
        mf_cols[3].metric("Avg Units/Project", f"{mf_df['units'].mean():,.0f}")

        st.divider()

        # Units over time
        mf_yearly = (
            mf_df.groupby("report_year")
            .agg(total_units=("units", "sum"), projects=("project_name", "count"),
                 total_sqft=("sqft", "sum"), avg_value=("est_value_millions", "mean"))
            .reset_index()
        )

        col1, col2 = st.columns(2)
        with col1:
            fig_mu = px.bar(
                mf_yearly, x="report_year", y="total_units",
                title="Multifamily Units Delivered/Planned by Year",
                labels={"report_year": "Year", "total_units": "Units"},
                color_discrete_sequence=["#2ca02c"],
            )
            fig_mu.update_layout(template="plotly_white", height=400)
            st.plotly_chart(fig_mu, use_container_width=True)

        with col2:
            fig_mp = px.line(
                mf_yearly, x="report_year", y="projects",
                title="Multifamily Project Count by Year",
                labels={"report_year": "Year", "projects": "Projects"},
                markers=True, color_discrete_sequence=["#2ca02c"],
            )
            fig_mp.update_layout(template="plotly_white", height=400)
            st.plotly_chart(fig_mp, use_container_width=True)

        # Map of MF projects
        mf_geo = mf_df.dropna(subset=["latitude", "longitude"])
        if not mf_geo.empty:
            mf_geo = mf_geo.copy()
            mf_geo["bubble"] = np.clip(mf_geo["units"].fillna(0) / 20, 5, 50)
            fig_mf_map = px.scatter_mapbox(
                mf_geo, lat="latitude", lon="longitude",
                size="bubble", color="city",
                hover_name="project_name",
                hover_data={"units": True, "sqft": True, "status": True, "bubble": False,
                            "latitude": False, "longitude": False},
                mapbox_style=MAPBOX_STYLE,
                zoom=5 if mf_geo["city"].nunique() > 1 else 11,
                center={"lat": mf_geo["latitude"].mean(), "lon": mf_geo["longitude"].mean()},
                title="Multifamily Projects Geographic Distribution",
                height=500, opacity=0.8,
            )
            fig_mf_map.update_layout(margin={"r": 0, "t": 40, "l": 0, "b": 0})
            st.plotly_chart(fig_mf_map, use_container_width=True)

        # Top MF projects table
        st.subheader("Top Multifamily Projects by Units")
        top_mf = (
            mf_df.nlargest(15, "units")[["project_name", "city", "neighborhood", "units", "sqft",
                                          "est_value_millions", "status", "report_year"]]
            .reset_index(drop=True)
        )
        top_mf.index += 1
        st.dataframe(top_mf, use_container_width=True)

# ──────────────────────────────────────────────────────────────────────────
# TAB 5: DATA EXPLORER
# ──────────────────────────────────────────────────────────────────────────
with tab_data:
    st.subheader("📋 Data Explorer")
    st.markdown("Browse, search, and export the full filtered dataset.")

    if df.empty:
        st.warning("No data available.")
    else:
        st.dataframe(
            df[["project_name", "city", "sector", "ward", "neighborhood",
                "developer", "status", "sqft", "units", "est_value_millions",
                "report_year"]].sort_values(["report_year", "city"], ascending=[False, True]),
            use_container_width=True,
            height=500,
        )

        # Download button
        csv_data = df.to_csv(index=False)
        st.download_button(
            "⬇️ Download Filtered Data as CSV",
            csv_data,
            file_name="cre_flood_graph_export.csv",
            mime="text/csv",
            use_container_width=True,
        )

        st.divider()

        # Quick stats
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("**Records by City**")
            st.dataframe(df["city"].value_counts().reset_index().rename(
                columns={"city": "City", "count": "Records"}
            ), hide_index=True)
        with col2:
            st.markdown("**Records by Sector**")
            st.dataframe(df["sector"].value_counts().reset_index().rename(
                columns={"sector": "Sector", "count": "Records"}
            ), hide_index=True)
        with col3:
            st.markdown("**Records by Status**")
            st.dataframe(df["status"].value_counts().reset_index().rename(
                columns={"status": "Status", "count": "Records"}
            ), hide_index=True)

# ── Footer ───────────────────────────────────────────────────────────────────
st.divider()
st.markdown(
    "<center><small>CRE Flood Graph v1.0 · Built for Project REAP · "
    "CoStar-Ready Architecture · Data: Open Data DC & City of Atlanta</small></center>",
    unsafe_allow_html=True,
)
