import streamlit as st
from classes.style_manager import StyleManager
st.title(" EXORA")
st.subheader("Smart Navigation")

st.markdown (
"""
### Welcome to EXORA!

```
Explore the exhibition, discover pavilions,
and find the best route to your destination.

Your smart companion for a better Expo experience.
"""

)

st.divider()

st.subheader("Explore EXPO")

col1, col2 = st.columns(2)

with col1:
 st.markdown("###  Map Navigation")
st.write(
"Explore the exhibition map, choose your destination, "
"and find the best route."
)
if st.button("Open Map", use_container_width=True):
 st.switch_page("pages/map.py")

with col2:
 st.markdown("###  AR Navigation")
st.write(
"Navigate through the exhibition using your camera "
"and follow the recommended route."
)
if st.button("Start AR Navigation", use_container_width=True):
 st.switch_page("pages/ar.py")

st.divider()

col3, col4 = st.columns(2)

with col3:
 st.markdown("###  AI Assistant")
st.write("Ask questions and get help during your Expo visit.")
if st.button("Open AI Chatbot", use_container_width=True):
 st.switch_page("pages/ai.py")

with col4:
 st.markdown("###  Account")
st.write("Access your account and manage your profile.")
if st.button("Open Account", use_container_width=True):
 st.switch_page("pages/account.py")

st.divider()

st.markdown("### Already have an account?")

if st.button("Log In", use_container_width=True):
 st.switch_page("pages/log_in.py")
