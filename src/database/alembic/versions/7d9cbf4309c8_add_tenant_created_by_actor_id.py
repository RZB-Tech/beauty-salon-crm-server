"""add tenant created_by_actor_id

Revision ID: 7d9cbf4309c8
Revises: 0d25cbf1ec1e
Create Date: 2026-08-20 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7d9cbf4309c8'
down_revision: Union[str, Sequence[str], None] = '0d25cbf1ec1e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('tenants', sa.Column('created_by_actor_id', sa.Integer(), nullable=True))
    op.create_index(op.f('ix_tenants_created_by_actor_id'), 'tenants', ['created_by_actor_id'], unique=False)
    op.create_foreign_key('fk_tenants_created_by_actor_id_actors', 'tenants', 'actors', ['created_by_actor_id'], ['id'], ondelete='SET NULL')


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint('fk_tenants_created_by_actor_id_actors', 'tenants', type_='foreignkey')
    op.drop_index(op.f('ix_tenants_created_by_actor_id'), table_name='tenants')
    op.drop_column('tenants', 'created_by_actor_id')
