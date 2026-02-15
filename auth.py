import streamlit as st
import secrets
from passlib.context import CryptContext
from database import SessionLocal
from models import User

# 🔥 Use PBKDF2 instead of bcrypt (stable on Streamlit Cloud)
pwd_context = CryptContext(
    schemes=["pbkdf2_sha256"],
    deprecated="auto"
)


# =========================
# AUTO LOGIN FROM TOKEN
# =========================
def load_user_from_token():

    params = st.query_params

    if "auth_token" in params:
        token = params["auth_token"]

        db = SessionLocal()
        user = db.query(User).filter_by(auth_token=token).first()

        if user:
            st.session_state["user_id"] = user.id
            st.session_state["user_email"] = user.email

        db.close()


# =========================
# REGISTER
# =========================
def register_user():

    st.subheader("Create Account")

    name = st.text_input("Full Name", key="reg_name")
    email = st.text_input("Email", key="reg_email")
    gender = st.selectbox("Gender", ["Male", "Female", "Other"], key="reg_gender")
    password = st.text_input("Password", type="password", key="reg_password")
    confirm = st.text_input("Confirm Password", type="password", key="reg_confirm")

    if st.button("Register", key="reg_button"):

        if password != confirm:
            st.error("Passwords do not match")
            return

        db = SessionLocal()
        existing = db.query(User).filter_by(email=email).first()

        if existing:
            st.error("Email already registered")
            db.close()
            return

        token = secrets.token_urlsafe(32)

        user = User(
            name=name,
            email=email,
            gender=gender,
            password_hash=pwd_context.hash(password),
            auth_token=token
        )

        db.add(user)
        db.commit()

        st.session_state["user_id"] = user.id
        st.session_state["user_email"] = user.email

        st.query_params["auth_token"] = token

        db.close()
        st.rerun()


# =========================
# LOGIN
# =========================
def login_user():

    st.subheader("Login")

    email = st.text_input("Email", key="login_email")
    password = st.text_input("Password", type="password", key="login_password")

    if st.button("Login", key="login_button"):

        db = SessionLocal()
        user = db.query(User).filter_by(email=email).first()

        if not user or not user.password_hash:
            st.error("Invalid credentials")
            db.close()
            return

        if not pwd_context.verify(password, user.password_hash):
            st.error("Invalid credentials")
            db.close()
            return

        token = secrets.token_urlsafe(32)
        user.auth_token = token
        db.commit()

        st.session_state["user_id"] = user.id
        st.session_state["user_email"] = user.email

        st.query_params["auth_token"] = token

        db.close()
        st.rerun()


# =========================
# LOGOUT
# =========================
def logout_user():

    if st.sidebar.button("Logout"):

        db = SessionLocal()
        user = db.query(User).filter_by(id=st.session_state["user_id"]).first()

        if user:
            user.auth_token = None
            db.commit()

        db.close()

        st.session_state.clear()
        st.query_params.clear()
        st.rerun()
