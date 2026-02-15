import streamlit as st
from authlib.integrations.requests_client import OAuth2Session
from database import SessionLocal
from models import User

AUTH_URL = "https://accounts.google.com/o/oauth2/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"
USER_INFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"


def login_button():
    client_id = st.secrets["auth"]["client_id"]
    redirect_uri = st.secrets["auth"]["redirect_uri"]

    oauth = OAuth2Session(
        client_id,
        redirect_uri=redirect_uri,
        scope="openid email profile"
    )

    authorization_url, state = oauth.create_authorization_url(AUTH_URL)

    st.session_state["oauth_state"] = state

    st.markdown(f"[Login with Google]({authorization_url})")


def handle_callback():

    if "code" not in st.query_params:
        return

    client_id = st.secrets["auth"]["client_id"]
    client_secret = st.secrets["auth"]["client_secret"]
    redirect_uri = st.secrets["auth"]["redirect_uri"]

    # Reconstruct full callback URL manually
    code = st.query_params["code"]

    oauth = OAuth2Session(client_id, redirect_uri=redirect_uri)

    token = oauth.fetch_token(
        TOKEN_URL,
        client_secret=client_secret,
        code=code
    )

    resp = oauth.get(USER_INFO_URL)
    user_info = resp.json()

    db = SessionLocal()

    user = db.query(User).filter_by(email=user_info["email"]).first()

    if not user:
        user = User(
            email=user_info["email"],
            name=user_info.get("name")
        )
        db.add(user)
        db.commit()

    st.session_state["user_id"] = user.id
    st.session_state["user_email"] = user.email

    db.close()

    # Clear query params after login
    st.query_params.clear()
