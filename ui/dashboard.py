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

    # =============================
    # HEADER
    # =============================
    toxicity = relationship.toxicity_index or 0

    if toxicity > 60:
        badge_color = "#ef4444"
        badge_text = "High Tension"
    elif toxicity > 30:
        badge_color = "#f59e0b"
        badge_text = "Moderate Tension"
    else:
        badge_color = "#22c55e"
        badge_text = "Stable"

    st.markdown(
        f"""
        <div class="card">
            <div class="metric-label">Relationship</div>
            <div class="metric-value">{relationship.name}</div>
            <div class="metric-label">
                {relationship.relationship_type} • {relationship.category}
            </div>
            <div style="margin-top:10px;color:{badge_color};font-weight:500;">
                Toxicity Index: {toxicity} • {badge_text}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # =============================
    # LOAD LAST CONVERSATION
    # =============================
    last_convo = (
        db.query(Conversation)
        .filter_by(relationship_id=relationship.id)
        .order_by(Conversation.created_at.desc())
        .first()
    )

    if last_convo:

        st.markdown("## Relationship Metrics")

        def metric_card(title, value, color="white", glow=False):
            glow_style = "box-shadow:0 0 20px rgba(255,0,0,0.6);" if glow else ""
            st.markdown(
                f"""
                <div class="card" style="{glow_style}">
                    <div class="metric-label">{title}</div>
                    <div class="metric-value" style="color:{color};">
                        {value}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

        col1, col2 = st.columns(2)
        col3, col4 = st.columns(2)

        health_color = "#22c55e" if last_convo.health_score > 70 else "#f59e0b"
        safety_color = "#3b82f6" if last_convo.safety_score > 70 else "#f59e0b"
        risk_a_color = "#ef4444" if last_convo.risk_a > 50 else "#f59e0b"
        risk_b_color = "#ef4444" if last_convo.risk_b > 50 else "#f59e0b"

        with col1:
            metric_card("Communication Health", f"{last_convo.health_score}%", health_color)

        with col2:
            metric_card("Emotional Safety", f"{last_convo.safety_score}%", safety_color)

        with col3:
            metric_card("Partner A Risk", f"{last_convo.risk_a}%", risk_a_color, glow=last_convo.risk_a > 70)

        with col4:
            metric_card("Partner B Risk", f"{last_convo.risk_b}%", risk_b_color, glow=last_convo.risk_b > 70)

    else:
        st.info("No conversations analyzed yet.")

    # =============================
    # SMART TOOLS
    # =============================
    st.markdown("## Smart Tools")

    tab1, tab2, tab3 = st.tabs(["Analyze", "Feeling Stuck?", "Repair"])

    with tab1:
        conversation_text = st.text_area("Paste conversation here")

        if st.button("Analyze Conversation"):
            scores = analyze_conversation(conversation_text, relationship.category)

            if scores:
                toxicity = update_toxicity_memory(
                    db,
                    relationship,
                    scores["health"],
                    scores["safety"],
                    scores["risk_a"],
                    scores["risk_b"]
                )

                capped_health = apply_health_cap(scores["health"], toxicity)

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

                update_style_profile(db, relationship, conversation_text)

                st.success("Conversation analyzed.")
                st.rerun()

    with tab2:
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

    with tab3:
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

    db.close()
