from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from app.db.base import Base


class EmailTemplate(Base):
    """Email template model for reusable email designs"""
    
    __tablename__ = "email_templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=False, default="general")  # welcome, promotional, newsletter, transactional
    subject = Column(String(500), nullable=False)
    html_content = Column(Text, nullable=False)
    plain_text_content = Column(Text, nullable=True)
    
    # Template variables/placeholders documentation
    available_variables = Column(Text, nullable=True)  # JSON string of available variables
    
    # Status and metadata
    is_active = Column(Boolean, default=True)
    is_default = Column(Boolean, default=False)
    
    # Usage tracking
    usage_count = Column(Integer, default=0)
    last_used_at = Column(DateTime, nullable=True)
    
    # Ownership
    created_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<EmailTemplate(id={self.id}, name='{self.name}', category='{self.category}')>"

