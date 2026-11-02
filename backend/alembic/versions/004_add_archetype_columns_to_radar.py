"""add archetype and gap columns to market_opportunities

Revision ID: 004
Revises: 003
Create Date: 2026-11-02

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "004"
down_revision: Union[str, None] = "003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "market_opportunities",
        sa.Column("is_archetype", sa.Boolean(), nullable=False, server_default="false"),
    )
    op.add_column(
        "market_opportunities",
        sa.Column("leverage_score", sa.Float(), nullable=True),
    )
    op.add_column(
        "market_opportunities",
        sa.Column("gap_type", sa.String(length=100), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("market_opportunities", "gap_type")
    op.drop_column("market_opportunities", "leverage_score")
    op.drop_column("market_opportunities", "is_archetype")
