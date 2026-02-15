import streamlit as st
from passlib.hash import bcrypt
from database import SessionLocal
from models import User
from streamlit_cookies_manager import EncryptedCookieManager

cookies = EncryptedCookieManager(
    prefix="relationship_os_",
    password="super-secret-key"
)

if not cookies.ready():
    st.stop()


# =========================
# REGISTER
# =========================
def register_user():

    st.subheader("Create Account")

    name = st.text_input("Full Name")
    email = st.text_input("Email")
    gender = st.selectbox("Gender", ["Male", "Female", "Other"])
    password = st.text_input("Password", type="password")
    confirm = st.text_input("Confirm Password", type="password")

    if st.button("Register"):

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
            password_hash=bcrypt.hash(password)
        )

        db.add(user)
        db.commit()

        cookies["user_id"] = str(user.id)
        cookies.save()

        st.success("Account created!")
        st.session_state["user_id"] = user.id
        st.session_state["user_email"] = user.email
        db.close()
        st.rerun()


# =========================
# LOGIN
# =========================
def login_user():

    st.subheader("Login")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Login"):

        db = SessionLocal()
        user = db.query(User).filter_by(email=email).first()

        if not user or not user.password_hash:
            st.error("Invalid credentials")
            db.close()
            return

        if not bcrypt.verify(password, user.password_hash):
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
# AUTO LOGIN FROM COOKIE
# =========================
def load_user_from_cookie():

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

    if st.button("Logout"):
        cookies["user_id"] = ""
        cookies.save()
        st.session_state.clear()
        st.rerun()
