"""Add workspace ownership without assigning or deleting legacy records."""
from alembic import op
import sqlalchemy as sa
from app.database.metadata import metadata

revision = "86b4d920a001"
down_revision = "da810021276a"
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    for name in ("clinic_leads", "collaboration_sessions"):
        inspector = sa.inspect(bind)
        if not inspector.has_table(name):
            metadata.tables[name].create(bind)
            continue
        columns = {column["name"] for column in inspector.get_columns(name)}
        if "business_uid" not in columns:
            op.add_column(name, sa.Column("business_uid", sa.String(), nullable=True))
        indexes = {index["name"] for index in sa.inspect(bind).get_indexes(name)}
        index_name = f"ix_{name}_business_uid"
        if index_name not in indexes:
            op.create_index(index_name, name, ["business_uid"], unique=False)


def downgrade():
    raise RuntimeError("Ownership downgrade is disabled to preserve isolation and data.")
