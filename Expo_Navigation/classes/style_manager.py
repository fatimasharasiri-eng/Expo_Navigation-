import streamlit as st
from pathlib import Path


class StyleManager:

    @staticmethod
    def load_css():

        css_path = Path(__file__).resolve().parent.parent / "assets" / "style.css"

        with open(css_path, "r", encoding="utf-8") as file:
            css = file.read()

        st.markdown(
            f"<style>{css}</style>",
            unsafe_allow_html=True
        )