from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    JSON,
    Numeric,
    String,
    Text,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Bin(Base):
    __tablename__ = "bins"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(64), unique=True)
    district: Mapped[str] = mapped_column(String(32), index=True)
    lat: Mapped[float] = mapped_column(Float)
    lon: Mapped[float] = mapped_column(Float)
    capacity_l: Mapped[int] = mapped_column(Integer, default=120)
    hardware_id: Mapped[str | None] = mapped_column(String(64), unique=True, nullable=True)
    qr_code: Mapped[str | None] = mapped_column(String(128), unique=True, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    telemetries = relationship("Telemetry", back_populates="bin", cascade="all, delete-orphan")
    classifications = relationship(
        "Classification", back_populates="bin", cascade="all, delete-orphan"
    )


class Telemetry(Base):
    __tablename__ = "telemetry"

    ts: Mapped[datetime] = mapped_column(DateTime, primary_key=True)
    bin_id: Mapped[int] = mapped_column(ForeignKey("bins.id"), primary_key=True, index=True)
    fill_pct: Mapped[float] = mapped_column(Float)
    weight_kg: Mapped[float] = mapped_column(Float)
    temp_c: Mapped[float] = mapped_column(Float)
    humidity_pct: Mapped[float] = mapped_column(Float)
    gas_ppm: Mapped[float] = mapped_column(Float)
    source: Mapped[str] = mapped_column(String(16), default="simulator")

    bin = relationship("Bin", back_populates="telemetries")


class Classification(Base):
    __tablename__ = "classifications"

    id: Mapped[int] = mapped_column(primary_key=True)
    bin_id: Mapped[int] = mapped_column(ForeignKey("bins.id"), index=True)
    ts: Mapped[datetime] = mapped_column(DateTime, index=True)
    waste_class: Mapped[str] = mapped_column(String(16))
    confidence: Mapped[float] = mapped_column(Float)
    item_count: Mapped[int] = mapped_column(Integer, default=1)

    bin = relationship("Bin", back_populates="classifications")


class WQSScore(Base):
    __tablename__ = "wqs_scores"

    id: Mapped[int] = mapped_column(primary_key=True)
    bin_id: Mapped[int] = mapped_column(ForeignKey("bins.id"), index=True)
    ts: Mapped[datetime] = mapped_column(DateTime, index=True)
    wqs: Mapped[float] = mapped_column(Float)
    contamination_pct: Mapped[float] = mapped_column(Float)
    per_class_pct: Mapped[dict] = mapped_column(JSON)


class DCPIScore(Base):
    __tablename__ = "dcpi_scores"

    id: Mapped[int] = mapped_column(primary_key=True)
    bin_id: Mapped[int] = mapped_column(ForeignKey("bins.id"), index=True)
    ts: Mapped[datetime] = mapped_column(DateTime, index=True)
    dcpi: Mapped[float] = mapped_column(Float)
    features: Mapped[dict] = mapped_column(JSON)
    reasons: Mapped[list] = mapped_column(JSON)


class Prediction(Base):
    __tablename__ = "predictions"

    id: Mapped[int] = mapped_column(primary_key=True)
    bin_id: Mapped[int] = mapped_column(ForeignKey("bins.id"), index=True)
    ts_made: Mapped[datetime] = mapped_column(DateTime)
    ts_target: Mapped[datetime] = mapped_column(DateTime, index=True)
    predicted_fill_pct: Mapped[float] = mapped_column(Float)
    horizon_hours: Mapped[int] = mapped_column(Integer)


class Route(Base):
    __tablename__ = "routes"

    id: Mapped[int] = mapped_column(primary_key=True)
    ts: Mapped[datetime] = mapped_column(DateTime, index=True)
    truck_id: Mapped[str] = mapped_column(String(32))
    stops: Mapped[list] = mapped_column(JSON)
    distance_km: Mapped[float] = mapped_column(Float)
    expected_fuel_saving_pct: Mapped[float] = mapped_column(Float)
    expected_co2_saving_kg: Mapped[float] = mapped_column(Float)


class XAIExplanation(Base):
    __tablename__ = "xai_explanations"

    id: Mapped[int] = mapped_column(primary_key=True)
    dcpi_id: Mapped[int] = mapped_column(ForeignKey("dcpi_scores.id"), index=True)
    natural_language: Mapped[str] = mapped_column(Text)
    features: Mapped[list] = mapped_column(JSON)


class Worker(Base):
    __tablename__ = "workers"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(64))
    phone: Mapped[str] = mapped_column(String(24), unique=True)
    district: Mapped[str] = mapped_column(String(32))
    active: Mapped[bool] = mapped_column(Boolean, default=True)


class Collection(Base):
    __tablename__ = "collections"

    id: Mapped[int] = mapped_column(primary_key=True)
    worker_id: Mapped[int] = mapped_column(ForeignKey("workers.id"), index=True)
    bin_id: Mapped[int] = mapped_column(ForeignKey("bins.id"), index=True)
    ts: Mapped[datetime] = mapped_column(DateTime, index=True)
    qr_scan: Mapped[str] = mapped_column(String(128))
    weight_kg: Mapped[float] = mapped_column(Float)
    payment_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2))


class CityEvent(Base):
    __tablename__ = "city_events"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(128))
    district: Mapped[str] = mapped_column(String(32))
    start_ts: Mapped[datetime] = mapped_column(DateTime)
    end_ts: Mapped[datetime] = mapped_column(DateTime)
    expected_multiplier: Mapped[float] = mapped_column(Float, default=1.5)
