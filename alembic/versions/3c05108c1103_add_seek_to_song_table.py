"""add_seek_to_song_table

Revision ID: 3c05108c1103
Revises: e01721c38e58
Create Date: 2024-09-12 01:22:10.810482

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3c05108c1103'
down_revision: Union[str, None] = 'e01721c38e58'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('songs', sa.Column('seek', sa.String, nullable=False, server_default="0,30,60", index=True))


def downgrade() -> None:
    op.drop_column('songs', 'seek')
