from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


# ======================================================
# USER MODEL (AUTH + PROFILE)
# ======================================================
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    # Authentication
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=True)  # Null for Google users

    # Profile
    name = Column(String)
    gender = Column(String)  # Male / Female / Other
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships owned by user
    relationships = relationship(
        "Relationship",
        back_populates="user",
        cascade="all, delete-orphan"
    )


# ======================================================
# RELATIONSHIP MODEL
# ======================================================
class Relationship(Base):
    __tablename__ = "relationships"

    id = Column(Integer, primary_key=True, index=True)

    # Owner
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    user = relationship("User", back_populates="relationships")

    # Basic Info
    name = Column(String, nullable=False)  # Person name
    relationship_type = Column(String, nullable=False)  # boyfriend, boss, etc.
    category = Column(String, nullable=False)  # Romantic, Professional, Family

    # AI Behavioral Memory
    user_style_summary = Column(Text, nullable=True)
    style_confidence = Column(Integer, default=0)
    toxicity_index = Column(Integer, default=0)

    # Optional Psychological Extensions (future-ready)
    person_gender = Column(String, nullable=True)
    emotional_style = Column(String, nullable=True)
    attachment_style = Column(String, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    # Conversations
    conversations = relationship(
        "Conversation",
        back_populates="relationship",
        cascade="all, delete-orphan"
    )


# ======================================================
# CONVERSATION MODEL
# ======================================================
class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)

    relationship_id = Column(Integer, ForeignKey("relationships.id", ondelete="CASCADE"))
    relationship = relationship("Relationship", back_populates="conversations")

    raw_text = Column(Text, nullable=False)

    # AI Scoring
    health_score = Column(Integer)
    safety_score = Column(Integer)
    risk_a = Column(Integer)
    risk_b = Column(Integer)

    created_at = Column(DateTime, default=datetime.utcnow)
