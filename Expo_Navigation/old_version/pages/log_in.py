import streamlit as st
from classes.authentication import Authentication
from classes.language_manager import LanguageManager
from classes.style_manager import StyleManager

st.set_page_config(
    page_title="EXORA",
    
    layout="wide"
)


# Initialize session state
if "auth" not in st.session_state:
    st.session_state.auth = Authentication()

if "page" not in st.session_state:
    st.session_state.page = "Register"

if "language" not in st.session_state:
    st.session_state.language = "en"

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "current_user" not in st.session_state:
    st.session_state.current_user = None


# Language selection
languages = {
    "English 🇬🇧": "en",
    "العربية 🇸🇦": "ar",
    "Français 🇫🇷": "fr"
}

selected_language = st.selectbox(
    "Language / اللغة / Langue",
    list(languages.keys()),
    index=list(languages.values()).index(
        st.session_state.language
    )
)

st.session_state.language = languages[selected_language]

language = LanguageManager(st.session_state.language)
auth = st.session_state.auth


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


def t(key):
    return language.get_text(key)


st.title("EXORA", text_alignment="center")


# REGISTER
if st.session_state.page == "Register":

    st.header(t("create_account"))

    email = st.text_input(
        t("email"),
        key="register_email"
    )

    username = st.text_input(
        t("username"),
        key="register_username"
    )

    password = st.text_input(
        t("password"),
        type="password",
        key="register_password"
    )

    if st.button(t("register")):

        success, message = auth.sign_up(
            email,
            username,
            password
        )

        if success:
            st.success(t("registration_success"))
            st.session_state.page = "Login"
            st.rerun()

        else:
            if message == "Invalid email":
                st.error(t("invalid_email"))

            elif message == "Please enter a username":
                st.warning(t("enter_username"))

            elif message == "Password must be at least 8 characters":
                st.warning(t("password_length"))

            else:
                st.error(message)

    if st.button(t("already_account")):
        st.session_state.page = "Login"
        st.rerun()


# LOGIN
elif st.session_state.page == "Login":

    st.header(t("login"))

    username = st.text_input(
        t("username"),
        key="login_username"
    )

    password = st.text_input(
        t("password"),
        type="password",
        key="login_password"
    )

    if st.button(t("login")):

        if auth.login(username, password):

            st.session_state.logged_in = True
            st.session_state.current_user = username

            st.success(t("login_success"))
            st.info(t("login_next_step"))

        else:
            st.error(t("invalid_credentials"))

    if st.button(t("forgot_password")):
        st.session_state.page = "Forgot Password"
        st.rerun()

    if st.button(t("create_new_account")):
        st.session_state.page = "Register"
        st.rerun()


# FORGOT PASSWORD
elif st.session_state.page == "Forgot Password":

    st.header(t("forgot_password"))

    email = st.text_input(t("enter_email"))

    if st.button(t("generate_code")):

        success, code = auth.generate_reset_code(email)

        if success:
            st.session_state.reset_email = email
            st.info(f"{t('demo_code')}: {code}")

        else:
            st.error(t("email_not_found"))

    st.divider()

    st.subheader(t("reset_password"))

    code = st.text_input(t("verification_code"))

    new_password = st.text_input(
        t("new_password"),
        type="password"
    )

    if st.button(t("reset_password")):

        email = st.session_state.get("reset_email", "")

        success, message = auth.reset_password(
            email,
            code,
            new_password
        )

        if success:
            st.success(t("password_changed"))
            st.session_state.page = "Login"
            st.rerun()

        else:
            if message == "Verification code expired":
                st.error(t("code_expired"))

            elif message == "Invalid verification code":
                st.error(t("invalid_code"))

            elif message == "Password must be at least 8 characters":
                st.warning(t("password_length"))

            else:
                st.error(message)

    if st.button(t("back_to_login")):
        st.session_state.page = "Login"
        st.rerun()