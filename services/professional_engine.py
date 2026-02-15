 from groq import Groq
import streamlit as st

client = Groq(api_key=st.secrets["groq"]["api_key"])


def generate_professional_response(context, tone_level):

    tone_instruction = {
        "Formal": "Use highly professional corporate tone.",
        "Neutral": "Use calm professional tone.",
        "Direct": "Use confident and concise tone."
    }.get(tone_level, "Use professional tone.")

    prompt = f"""
You are a professional communication strategist.

Context:
{context}

Task:
1. Create a professional explanation that maintains credibility.
2. Provide a strategic recovery plan with timeline.
3. Keep authority-respecting tone.

Tone Instruction:
{tone_instruction}

Do NOT sound emotional.
Do NOT over-apologize.
Do NOT blame others.

Structure output like this:

Professional Explanation:
...

Recovery Plan:
...

Optional Follow-Up:
...
"""

    response = client.chat.completions.create(
        model="llama-3.1-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4,
    )

    return response.choices[0].message.content
