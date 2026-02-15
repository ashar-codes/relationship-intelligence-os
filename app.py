import streamlit as st
from database import init_db
from ui.profile_manager import render_profile_sidebar
from ui.dashboard import render_dashboard
from auth import register_user, login_user, load_user_from_token, logout_user

# =============================
# PAGE CONFIG
# =============================
st.set_page_config(
    page_title="Relationship Intelligence OS",
    layout="wide"
)

# =============================
# PREMIUM DARK STYLING
# =============================
st.markdown("""
<style>

/* Background */
body {
    background-color: #0f172a;
}

/* Container spacing */
.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: #0b1220;
    border-right: 1px solid rgba(255,255,255,0.05);
}

/* Cards */
.card {
    background: linear-gradient(145deg, #1e293b, #172033);
    padding: 24px;
    border-radius: 20px;
    box-shadow: 0 8px 30px rgba(0,0,0,0.4);
    margin-bottom: 20px;
    transition: all 0.3s ease-in-out;
}

.card:hover {
    transform: translateY(-4px);
    box-shadow: 0 15px 40px rgba(0,0,0,0.6);
}

/* Typography */
.metric-value {
    font-size: 36px;
    font-weight: 600;
    letter-spacing: -1px;
}

.metric-label {
    font-size: 14px;
    opacity: 0.6;
    margin-bottom: 8px;
}

.glow-red {
    box-shadow: 0 0 20px rgba(255, 0, 0, 0.6);
}

</style>
""", unsafe_allow_html=True)

# =============================
# INIT DATABASE
# =============================
init_db()

# =============================
# LOAD USER FROM COOKIE
# (Remember Me Logic)
# =============================
load_user_from_token()

if "user_id" not in st.session_state:
    st.title("Relationship Intelligence OS")

    tab_login, tab_register = st.tabs(["Login", "Register"])

    with tab_login:
        login_user()

    with tab_register:
        register_user()

    st.stop()

# =============================
# USER IS AUTHENTICATED
# =============================
st.sidebar.write(f"Logged in as: {st.session_state['user_email']}")

# Logout button in sidebar
logout_user()

# =============================
# PROFILE SELECTION
# =============================
selected_profile_id = render_profile_sidebar()

if selected_profile_id:
    render_dashboard(selected_profile_id)
else:
    st.info("Create or select a relationship profile.")
