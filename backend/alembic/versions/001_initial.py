"""Initial schema

Revision ID: 001_initial
Revises:
Create Date: 2026-08-17
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "bins",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=64), nullable=False),
        sa.Column("district", sa.String(length=32), nullable=False),
        sa.Column("lat", sa.Float(), nullable=False),
        sa.Column("lon", sa.Float(), nullable=False),
        sa.Column("capacity_l", sa.Integer(), nullable=False),
        sa.Column("hardware_id", sa.String(length=64), nullable=True),
        sa.Column("qr_code", sa.String(length=128), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("hardware_id"),
        sa.UniqueConstraint("name"),
        sa.UniqueConstraint("qr_code"),
    )
    op.create_index(op.f("ix_bins_district"), "bins", ["district"], unique=False)

    op.create_table(
        "city_events",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("district", sa.String(length=32), nullable=False),
        sa.Column("start_ts", sa.DateTime(), nullable=False),
        sa.Column("end_ts", sa.DateTime(), nullable=False),
        sa.Column("expected_multiplier", sa.Float(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "workers",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=64), nullable=False),
        sa.Column("phone", sa.String(length=24), nullable=False),
        sa.Column("district", sa.String(length=32), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("phone"),
    )

    op.create_table(
        "telemetry",
        sa.Column("ts", sa.DateTime(), nullable=False),
        sa.Column("bin_id", sa.Integer(), nullable=False),
        sa.Column("fill_pct", sa.Float(), nullable=False),
        sa.Column("weight_kg", sa.Float(), nullable=False),
        sa.Column("temp_c", sa.Float(), nullable=False),
        sa.Column("humidity_pct", sa.Float(), nullable=False),
        sa.Column("gas_ppm", sa.Float(), nullable=False),
        sa.Column("source", sa.String(length=16), nullable=False),
        sa.ForeignKeyConstraint(["bin_id"], ["bins.id"]),
        sa.PrimaryKeyConstraint("ts", "bin_id"),
    )
    op.create_index(op.f("ix_telemetry_bin_id"), "telemetry", ["bin_id"], unique=False)

    op.create_table(
        "classifications",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("bin_id", sa.Integer(), nullable=False),
        sa.Column("ts", sa.DateTime(), nullable=False),
        sa.Column("waste_class", sa.String(length=16), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("item_count", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["bin_id"], ["bins.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_classifications_bin_id"), "classifications", ["bin_id"], unique=False)
    op.create_index(op.f("ix_classifications_ts"), "classifications", ["ts"], unique=False)

    op.create_table(
        "wqs_scores",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("bin_id", sa.Integer(), nullable=False),
        sa.Column("ts", sa.DateTime(), nullable=False),
        sa.Column("wqs", sa.Float(), nullable=False),
        sa.Column("contamination_pct", sa.Float(), nullable=False),
        sa.Column("per_class_pct", sa.JSON(), nullable=False),
        sa.ForeignKeyConstraint(["bin_id"], ["bins.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_wqs_scores_bin_id"), "wqs_scores", ["bin_id"], unique=False)
    op.create_index(op.f("ix_wqs_scores_ts"), "wqs_scores", ["ts"], unique=False)

    op.create_table(
        "dcpi_scores",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("bin_id", sa.Integer(), nullable=False),
        sa.Column("ts", sa.DateTime(), nullable=False),
        sa.Column("dcpi", sa.Float(), nullable=False),
        sa.Column("features", sa.JSON(), nullable=False),
        sa.Column("reasons", sa.JSON(), nullable=False),
        sa.ForeignKeyConstraint(["bin_id"], ["bins.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_dcpi_scores_bin_id"), "dcpi_scores", ["bin_id"], unique=False)
    op.create_index(op.f("ix_dcpi_scores_ts"), "dcpi_scores", ["ts"], unique=False)

    op.create_table(
        "predictions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("bin_id", sa.Integer(), nullable=False),
        sa.Column("ts_made", sa.DateTime(), nullable=False),
        sa.Column("ts_target", sa.DateTime(), nullable=False),
        sa.Column("predicted_fill_pct", sa.Float(), nullable=False),
        sa.Column("horizon_hours", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["bin_id"], ["bins.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_predictions_bin_id"), "predictions", ["bin_id"], unique=False)
    op.create_index(op.f("ix_predictions_ts_target"), "predictions", ["ts_target"], unique=False)

    op.create_table(
        "routes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("ts", sa.DateTime(), nullable=False),
        sa.Column("truck_id", sa.String(length=32), nullable=False),
        sa.Column("stops", sa.JSON(), nullable=False),
        sa.Column("distance_km", sa.Float(), nullable=False),
        sa.Column("expected_fuel_saving_pct", sa.Float(), nullable=False),
        sa.Column("expected_co2_saving_kg", sa.Float(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_routes_ts"), "routes", ["ts"], unique=False)

    op.create_table(
        "xai_explanations",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("dcpi_id", sa.Integer(), nullable=False),
        sa.Column("natural_language", sa.Text(), nullable=False),
        sa.Column("features", sa.JSON(), nullable=False),
        sa.ForeignKeyConstraint(["dcpi_id"], ["dcpi_scores.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_xai_explanations_dcpi_id"), "xai_explanations", ["dcpi_id"], unique=False)

    op.create_table(
        "collections",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("worker_id", sa.Integer(), nullable=False),
        sa.Column("bin_id", sa.Integer(), nullable=False),
        sa.Column("ts", sa.DateTime(), nullable=False),
        sa.Column("qr_scan", sa.String(length=128), nullable=False),
        sa.Column("weight_kg", sa.Float(), nullable=False),
        sa.Column("payment_amount", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.ForeignKeyConstraint(["bin_id"], ["bins.id"]),
        sa.ForeignKeyConstraint(["worker_id"], ["workers.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_collections_bin_id"), "collections", ["bin_id"], unique=False)
    op.create_index(op.f("ix_collections_ts"), "collections", ["ts"], unique=False)
    op.create_index(op.f("ix_collections_worker_id"), "collections", ["worker_id"], unique=False)


def downgrade() -> None:
    op.drop_table("collections")
    op.drop_table("xai_explanations")
    op.drop_table("routes")
    op.drop_table("predictions")
    op.drop_table("dcpi_scores")
    op.drop_table("wqs_scores")
    op.drop_table("classifications")
    op.drop_table("telemetry")
    op.drop_table("workers")
    op.drop_table("city_events")
    op.drop_table("bins")
