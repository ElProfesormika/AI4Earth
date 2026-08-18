"""TimescaleDB hypertable for telemetry

Revision ID: 002_timescale_hypertable
Revises: 001_initial
"""
from typing import Sequence, Union

from alembic import op

revision: str = "002_timescale_hypertable"
down_revision: Union[str, None] = "001_initial"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS timescaledb;")
    op.execute("SELECT create_hypertable('telemetry', 'ts', if_not_exists => TRUE);")
    op.execute("CREATE INDEX IF NOT EXISTS ix_telemetry_bin_ts ON telemetry (bin_id, ts DESC);")


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_telemetry_bin_ts;")
