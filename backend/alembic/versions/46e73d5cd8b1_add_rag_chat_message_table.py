"""add_rag_chat_message_table

Revision ID: 46e73d5cd8b1
Revises: 14f31d868bd7
Create Date: 2026-04-21 10:40:29.542742

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '46e73d5cd8b1'
down_revision: Union[str, Sequence[str], None] = '14f31d868bd7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # 创建 RAG 对话记录表
    op.create_table(
        'rag_chat_message',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('session_id', sa.Integer(), nullable=False),
        sa.Column('user_question', sa.Text(), nullable=False, comment='用户问题'),
        sa.Column('ai_answer', sa.Text(), nullable=False, comment='AI回答'),
        sa.Column('document_ids', sa.String(length=500), nullable=True, comment='检索的文档ID列表，JSON格式'),
        sa.Column('source_info', sa.Text(), nullable=True, comment='来源文档信息，JSON格式'),
        sa.Column('created_at', sa.DateTime(), nullable=True, comment='创建时间'),
        sa.ForeignKeyConstraint(['session_id'], ['chat_session.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_rag_chat_message_session_id'), 'rag_chat_message', ['session_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_rag_chat_message_session_id'), table_name='rag_chat_message')
    op.drop_table('rag_chat_message')
