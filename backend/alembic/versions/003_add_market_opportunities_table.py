"""add market_opportunities table

Revision ID: 003
Revises: 002
Create Date: 2026-11-02

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "market_opportunities",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("ml_id", sa.String(length=50), nullable=False),
        sa.Column("title", sa.String(length=500), nullable=False),
        sa.Column("category_name", sa.String(length=100), nullable=False, server_default="General"),
        sa.Column("price", sa.Float(), nullable=False),
        sa.Column("target_supplier_cost", sa.Float(), nullable=False),
        sa.Column("target_profit", sa.Float(), nullable=False),
        sa.Column("estimated_monthly_sales", sa.Float(), nullable=True),
        sa.Column("score", sa.Float(), nullable=False),
        sa.Column("demand_score", sa.Float(), nullable=True),
        sa.Column("competition_score", sa.Float(), nullable=False),
        sa.Column("permalink", sa.String(length=1000), nullable=False),
        sa.Column("thumbnail_url", sa.String(length=1000), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="active"),
        sa.Column("detected_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("ml_id"),
    )
    op.create_index(op.f("ix_market_opportunities_ml_id"), "market_opportunities", ["ml_id"], unique=True)
    op.create_index(op.f("ix_market_opportunities_status"), "market_opportunities", ["status"], unique=False)
    op.create_index(op.f("ix_market_opportunities_detected_at"), "market_opportunities", ["detected_at"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_market_opportunities_detected_at"), table_name="market_opportunities")
    op.drop_index(op.f("ix_market_opportunities_status"), table_name="market_opportunities")
    op.drop_index(op.f("ix_market_opportunities_ml_id"), table_name="market_opportunities")
    op.drop_table("market_opportunities")
