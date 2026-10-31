import streamlit as st
from classes.language_manager import LanguageManager


st.set_page_config(
    page_title="EXORA - Account",
    page_icon="👤",
    layout="wide"
)


# Check login
if not st.session_state.get("logged_in", False):
    st.warning("Please login first.")
    st.stop()


# Language selection
languages = {
    "English 🇬🇧": "en",
    "العربية 🇸🇦": "ar",
    "Français 🇫🇷": "fr"
}

if "language" not in st.session_state:
    st.session_state.language = "en"

selected_language = st.selectbox(
    "Language / اللغة / Langue",
    list(languages.keys()),
    index=list(languages.values()).index(
        st.session_state.language
    ),
    key="account_language"
)

st.session_state.language = languages[selected_language]

language = LanguageManager(st.session_state.language)


def t(key):
    return language.get_text(key)


# Page direction
if language.get_direction() == "rtl":
    st.markdown(
        """
        <style>
        .stApp {
            direction: rtl;
            text-align: right;
        }
        </style>
        """,
        unsafe_allow_html=True
    )


# Account Information
st.title(t("account"))

st.divider()

st.header(t("account_information"))

username = st.session_state.current_user

user = st.session_state.auth.users[username]

st.write(f"{t('username')}: {user['username']}")

st.write(f"{t('email')}: {user['email']}")


# Settings
st.divider()

st.header(t("settings"))

st.subheader(t("language"))

st.write(
    f"{t('current_language')}: "
    f"{language.get_current_language()}"
)


# Change Password
st.divider()

st.subheader(t("change_password"))

old_password = st.text_input(
    t("current_password"),
    type="password",
    key="old_password"
)

new_password = st.text_input(
    t("new_password"),
    type="password",
    key="new_password"
)

if st.button(t("update_password")):

    if not st.session_state.auth.login(username, old_password):
        st.error(t("incorrect_current_password"))

    elif len(new_password) < 8:
        st.error(t("password_length"))

    else:
        user["password"] = new_password
        st.success(t("password_updated"))


# Logout
st.divider()

if st.button(t("logout")):

    st.session_state.logged_in = False
    st.session_state.current_user = None
    st.session_state.page = "Login"

    st.switch_page("pages/log_in.py")