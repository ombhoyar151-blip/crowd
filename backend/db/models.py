from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from backend.db.base import Base


class CameraORM(Base):
    __tablename__ = "cameras"

    id = Column(String(64), primary_key=True)
    name = Column(String(128), nullable=False)
    source_type = Column(String(16), nullable=False)
    source_url = Column(Text, default="")
    is_active = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class CrowdSnapshotORM(Base):
    __tablename__ = "crowd_snapshots"

    id = Column(Integer, primary_key=True, autoincrement=True)
    time = Column(DateTime(timezone=True), nullable=False, index=True)
    camera_id = Column(String(64), nullable=False, index=True)
    frame_number = Column(Integer, nullable=False)
    person_count = Column(Integer, nullable=False)
    density_score = Column(Float, nullable=False)
    heatmap_path = Column(Text, nullable=True)


class ZoneSnapshotORM(Base):
    __tablename__ = "zone_snapshots"

    id = Column(Integer, primary_key=True, autoincrement=True)
    snapshot_id = Column(Integer, ForeignKey("crowd_snapshots.id"), nullable=False)
    time = Column(DateTime(timezone=True), nullable=False, index=True)
    camera_id = Column(String(64), nullable=False)
    zone_id = Column(String(64), nullable=False)
    zone_name = Column(String(128), nullable=False)
    count = Column(Integer, nullable=False)
    threshold = Column(Integer, nullable=False)
    is_violated = Column(Boolean, nullable=False)


class AlertORM(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    time = Column(DateTime(timezone=True), nullable=False, index=True)
    camera_id = Column(String(64), nullable=False, index=True)
    zone_id = Column(String(64), nullable=False)
    zone_name = Column(String(128), nullable=False)
    count = Column(Integer, nullable=False)
    threshold = Column(Integer, nullable=False)
    severity = Column(String(16), nullable=False)
    message = Column(Text, nullable=False)
    resolved_at = Column(DateTime(timezone=True), nullable=True)


class UserORM(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(64), unique=True, nullable=False, index=True)
    hashed_password = Column(Text, nullable=False)
    is_active = Column(Boolean, default=True)
    role = Column(String(16), default="viewer")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
