import streamlit as st
from database import init_db
from ui.profile_manager import render_profile_sidebar
from ui.dashboard import render_dashboard
from auth import login_button, handle_callback

st.set_page_config(
    page_title="Relationship Intelligence OS",
    layout="wide"
)

# 👇 ADD STYLING RIGHT AFTER
st.markdown("""
<style>

/* Global background */
body {
    background-color: #0f172a;
}

/* Main container spacing */
.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

/* Card style */
.card {
    background: #1e293b;
    padding: 24px;
    border-radius: 20px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.4);
    margin-bottom: 20px;
}

/* Metric number */
.metric-value {
    font-size: 32px;
    font-weight: 600;
    color: white;
}

/* Subtext */
.metric-label {
    font-size: 14px;
    opacity: 0.7;
    color: #cbd5e1;
}

/* Glow for high risk */
.glow-red {
    box-shadow: 0 0 20px rgba(255,0,0,0.4);
}

</style>
""", unsafe_allow_html=True)

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
