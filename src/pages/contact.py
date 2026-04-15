import streamlit as st
import os
import json
from src.shared.documentation.auto_doc import SemanticModelDocumenter

def main():
    st.header("📞 Multimodal Feedback & Contact Center")
    st.write("Share your experience or report an issue. We support Voice, Video, Images, and PDF.")

    # 1. Context-Aware Feedback
    # Current Map State Simulation
    map_state = {"zoom": 11, "center": [38.9, -77.0], "engine": "Leaflet"}

    with st.container(border=True):
        st.write("💬 **AI-Assisted Feedback Loop**")
        user_input = st.chat_input("Type your message... (Voice/Video upload enabled below)")

        col1, col2 = st.columns(2)
        with col1:
            media = st.file_uploader("Upload Media (Voice/Video/Image)", type=['mp3', 'mp4', 'png', 'jpg'])
        with col2:
            doc_file = st.file_uploader("Upload PDF/Reports", type=['pdf'])

        if st.button("🚀 Submit Multimodal Feedback"):
            payload = {
                "user_text": user_input,
                "map_context": map_state,
                "has_media": media is not None
            }
            st.success("Feedback captured with full map context! Mike Bush will review this state.")

            # Reactionary Survey
            st.divider()
            st.subheader("📋 Quick Experience Survey")
            with st.form("survey"):
                q1 = st.radio("Did the Z-Score math align with your expectations for this region?", ["Yes", "No", "Uncertain"])
                q2 = st.select_slider("Rate the 3D MapLibre performance:", options=range(1,6))
                if st.form_submit_button("Submit Survey"):
                    st.toast("Thank you for the data-driven feedback!")

    # 2. Open Source AI Guide (Gemma 4)
    st.divider()
    st.subheader("🤖 Alile AI Assistant (Gemma 4 Cascade)")
    st.write("Integrated open-source intelligence to help you understand data and visuals.")

    documenter = SemanticModelDocumenter()
    query = st.text_input("Ask about a field (e.g. 'What is SQFT?') or request a system fix report:")
    if query:
        with st.spinner("Cascading through LLMs..."):
            response = documenter.assist_user(query)
            st.chat_message("assistant").write(response)

if __name__ == "__main__":
    main()
