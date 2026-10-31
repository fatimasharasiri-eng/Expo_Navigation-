import streamlit as st

from classes.style_manager import StyleManager

st.set_page_config(
    page_title="EXORA | Smart Navigation",
    
    layout="wide"
)

StyleManager.load_css()

pages = [

    st.Page("pages/welcome.py", title="Welcome", default=True),

    st.Page("pages/home.py", title="Home"),

    st.Page("pages/map.py", title="Map"),

    st.Page("pages/ar.py", title="AR Navigation"),

    st.Page("pages/ai.py", title="AI Chatbot"),

    st.Page("pages/log_in.py", title="Log In"),

    st.Page("pages/account.py", title="Account"),

]

st.navigation(pages).run()