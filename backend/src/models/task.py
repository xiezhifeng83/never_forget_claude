"""
Task SQLAlchemy model.

Per data-model.md: Task entity with UUID, device token, text, position, timestamps.
"""

from sqlalchemy import Column, String, Integer, CheckConstraint, Index
from sqlalchemy.dialects.postgresql import UUID as PostgreSQLUUID
from sqlalchemy.sql import func
from sqlalchemy.types import DateTime, TypeDecorator, CHAR
import uuid

from backend.src.database import Base, DATABASE_URL


# Database-agnostic UUID type
class UUID(TypeDecorator):
    """Platform-independent GUID type.
    Uses PostgreSQL's UUID type if available, otherwise uses CHAR(36).
    """
    impl = CHAR
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(PostgreSQLUUID(as_uuid=True))
        else:
            return dialect.type_descriptor(CHAR(36))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return value
        else:
            if isinstance(value, uuid.UUID):
                return str(value)
            return value

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return value
        else:
            if isinstance(value, str):
                return uuid.UUID(value)
            return value


class Task(Base):
    """
    Task model representing a todo item.

    Attributes:
        id: UUID primary key (client-generated)
        device_token: UUID of the device that owns this task
        text: Task description (max 500 chars)
        position: Ordinal position (0 = top priority)
        created_at: UTC timestamp when task was created
        updated_at: UTC timestamp of last modification

    Constraints:
        - text must not be empty after trimming
        - position must be >= 0
        - updated_at must be >= created_at

    Indexes:
        - device_token: for filtering tasks by device
        - (device_token, position): for ordered retrieval
        - updated_at: for sync queries
    """

    __tablename__ = "tasks"

    # Primary key - client-generated UUID
    id = Column(
        UUID(),
        primary_key=True,
        default=uuid.uuid4,
        nullable=False,
    )

    # Device token that owns this task
    device_token = Column(
        UUID(),
        nullable=False,
        index=True,
    )

    # Task description/content
    text = Column(
        String(500),
        nullable=False,
    )

    # Ordinal position (0 = first/top priority)
    position = Column(
        Integer,
        nullable=False,
        default=0,
    )

    # Timestamps
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Table constraints per data-model.md
    __table_args__ = (
        # Text must not be empty after trimming
        CheckConstraint(
            "length(trim(text)) > 0",
            name="check_text_not_empty"
        ),
        # Position must be >= 0
        CheckConstraint(
            "position >= 0",
            name="check_position_non_negative"
        ),
        # Updated timestamp must be >= created timestamp
        CheckConstraint(
            "updated_at >= created_at",
            name="check_updated_after_created"
        ),
        # Composite index for ordered retrieval per device
        Index("idx_tasks_device_position", "device_token", "position"),
        # Index for sync queries
        Index("idx_tasks_updated_at", "updated_at"),
    )

    def __repr__(self):
        return f"<Task(id={self.id}, text='{self.text[:30]}...', position={self.position})>"
