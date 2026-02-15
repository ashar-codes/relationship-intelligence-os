from models import Relationship
from sqlalchemy.orm import Session


def update_toxicity_memory(
    db: Session,
    relationship: Relationship,
    health: int,
    safety: int,
    risk_a: int,
    risk_b: int
):

    toxicity = relationship.toxicity_index or 0

    # Escalation detection
    if risk_b > 70 or safety < 30:
        toxicity += 5

    elif risk_b > 50:
        toxicity += 3

    # Repair detection
    if safety > 70 and health > 70:
        toxicity = max(0, toxicity - 2)

    # Cap toxicity
    toxicity = min(100, toxicity)

    relationship.toxicity_index = toxicity

    db.commit()

    return toxicity


def apply_health_cap(health: int, toxicity: int):
    """
    Health cannot exceed (100 - toxicity influence)
    """

    cap = max(40, 100 - toxicity)
    return min(health, cap)
