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

        with col1:
            metric_card("Communication Health",
                        f"{last_convo.health_score}%",
                        "#22c55e" if last_convo.health_score > 70 else "#f59e0b")

        with col2:
            metric_card("Emotional Safety",
                        f"{last_convo.safety_score}%",
                        "#3b82f6" if last_convo.safety_score > 70 else "#f59e0b")

        with col3:
            metric_card("Partner A Risk",
                        f"{last_convo.risk_a}%",
                        "#ef4444" if last_convo.risk_a > 50 else "#f59e0b",
                        glow=last_convo.risk_a > 70)

        with col4:
            metric_card("Partner B Risk",
                        f"{last_convo.risk_b}%",
                        "#ef4444" if last_convo.risk_b > 50 else "#f59e0b",
                        glow=last_convo.risk_b > 70)

    # =============================
    # CONVERSATION HISTORY
    # =============================
    st.markdown("## Conversation History")

    all_convos = (
        db.query(Conversation)
        .filter_by(relationship_id=relationship.id)
        .order_by(Conversation.created_at.desc())
        .all()
    )

    if all_convos:

        convo_map = {
            f"{c.created_at.strftime('%Y-%m-%d %H:%M:%S')} | H:{c.health_score}% | S:{c.safety_score}%": c.id
            for c in all_convos
        }

        selected_label = st.selectbox(
            "Select Conversation",
            list(convo_map.keys())
        )

        selected_id = convo_map[selected_label]
        selected_convo = db.query(Conversation).filter_by(id=selected_id).first()

        st.markdown("### Conversation Content")
        st.markdown(
            f"<div class='card'>{selected_convo.raw_text}</div>",
            unsafe_allow_html=True
        )

        if st.button("Delete This Conversation"):
            db.delete(selected_convo)
            db.commit()
            st.success("Conversation deleted.")
            st.rerun()

    else:
        st.info("No previous conversations stored.")

    # =============================
    # SMART TOOLS
    # =============================
    st.markdown("## Smart Tools")

    is_professional = relationship.category == "Professional"

    if is_professional:
        tabs = st.tabs([
            "Analyze",
            "Feeling Stuck?",
            "Repair",
            "Professional Response",
            "Say No"
        ])
        tab_analyze, tab_stuck, tab_repair, tab_professional, tab_no = tabs
    else:
        tabs = st.tabs([
            "Analyze",
            "Feeling Stuck?",
            "Repair",
            "Say No"
        ])
        tab_analyze, tab_stuck, tab_repair, tab_no = tabs

    # -----------------------------
    # ANALYZE
    # -----------------------------
    with tab_analyze:

    conversation_text = st.text_area("Paste conversation here")

    st.markdown("### Or Upload Screenshot")

    uploaded_image = st.file_uploader(
        "Upload conversation image",
        type=["png", "jpg", "jpeg"],
        key="ocr_upload"
    )

    if uploaded_image:
        from services.ocr_engine import extract_text_from_image

        extracted_text = extract_text_from_image(uploaded_image)

        if extracted_text:
            st.success("Text extracted from image.")
            conversation_text = st.text_area(
                "Extracted Text",
                value=extracted_text,
                height=200
            )
        else:
            st.error("Could not extract text from image.")



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

    # -----------------------------
    # STUCK
    # -----------------------------
    with tab_stuck:
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

    # -----------------------------
    # REPAIR
    # -----------------------------
    with tab_repair:
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

    # -----------------------------
    # PROFESSIONAL RESPONSE
    # -----------------------------
    if is_professional:
        with tab_professional:
            from services.professional_engine import generate_professional_response

            prof_context = st.text_area("Describe the situation")
            tone = st.selectbox("Select Tone", ["Formal", "Neutral", "Direct"])

            if st.button("Generate Professional Response"):
                response = generate_professional_response(prof_context, tone)
                if response:
                    st.markdown(response)

    # -----------------------------
    # SAY NO (ALL RELATIONSHIPS)
    # -----------------------------
    with tab_no:
        from services.boundary_engine import generate_polite_no

        no_context = st.text_area("What do you need to decline?")

        if st.button("Generate Polite No"):
            result = generate_polite_no(
                no_context,
                relationship.category
            )
            if result:
                st.markdown(result)

    db.close()
