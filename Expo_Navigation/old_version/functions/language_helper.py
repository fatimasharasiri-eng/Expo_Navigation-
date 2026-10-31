import streamlit as st
from classes.language_manager import LanguageManager


LANGUAGES = {
    "English 🇬🇧": "en",
    "العربية 🇸🇦": "ar",
    "Français 🇫🇷": "fr"
}


def get_language_manager():

    if "language" not in st.session_state:
        st.session_state.language = "en"

    return LanguageManager(st.session_state.language)


def language_selector(key):

    current_language = st.session_state.get("language", "en")

    language_names = list(LANGUAGES.keys())

    current_name = next(
        name for name, code in LANGUAGES.items()
        if code == current_language
    )

    selected = st.selectbox(
        "Language",
        language_names,
        index=language_names.index(current_name),
        key=key
    )

    st.session_state.language = LANGUAGES[selected]

    return LanguageManager(st.session_state.language)