import streamlit as st
from database import SessionLocal
from models import Relationship


def get_all_profiles(user_id: int):
    db = SessionLocal()
    profiles = db.query(Relationship).filter_by(user_id=user_id).all()
    db.close()
    return profiles


def create_profile(name: str, relationship_type: str, category: str, user_id: int):
    db = SessionLocal()
    profile = Relationship(
        name=name,
        relationship_type=relationship_type,
        category=category,
        user_id=user_id
    )
    db.add(profile)
    db.commit()
    db.close()


def delete_profile(profile_id: int, user_id: int):
    db = SessionLocal()
    profile = db.query(Relationship).filter_by(id=profile_id, user_id=user_id).first()
    if profile:
        db.delete(profile)
        db.commit()
    db.close()


def render_profile_sidebar():

    if "user_id" not in st.session_state:
        return None

    user_id = st.session_state["user_id"]

    st.sidebar.markdown("## Relationship OS")
    st.sidebar.markdown("---")
    st.sidebar.markdown("### Profiles")

    profiles = get_all_profiles(user_id)

    if profiles:
        profile_dict = {f"{p.name} ({p.category})": p.id for p in profiles}
        selected_label = st.sidebar.selectbox("Select Profile", list(profile_dict.keys()))
        selected_id = profile_dict[selected_label]
    else:
        selected_id = None
        st.sidebar.info("No profiles yet.")

    with st.sidebar.expander("➕ Create New Profile"):
        name = st.text_input("Name")
        rel_type = st.text_input("Relationship Type")
        category = st.selectbox(
            "Category",
            ["Romantic", "Family", "Professional", "Friendship", "Other"]
        )

        if st.button("Create Profile"):
            if name and rel_type:
                create_profile(name, rel_type, category, user_id)
                st.success("Profile Created")
                st.rerun()

    if selected_id:
        with st.sidebar.expander("⚠ Delete Profile"):
            if st.button("Delete Selected Profile"):
                delete_profile(selected_id, user_id)
                st.success("Profile Deleted")
                st.rerun()

    return selected_id
