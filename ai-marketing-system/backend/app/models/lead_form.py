"""
Lead Form Model

Database model for website lead capture forms.
"""

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.base import Base


class LeadForm(Base):
    """Website lead capture form"""

    __tablename__ = "lead_forms"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    slug = Column(String, unique=True, index=True, nullable=False)  # URL-friendly identifier

    # Form configuration
    title = Column(String, nullable=False)
    description = Column(Text)
    submit_button_text = Column(String, default="Submit")
    success_message = Column(Text, default="Thank you! We'll be in touch soon.")

    # Fields configuration (JSON array of field definitions)
    fields = Column(JSON, nullable=False)  # [{ name, type, label, required, placeholder, options }]

    # Design settings
    theme_color = Column(String, default="#2563eb")  # Primary color (blue-600)
    background_color = Column(String, default="#ffffff")
    text_color = Column(String, default="#111827")

    # Behavior settings
    redirect_url = Column(String)  # Optional redirect after submission
    enable_double_optin = Column(Boolean, default=False)
    require_consent = Column(Boolean, default=True)
    consent_text = Column(Text, default="I agree to receive marketing communications")

    # Security & Spam Protection
    enable_recaptcha = Column(Boolean, default=False)
    enable_honeypot = Column(Boolean, default=True)  # Hidden field for spam bots
    rate_limit_enabled = Column(Boolean, default=True)
    max_submissions_per_ip = Column(Integer, default=5)  # Per hour

    # Status & Tracking
    is_active = Column(Boolean, default=True)
    submission_count = Column(Integer, default=0)

    # Metadata
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    submissions = relationship("LeadFormSubmission", back_populates="form", cascade="all, delete-orphan")


class LeadFormSubmission(Base):
    """Individual form submission record"""

    __tablename__ = "lead_form_submissions"

    id = Column(Integer, primary_key=True, index=True)
    form_id = Column(Integer, ForeignKey("lead_forms.id"), nullable=False)

    # Submission data
    data = Column(JSON, nullable=False)  # The actual form field values

    # Meta information
    ip_address = Column(String)
    user_agent = Column(Text)
    referrer = Column(Text)

    # Processing status
    status = Column(String, default="pending")  # pending, processed, spam, error
    lead_id = Column(Integer, ForeignKey("leads.id"), nullable=True)  # Created lead reference
    error_message = Column(Text)

    # Timestamps
    submitted_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime)

    # Relationships
    form = relationship("LeadForm", back_populates="submissions")
