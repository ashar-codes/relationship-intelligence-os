from groq import Groq
import streamlit as st
from config import get_groq_api_key, RESPONSE_MODEL


def generate_polite_no(context, relationship_category):

    client = Groq(api_key=get_groq_api_key())

    category_instruction = {
        "Romantic": "Maintain warmth and emotional reassurance.",
        "Family": "Be respectful and considerate.",
        "Professional": "Be structured, confident, and respectful.",
        "Friendship": "Be casual but firm.",
        "Other": "Be polite and clear."
    }.get(relationship_category, "Be polite and clear.")

    prompt = f"""
You are a communication strategist helping someone say NO politely but confidently.

Context:
{context}

Relationship Type:
{relationship_category}

Instruction:
{category_instruction}

Generate 3 versions:

1. Soft Boundary
2. Assertive Boundary
3. Direct Boundary

Rules:
- No over-apologizing
- No guilt language
- No emotional manipulation
- Clear and healthy boundary

Format clearly with section titles.
"""

    response = client.chat.completions.create(
        model=RESPONSE_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5,
    )

    return response.choices[0].message.content
