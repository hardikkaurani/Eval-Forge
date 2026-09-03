import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database.session import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class DeveloperProfile(Base):
    __tablename__ = "developer_profiles"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    api_key_hash = Column(String(255), nullable=False, unique=True)
    scope = Column(String(255), default="read:all")
    quota_limit = Column(Integer, default=5000)  # Monthly request limit
    request_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), default=_utcnow)
    updated_at = Column(DateTime(timezone=True), default=_utcnow, onupdate=_utcnow)


class WebhookSubscription(Base):
    __tablename__ = "webhook_subscriptions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), nullable=False)
    target_url = Column(String(512), nullable=False)
    secret_token = Column(String(255), nullable=False)
    events = Column(
        JSON, nullable=False
    )  # list of events: ["evaluation.completed", "job.failed"]
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=_utcnow)
    updated_at = Column(DateTime(timezone=True), default=_utcnow, onupdate=_utcnow)

    deliveries = relationship(
        "WebhookDelivery", back_populates="subscription", cascade="all, delete-orphan"
    )


class WebhookOutboxEvent(Base):
    __tablename__ = "webhook_outbox_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(UUID(as_uuid=True), nullable=False)
    event_type = Column(String(100), nullable=False)
    payload = Column(JSON, nullable=False)
    status = Column(String(32), default="PENDING")  # PENDING, PROCESSED, FAILED
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
    created_at = Column(DateTime(timezone=True), default=_utcnow)
    processed_at = Column(DateTime(timezone=True), nullable=True)


class WebhookDelivery(Base):
    __tablename__ = "webhook_deliveries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    subscription_id = Column(
        UUID(as_uuid=True),
        ForeignKey("webhook_subscriptions.id", ondelete="CASCADE"),
        nullable=False,
    )
    event_type = Column(String(100), nullable=False)
    status_code = Column(Integer, nullable=True)
    request_payload = Column(JSON, nullable=False)
    response_body = Column(Text, nullable=True)
    latency_ms = Column(Integer, default=0)
    success = Column(Boolean, default=False)
    attempt_count = Column(Integer, default=1)
    delivered_at = Column(DateTime(timezone=True), default=_utcnow)

    subscription = relationship("WebhookSubscription", back_populates="deliveries")


class PluginDescriptor(Base):
    __tablename__ = "plugin_descriptors"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workspace_id = Column(
        String(36), nullable=True, index=True
    )  # Nullable for system/global plugins
    is_global = Column(Boolean, default=False, nullable=False)
    name = Column(String(128), nullable=False)
    identifier = Column(
        String(128), nullable=False
    )  # e.g. "com.evalforge.custom-metric"
    version = Column(String(32), nullable=False)
    plugin_type = Column(
        String(64), nullable=False
    )  # e.g., "metric", "provider", "exporter"
    capabilities = Column(
        JSON, nullable=False, default=list
    )  # ["metric:compute", "dataset:filter"]
    is_enabled = Column(Boolean, default=True)
    configuration_schema = Column(JSON, nullable=True)
    settings = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), default=_utcnow)
    updated_at = Column(DateTime(timezone=True), default=_utcnow, onupdate=_utcnow)
