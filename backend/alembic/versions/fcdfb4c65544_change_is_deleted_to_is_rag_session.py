"""change_is_deleted_to_is_rag_session

Revision ID: fcdfb4c65544
Revises: 46e73d5cd8b1
Create Date: 2026-04-21 16:46:59.153781

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fcdfb4c65544'
down_revision: Union[str, Sequence[str], None] = '46e73d5cd8b1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # 删除 is_deleted 列
    op.drop_column('chat_session', 'is_deleted')
    
    # 添加 is_rag_session 列
    op.add_column('chat_session',
        sa.Column('is_rag_session', sa.Boolean(), default=False, nullable=False)
    )


def downgrade() -> None:
    """Downgrade schema."""
    # 删除 is_rag_session 列
    op.drop_column('chat_session', 'is_rag_session')
    
    # 添加 is_deleted 列
    op.add_column('chat_session',
        sa.Column('is_deleted', sa.Boolean(), default=False, nullable=False)
    )
