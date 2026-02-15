from groq import Groq
from config import get_groq_api_key


def generate_block_responses(
    context: str,
    category: str,
    style_summary: str | None,
    toxicity_index: int
):
    """
    Generate strategic responses when user is stuck.
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

    toxicity_context = ""
    if toxicity_index > 50:
        toxicity_context = """
The relationship currently has elevated tension.
Prioritize de-escalation and emotional safety.
"""
    elif toxicity_index > 20:
        toxicity_context = """
There are mild recurring tensions.
Balance assertiveness with calm tone.
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": f"""
You are a communication strategist helping in a {category} relationship.

{style_section}

{toxicity_context}

Generate three distinct responses:

1. Emotional Bridge Response
2. Assertive Boundary Response
3. De-escalation Response

Keep responses realistic and natural.
Avoid therapist language.
Keep them concise.
"""
            },
            {
                "role": "user",
                "content": context
            }
        ]
    )

    return response.choices[0].message.content
