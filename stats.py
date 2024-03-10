# this page intends to allow user to adjust timeout seconds, 

import streamlit as st
import random
import serial
import time
from helpers import *

# UI setup
st.sidebar.image("logo.png", width=270)
st.header("Settings")
st.markdown("---")

# adjust timeout seconds
timeout_seconds = st.slider("Set timeout (in seconds) for feedback:", 1, 60, 10, 1)

# save button saves adjusted timeout_seconds and pass to wait_for_feedback
if st.button('Save'):
    st.session_state.timeout_seconds = timeout_seconds
    st.success("Timeout saved!")
else:
    timeout_seconds = st.session_state.timeout_seconds


# Display selected settings
st.markdown("---")
st.subheader("📊 Selections")
st.write("Timeout seconds for feedback:", timeout_seconds)
st.markdown("---")
