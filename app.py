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

/* Background */
body {
    background-color: #0f172a;
}

/* Remove default padding */
.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

/* Sidebar styling */
section[data-testid="stSidebar"] {
    background-color: #0b1220;
    border-right: 1px solid rgba(255,255,255,0.05);
}

/* Card styling */
.card {
    background: linear-gradient(145deg, #1e293b, #172033);
    padding: 24px;
    border-radius: 20px;
    box-shadow: 0 8px 30px rgba(0,0,0,0.4);
    margin-bottom: 20px;
    transition: all 0.3s ease-in-out;
}

/* Hover effect */
.card:hover {
    transform: translateY(-4px);
    box-shadow: 0 15px 40px rgba(0,0,0,0.6);
}

/* Metric value */
.metric-value {
    font-size: 36px;
    font-weight: 600;
    letter-spacing: -1px;
    transition: all 0.4s ease-in-out;
}

/* Label */
.metric-label {
    font-size: 14px;
    opacity: 0.6;
    margin-bottom: 8px;
}

/* Glow for high risk */
.glow-red {
    box-shadow: 0 0 20px rgba(255, 0, 0, 0.6);
}

/* Badge style */
.badge {
    display: inline-block;
    padding: 6px 14px;
    border-radius: 999px;
    font-size: 12px;
    font-weight: 500;
    margin-top: 10px;
}

.badge-low {
    background-color: rgba(34,197,94,0.15);
    color: #22c55e;
}

.badge-mid {
    background-color: rgba(245,158,11,0.15);
    color: #f59e0b;
}

.badge-high {
    background-color: rgba(239,68,68,0.15);
    color: #ef4444;
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
