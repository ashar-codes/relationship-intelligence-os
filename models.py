from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False)
    name = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    relationships = relationship("Relationship", back_populates="user", cascade="all, delete")

class Relationship(Base):
    __tablename__ = "relationships"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
user = relationship("User", back_populates="relationships")

    name = Column(String, nullable=False)
    relationship_type = Column(String, nullable=False)
    category = Column(String, nullable=False)

    # Style learning
    user_style_summary = Column(Text, nullable=True)
    style_confidence = Column(Integer, default=0)

    # Risk memory
    toxicity_index = Column(Integer, default=0)

    created_at = Column(DateTime, default=datetime.utcnow)

    conversations = relationship("Conversation", back_populates="relationship", cascade="all, delete")


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)

    relationship_id = Column(Integer, ForeignKey("relationships.id"))

    raw_text = Column(Text, nullable=False)

    health_score = Column(Integer)
    safety_score = Column(Integer)
    risk_a = Column(Integer)
    risk_b = Column(Integer)

    created_at = Column(DateTime, default=datetime.utcnow)

    relationship = relationship("Relationship", back_populates="conversations")
