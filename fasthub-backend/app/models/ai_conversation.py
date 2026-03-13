"""
AIConversation + AIGenerationLog models — AI chat history and usage tracking.
"""

from sqlalchemy import Boolean, Column, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from fasthub_core.db.base import BaseModel


class AIConversation(BaseModel):
    __tablename__ = "ai_conversations"

    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)

    context = Column(String(30), nullable=False)  # validation, structure, editing, config
    messages_json = Column(JSONB, default=list)

    model_used = Column(String(50))
    total_tokens_in = Column(Integer, default=0)
    total_tokens_out = Column(Integer, default=0)

    # Relations
    project = relationship("Project", back_populates="ai_conversations")

    def __repr__(self):
        return f"<AIConversation {self.context} project={self.project_id}>"


class AIGenerationLog(BaseModel):
    __tablename__ = "ai_generation_logs"

    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="SET NULL"), nullable=True, index=True)
    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id"), nullable=False, index=True)

    action = Column(String(30), nullable=False)  # validate, generate_structure, generate_content, chat, visual_review, generate_legal
    model = Column(String(50), nullable=False)

    prompt_preview = Column(String(500))
    tokens_in = Column(Integer, default=0)
    tokens_out = Column(Integer, default=0)
    cost_usd = Column(Float, default=0.0)
    duration_ms = Column(Integer)

    # Vision
    screenshots_count = Column(Integer, default=0)
    iterations = Column(Integer, default=1)

    success = Column(Boolean, default=True)
    error_message = Column(Text)

    def __repr__(self):
        return f"<AIGenerationLog {self.action} ({self.model})>"
