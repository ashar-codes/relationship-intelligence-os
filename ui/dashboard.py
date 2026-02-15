import streamlit as st
from database import SessionLocal
from models import Relationship, Conversation
from services.analyzer import analyze_conversation
from services.risk_engine import update_toxicity_memory, apply_health_cap
from services.style_engine import update_style_profile
from services.assistant import generate_block_responses
from services.repair import generate_repair_message


def render_dashboard(profile_id: int):

    db = SessionLocal()
    relationship = db.query(Relationship).filter_by(id=profile_id).first()

    if not relationship:
        st.warning("Profile not found.")
        db.close()
        return

    st.title(f"{relationship.name} Dashboard")
    st.caption(f"Type: {relationship.relationship_type} | Category: {relationship.category}")

    # -----------------------------
    # Analyze New Conversation
    # -----------------------------
    st.subheader("Analyze Conversation")

    conversation_text = st.text_area("Paste conversation here")

    if st.button("Analyze"):
        scores = analyze_conversation(conversation_text, relationship.category)

        if scores:

            # Apply risk memory
            toxicity = update_toxicity_memory(
                db,
                relationship,
                scores["health"],
                scores["safety"],
                scores["risk_a"],
                scores["risk_b"]
            )

            # Cap health based on toxicity
            capped_health = apply_health_cap(scores["health"], toxicity)

            # Store conversation
            convo = Conversation(
                relationship_id=relationship.id,
                raw_text=conversation_text,
                health_score=capped_health,
                safety_score=scores["safety"],
                risk_a=scores["risk_a"],
                risk_b=scores["risk_b"]
            )
            db.add(convo)
            db.commit()

            # Update style profile
            update_style_profile(db, relationship, conversation_text)

            st.success("Conversation analyzed.")
            st.rerun()

    # -----------------------------
    # Load Last Conversation
    # -----------------------------
    last_convo = (
        db.query(Conversation)
        .filter_by(relationship_id=relationship.id)
        .order_by(Conversation.created_at.desc())
        .first()
    )

    if last_convo:

        st.subheader("Live Relationship Metrics")

        col1, col2 = st.columns(2)

        with col1:
            st.progress(last_convo.health_score / 100)
            st.caption(f"Communication Health: {last_convo.health_score}")

            st.progress(last_convo.safety_score / 100)
            st.caption(f"Emotional Safety: {last_convo.safety_score}")

        with col2:
            st.progress(last_convo.risk_a / 100)
            st.caption(f"Partner A Risk: {last_convo.risk_a}")

            st.progress(last_convo.risk_b / 100)
            st.caption(f"Partner B Risk: {last_convo.risk_b}")

        # -------------------------
        # Red Flag Section
        # -------------------------
        st.subheader("Red Flag Detection")

        if last_convo.risk_b > 70:
            st.error("🚩 High Risk Behavior Detected")
        elif last_convo.risk_b > 40:
            st.warning("⚠ Early Warning Signs")
        else:
            st.success("✅ No Major Red Flags")

        # -------------------------
        # Block Assistant
        # -------------------------
        st.subheader("Feeling Stuck?")

        block_context = st.text_area("Paste last few lines")

        if st.button("Suggest Responses"):
            responses = generate_block_responses(
                block_context,
                relationship.category,
                relationship.user_style_summary,
                relationship.toxicity_index
            )

            if responses:
                st.markdown(responses)

        # -------------------------
        # Repair Section
        # -------------------------
        st.subheader("Repair Conversation")

        repair_context = st.text_area("Repair context")

        if st.button("Generate Repair"):
            repair_msg = generate_repair_message(
                repair_context,
                relationship.category,
                relationship.user_style_summary,
                relationship.toxicity_index
            )

            if repair_msg:
                st.markdown(repair_msg)

    else:
        st.info("No conversations analyzed yet.")

    db.close()
