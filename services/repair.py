from groq import Groq
from config import get_groq_api_key


def generate_repair_message(
    context: str,
    category: str,
    style_summary: str | None,
    toxicity_index: int
):
    """
    Generate structured repair message.
    """

    api_key = get_groq_api_key()
    if not api_key:
        return None

    client = Groq(api_key=api_key)

    style_section = ""
    if style_summary:
        style_section = f"""
Match the user's communication style:
{style_summary}
"""

    severity_section = ""
    if toxicity_index > 60:
        severity_section = """
The relationship has significant accumulated tension.
Repair should prioritize accountability and emotional reassurance.
"""
    elif toxicity_index > 30:
        severity_section = """
Moderate tension exists.
Repair should balance accountability and mutual understanding.
"""
    else:
        severity_section = """
Low accumulated tension.
Repair can be light and constructive.
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": f"""
You are generating a repair message in a {category} relationship.

{style_section}

{severity_section}

Generate:
1. Soft Repair Version
2. Direct Accountability Version
3. Deep Reconnection Version

Keep responses emotionally intelligent but natural.
Avoid sounding clinical.
Keep concise.
"""
            },
            {
                "role": "user",
                "content": context
            }
        ]
    )

    return response.choices[0].message.content
