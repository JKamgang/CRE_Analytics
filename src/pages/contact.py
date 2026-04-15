import streamlit as st
import os
from src.shared.documentation.auto_doc import SemanticModelDocumenter

def main():
    st.title("📞 Multimodal Contact Center")
    st.markdown("We value your feedback. Please share your experience using text, voice, video, or files.")

    # 1. Multimodal Feedback
    user_feedback = st.chat_input("Type your feedback here or upload media...")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.file_uploader("Upload Images/Videos", type=["png", "jpg", "mp4", "mov"])
    with col2:
        st.file_uploader("Upload PDF/Docs", type=["pdf", "docx"])
    with col3:
        if st.button("🎤 Record Voice Note"):
            st.info("Voice recording initiated... (simulated)")

    st.divider()

    # 2. UX Questionnaire
    st.subheader("📋 UI/UX Experience Survey")
    with st.form("ux_survey"):
        q1 = st.radio("1. How intuitive was the 'Growth Dynamics' transition?",
                     ["Very Intuitive", "Neutral", "Confusing"])

        q2 = st.select_slider("2. Rate the performance of the Mapping Engine:",
                             options=range(1, 6))

        q3 = st.text_area("3. Which mapping engine did you prefer most? (Leaflet, MapLibre, QGIS)")

        q4 = st.checkbox("4. Would you like to see more 'What If' scenarios?")

        q5 = st.radio("5. How likely are you to recommend Alile CRE Analytics?",
                     ["Definitely", "Maybe", "Unlikely"])

        if st.form_submit_button("Submit Survey"):
            st.success("Thank you for your valuable feedback!")

    # 3. AI Assistant Integration
    st.divider()
    st.subheader("🤖 Open Source AI Assistant (Gemma 4 / Llama 3)")
    st.write("I am here to help you navigate the system, interpret data, and report issues.")

    doc = SemanticModelDocumenter()
    query = st.text_input("How can I assist you today? (e.g., 'Explain SQFT' or 'Report a bug')")
    if query:
        with st.spinner("Gemma 4 is thinking..."):
            response = doc.assist_user(query)
            st.chat_message("assistant").write(response)

if __name__ == "__main__":
    main()
