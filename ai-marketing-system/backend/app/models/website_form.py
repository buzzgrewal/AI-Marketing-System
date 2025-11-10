"""
Website Form Models
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base


class WebsiteForm(Base):
    """Model for website lead generation forms"""
    __tablename__ = "website_forms"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    fields = Column(JSON, nullable=False)  # Stores form field configuration
    submit_text = Column(String(100), default="Submit")
    success_message = Column(Text, default="Thank you for your submission!")
    is_active = Column(Boolean, default=True)
    embed_code = Column(Text)  # Stores generated embed script
    submission_count = Column(Integer, default=0)
    conversion_rate = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="website_forms")
    submissions = relationship("FormSubmission", back_populates="form", cascade="all, delete-orphan")


class FormSubmission(Base):
    """Model for storing form submissions"""
    __tablename__ = "form_submissions"

    id = Column(Integer, primary_key=True, index=True)
    form_id = Column(Integer, ForeignKey("website_forms.id"), nullable=False)
    data = Column(JSON, nullable=False)  # Stores submitted form data
    source_url = Column(String(500))  # URL where form was submitted from
    ip_address = Column(String(45))  # Store IP for analytics
    user_agent = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    form = relationship("WebsiteForm", back_populates="submissions")