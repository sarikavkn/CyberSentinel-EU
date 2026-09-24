from datetime import datetime, timezone
from sqlalchemy import String, Integer, Float, DateTime, Text, Boolean, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from .db import Base

def utcnow():
    return datetime.now(timezone.utc)

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(40), default="Viewer")
    active: Mapped[bool] = mapped_column(Boolean, default=True)

class Organization(Base):
    __tablename__ = "organizations"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(200), unique=True)
    country: Mapped[str] = mapped_column(String(2), default="EU")
    sector: Mapped[str] = mapped_column(String(160), default="General")
    employee_band: Mapped[str] = mapped_column(String(80), default="Unknown")
    financial_entity: Mapped[bool] = mapped_column(Boolean, default=False)
    product_manufacturer: Mapped[bool] = mapped_column(Boolean, default=False)
    processes_personal_data: Mapped[bool] = mapped_column(Boolean, default=True)
    essential_service: Mapped[bool] = mapped_column(Boolean, default=False)
    digital_provider_category: Mapped[str] = mapped_column(String(160), default="")
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

class ApplicabilityResult(Base):
    __tablename__ = "applicability_results"
    __table_args__ = (UniqueConstraint("framework", name="uq_applicability_framework"),)
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    framework: Mapped[str] = mapped_column(String(80), index=True)
    result: Mapped[str] = mapped_column(String(40), default="REVIEW")
    confidence: Mapped[str] = mapped_column(String(30), default="Screening")
    reason: Mapped[str] = mapped_column(Text, default="")
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

class Assessment(Base):
    __tablename__ = "assessments"
    __table_args__ = (UniqueConstraint("requirement_code", name="uq_assessment_requirement"),)
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    framework: Mapped[str] = mapped_column(String(80), index=True)
    requirement_code: Mapped[str] = mapped_column(String(120), index=True)
    applicability: Mapped[str] = mapped_column(String(30), default="REVIEW")
    status: Mapped[str] = mapped_column(String(30), default="NOT_ASSESSED")
    maturity: Mapped[int] = mapped_column(Integer, default=0)
    score: Mapped[float] = mapped_column(Float, default=0)
    owner: Mapped[str] = mapped_column(String(120), default="")
    notes: Mapped[str] = mapped_column(Text, default="")
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

class Evidence(Base):
    __tablename__ = "evidence"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    requirement_code: Mapped[str] = mapped_column(String(120), index=True)
    control_id: Mapped[str] = mapped_column(String(80), index=True)
    title: Mapped[str] = mapped_column(String(250))
    source: Mapped[str] = mapped_column(String(250), default="manual")
    evidence_type: Mapped[str] = mapped_column(String(80), default="document")
    status: Mapped[str] = mapped_column(String(30), default="PENDING_REVIEW")
    original_filename: Mapped[str] = mapped_column(String(255), default="")
    stored_filename: Mapped[str] = mapped_column(String(255), default="")
    size_bytes: Mapped[int] = mapped_column(Integer, default=0)
    hash_sha256: Mapped[str] = mapped_column(String(64), default="")
    reviewer: Mapped[str] = mapped_column(String(120), default="")
    notes: Mapped[str] = mapped_column(Text, default="")
    collected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

class Finding(Base):
    __tablename__ = "findings"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    requirement_code: Mapped[str] = mapped_column(String(120), index=True)
    control_id: Mapped[str] = mapped_column(String(80), index=True)
    title: Mapped[str] = mapped_column(String(250))
    severity: Mapped[str] = mapped_column(String(30), default="Medium")
    status: Mapped[str] = mapped_column(String(30), default="OPEN")
    owner: Mapped[str] = mapped_column(String(120), default="")
    due_date: Mapped[str] = mapped_column(String(30), default="")
    remediation: Mapped[str] = mapped_column(Text, default="")
    verification_notes: Mapped[str] = mapped_column(Text, default="")
    details: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

class Risk(Base):
    __tablename__ = "risks"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(250))
    category: Mapped[str] = mapped_column(String(120), default="Cyber")
    likelihood: Mapped[int] = mapped_column(Integer, default=3)
    impact: Mapped[int] = mapped_column(Integer, default=3)
    inherent_score: Mapped[int] = mapped_column(Integer, default=9)
    residual_score: Mapped[int] = mapped_column(Integer, default=9)
    treatment: Mapped[str] = mapped_column(Text, default="")
    owner: Mapped[str] = mapped_column(String(120), default="")
    status: Mapped[str] = mapped_column(String(30), default="OPEN")

class Asset(Base):
    __tablename__ = "assets"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(180), unique=True)
    asset_type: Mapped[str] = mapped_column(String(80), default="System")
    owner: Mapped[str] = mapped_column(String(120), default="")
    criticality: Mapped[str] = mapped_column(String(30), default="Medium")
    internet_exposed: Mapped[bool] = mapped_column(Boolean, default=False)
    contains_personal_data: Mapped[bool] = mapped_column(Boolean, default=False)

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    actor: Mapped[str] = mapped_column(String(100))
    action: Mapped[str] = mapped_column(String(180))
    target: Mapped[str] = mapped_column(String(180), default="")
    details: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
