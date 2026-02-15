import re
from groq import Groq
from config import get_groq_api_key


def analyze_conversation(text: str, category: str):

    api_key = get_groq_api_key()
    if not api_key:
        return None

    client = Groq(api_key=api_key)

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": f"""
You are a professional psychologist analyzing a {category} relationship.

Return ONLY the following format:
- Overall Communication Health: 0-100
- Partner A Behavioral Risk: 0-100
- Partner B Behavioral Risk: 0-100
- Emotional Safety Level: 0-100

No explanations.
"""
            },
            {
                "role": "user",
                "content": text
            }
        ]
    )

    content = response.choices[0].message.content

    scores = re.findall(r":\s*(\d+)", content)

    if len(scores) < 4:
        return None

    return {
        "health": int(scores[0]),
        "risk_a": int(scores[1]),
        "risk_b": int(scores[2]),
        "safety": int(scores[3]),
    }
