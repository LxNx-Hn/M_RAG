"""auth and paper hardening

Revision ID: 20260414_000002
Revises: 20260414_000001
Create Date: 2026-04-14 16:10:00
"""

from alembic import op
import sqlalchemy as sa

revision = "20260414_000002"
down_revision = "20260414_000001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "revoked_tokens",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("jti", sa.String(length=128), nullable=False),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_revoked_tokens_user_id", "revoked_tokens", ["user_id"], unique=False
    )
    op.create_index("ix_revoked_tokens_jti", "revoked_tokens", ["jti"], unique=True)

    op.execute("DELETE FROM conversations WHERE user_id IS NULL")
    with op.batch_alter_table("conversations") as batch:
        batch.alter_column(
            "user_id", existing_type=sa.String(length=36), nullable=False
        )

    with op.batch_alter_table("papers") as batch:
        batch.add_column(
            sa.Column(
                "doc_type", sa.String(length=32), nullable=True, server_default="paper"
            )
        )
    op.execute("UPDATE papers SET doc_type = 'paper' WHERE doc_type IS NULL")

    op.execute("DELETE FROM papers WHERE user_id IS NULL")
    with op.batch_alter_table("papers") as batch:
        batch.alter_column(
            "user_id", existing_type=sa.String(length=36), nullable=False
        )
        batch.drop_index("ix_papers_doc_id")
        batch.create_index("ix_papers_doc_id", ["doc_id"], unique=False)
        batch.create_index(
            "uq_papers_user_collection_doc",
            ["user_id", "collection_name", "doc_id"],
            unique=True,
        )
        batch.alter_column(
            "doc_type",
            existing_type=sa.String(length=32),
            nullable=False,
            server_default=None,
        )


def downgrade() -> None:
    with op.batch_alter_table("papers") as batch:
        batch.drop_index("uq_papers_user_collection_doc")
        batch.drop_index("ix_papers_doc_id")
        batch.create_index("ix_papers_doc_id", ["doc_id"], unique=True)
        batch.drop_column("doc_type")

    with op.batch_alter_table("conversations") as batch:
        batch.alter_column("user_id", existing_type=sa.String(length=36), nullable=True)

    op.drop_index("ix_revoked_tokens_jti", table_name="revoked_tokens")
    op.drop_index("ix_revoked_tokens_user_id", table_name="revoked_tokens")
    op.drop_table("revoked_tokens")
