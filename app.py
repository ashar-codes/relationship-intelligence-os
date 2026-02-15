import streamlit as st
from database import init_db
from ui.profile_manager import render_profile_sidebar
from ui.dashboard import render_dashboard


# -------------------------
# App Configuration
# -------------------------
st.set_page_config(
    page_title="Relationship Intelligence OS",
    layout="wide"
)

# Initialize database
init_db()

st.title("Relationship Intelligence OS")

# -------------------------
# Sidebar Profile Selection
# -------------------------
selected_profile_id = render_profile_sidebar()

# -------------------------
# Main Dashboard
# -------------------------
if selected_profile_id:
    render_dashboard(selected_profile_id)
else:
    st.info("Create or select a relationship profile to begin.")
