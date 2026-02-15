from groq import Groq
from config import get_groq_api_key
from models import Relationship
from sqlalchemy.orm import Session
import re


def extract_user_messages(text: str):
    """
    Extract lines starting with 'Me:' or similar patterns.
    """
    lines = text.split("\n")
    user_lines = []

    for line in lines:
        if line.strip().lower().startswith("me:"):
            cleaned = re.sub(r"^me:\s*", "", line.strip(), flags=re.IGNORECASE)
            user_lines.append(cleaned)

    return user_lines


def build_style_summary(messages: list[str]):
    """
    Ask LLM to summarize user's communication style.
    """

    api_key = get_groq_api_key()
    if not api_key or not messages:
        return None

    client = Groq(api_key=api_key)

    joined = "\n".join(messages)

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": """
Analyze this user's communication style.

Return a concise structured description including:
- Tone
- Emotional expressiveness (Low/Medium/High)
- Assertiveness level
- Sentence length tendency
- Conflict behavior
Keep it short and structured.
"""
            },
            {
                "role": "user",
                "content": joined
            }
        ]
    )

    return response.choices[0].message.content


def update_style_profile(
    db: Session,
    relationship: Relationship,
    conversation_text: str
):
    """
    Update style profile if enough messages collected.
    """

    user_messages = extract_user_messages(conversation_text)

    if not user_messages:
        return relationship.user_style_summary

    existing_style = relationship.user_style_summary or ""
    confidence = relationship.style_confidence or 0

    # Increase confidence gradually
    confidence += len(user_messages)

    # Only rebuild style after threshold
    if confidence >= 8:
        style_summary = build_style_summary(user_messages)
        relationship.user_style_summary = style_summary
        relationship.style_confidence = confidence
        db.commit()
        return style_summary

    relationship.style_confidence = confidence
    db.commit()

    return existing_style
