"""add_is_cover_to_song_table

Revision ID: e01721c38e58
Revises: 51233f56e1f2
Create Date: 2024-08-26 17:11:28.799634

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql as pg

# revision identifiers, used by Alembic.
revision: str = 'e01721c38e58'
down_revision: Union[str, None] = '51233f56e1f2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('songs', sa.Column('is_cover', sa.Boolean, nullable=True, server_default=sa.sql.expression.false(), index=True))
    op.add_column('songs', sa.Column('alternative_names', pg.JSONB, nullable=True))
    op.create_index('idx_alternative_names_gin', 'songs', ['alternative_names'], postgresql_using='gin')
    # ### end Alembic commands ###


def downgrade() -> None:
    op.drop_column('songs', 'is_cover')
    op.drop_column('songs', 'alternative_names')
    # ### end Alembic commands ###
