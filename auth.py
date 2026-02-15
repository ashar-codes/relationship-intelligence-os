import streamlit as st
from passlib.context import CryptContext
from database import SessionLocal
from models import User
from streamlit_cookies_manager import EncryptedCookieManager

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# =========================
# GET COOKIE MANAGER SAFELY
# =========================
def get_cookies():
    cookies = EncryptedCookieManager(
        prefix="relationship_os_",
        password="super-secret-key"
    )

    if not cookies.ready():
        st.stop()

    return cookies


# =========================
# REGISTER
# =========================
def register_user():

    cookies = get_cookies()

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

        user = User(
            name=name,
            email=email,
            gender=gender,
            password_hash=pwd_context.hash(password)
        )

        db.add(user)
        db.commit()

        cookies["user_id"] = str(user.id)
        cookies.save()

        st.session_state["user_id"] = user.id
        st.session_state["user_email"] = user.email

        db.close()
        st.rerun()


# =========================
# LOGIN
# =========================
def login_user():

    cookies = get_cookies()

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

        cookies["user_id"] = str(user.id)
        cookies.save()

        st.session_state["user_id"] = user.id
        st.session_state["user_email"] = user.email

        db.close()
        st.rerun()


# =========================
# LOAD USER FROM COOKIE
# =========================
def load_user_from_cookie():

    cookies = get_cookies()

    if "user_id" in cookies:
        user_id = cookies["user_id"]

        db = SessionLocal()
        user = db.query(User).filter_by(id=int(user_id)).first()

        if user:
            st.session_state["user_id"] = user.id
            st.session_state["user_email"] = user.email

        db.close()


# =========================
# LOGOUT
# =========================
def logout_user():

    cookies = get_cookies()

    if st.sidebar.button("Logout"):
        cookies["user_id"] = ""
        cookies.save()
        st.session_state.clear()
        st.rerun()
