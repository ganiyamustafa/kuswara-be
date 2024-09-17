"""create_user_character_column

Revision ID: 1883996e71d9
Revises: 3c05108c1103
Create Date: 2024-09-15 23:27:33.586029

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1883996e71d9'
down_revision: Union[str, None] = '3c05108c1103'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'user_characters',
        sa.Column('id', sa.UUID(as_uuid=True), nullable=False, primary_key=True, default=sa.text('uuid_generate_v4()')),
        sa.Column('name', sa.String(), nullable=False, index=True),
        sa.Column('code', sa.String(), unique=True, nullable=False, index=True),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('image', sa.String(), nullable=False),
        sa.Column('background_image', sa.String(), nullable=False),
        sa.Column('background_color', sa.String(), nullable=False),
        sa.Column('color_filter', sa.String(), nullable=False),
        sa.Column('primary_color', sa.String(), nullable=False),
        sa.Column('secondary_color', sa.String(), nullable=False),
        sa.Column('text_primary_color', sa.String(), nullable=False),
        sa.Column('text_secondary_color', sa.String(), nullable=False),
    )

    op.create_table(
        'user_character_skills',
        sa.Column('id', sa.UUID(as_uuid=True), nullable=False, primary_key=True, default=sa.text('uuid_generate_v4()')),
        sa.Column('name', sa.String(), nullable=False, index=True),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('image', sa.String(), nullable=False),
        sa.Column('cooldown', sa.Integer(), nullable=False, server_default=sa.text("2")),
        sa.Column('skill_type', sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column('user_character_id', sa.UUID(), sa.ForeignKey('user_characters.id', ondelete='CASCADE'), index=True)
    )

    op.add_column('users', sa.Column('user_character_id', sa.UUID(), sa.ForeignKey('user_characters.id', ondelete='SET NULL'), index=True))


def downgrade() -> None:
    op.drop_column('users', 'user_character_id')
    op.drop_table('user_characters')
    op.drop_table('user_character_skills')
