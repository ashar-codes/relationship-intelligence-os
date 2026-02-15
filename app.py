import streamlit as st
from database import init_db
from ui.profile_manager import render_profile_sidebar
from ui.dashboard import render_dashboard
from auth import login_button, handle_callback

st.set_page_config(page_title="Relationship Intelligence OS", layout="wide")

init_db()

# Handle OAuth callback
handle_callback()

# If not logged in
if "user_id" not in st.session_state:
    st.title("Relationship Intelligence OS")
    st.subheader("Login Required")
    login_button()
    st.stop()

st.sidebar.write(f"Logged in as: {st.session_state['user_email']}")

selected_profile_id = render_profile_sidebar()

if selected_profile_id:
    render_dashboard(selected_profile_id)
else:
    st.info("Create or select a relationship profile.")
