import streamlit as st
import os
import sys

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))

from src.shared.config.settings import APP_TITLE, APP_ICON
from src.pages import geo_viz, contact
from src.shared.monetization.framework import MonetizationTier

# ╔══════════════════════════════════════════════════════════════════════════╗
# ║  PAGE CONFIG                                                            ║
# ╚══════════════════════════════════════════════════════════════════════════╝
st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout="wide",
)

def main():
    st.sidebar.title("Alile Group")
    st.sidebar.image("https://img.icons8.com/fluency/96/city-buildings.png", width=64)

    # Tier Management
    if 'tier' not in st.session_state:
        st.session_state.tier = MonetizationTier.FREE

    tier_choice = st.sidebar.selectbox("Current Tier", [MonetizationTier.FREE, MonetizationTier.PRO, MonetizationTier.ENTERPRISE])
    st.session_state.tier = MonetizationTier(tier_choice)

    st.sidebar.divider()

    page = st.sidebar.selectbox("Navigate", ["Home", "Growth Dynamics Map", "Contact & Feedback"])

    if page == "Home":
        st.title(f"🚀 {APP_TITLE}")
        st.markdown("### Evolving from 'Growth' to 'Growth Dynamics'")
        st.write("Welcome to the next generation of CRE analytics. Our system now tracks capital 'increase', 'stagnation', and 'decline' using real-time ArcGIS data.")

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Growth Velocity", "+12.5%", delta="+2.1%")
        with col2:
            st.metric("Total Market Value", ".2B", delta="50M")
        with col3:
            st.metric("Active Projects", "154", delta="+12")

        st.divider()
        st.subheader("Key Innovation: Growth Status Logic")
        st.write("Using Z-Score normalization to categorize development intensity:")
        st.info("- **Increase ( > 1$):** High capital absorption and rapid growth.")
        st.warning("- **Stagnation (himBHs1 \le Z \le 1$):** Stable market with average permit volume.")
        st.error("- **Decline ( < -1$):** Significant reduction in project velocity.")

    elif page == "Growth Dynamics Map":
        geo_viz.main()
    elif page == "Contact & Feedback":
        contact.main()

if __name__ == "__main__":
    main()
