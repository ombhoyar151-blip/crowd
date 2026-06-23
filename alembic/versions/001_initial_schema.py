import sqlalchemy as sa
from alembic import op

revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "cameras",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column("name", sa.String(128), nullable=False),
        sa.Column("source_type", sa.String(16), nullable=False),
        sa.Column("source_url", sa.Text(), default=""),
        sa.Column("is_active", sa.Boolean(), default=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("username", sa.String(64), unique=True, nullable=False, index=True),
        sa.Column("hashed_password", sa.Text(), nullable=False),
        sa.Column("is_active", sa.Boolean(), default=True),
        sa.Column("role", sa.String(16), default="viewer"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    op.create_table(
        "crowd_snapshots",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("time", sa.DateTime(timezone=True), nullable=False, index=True),
        sa.Column("camera_id", sa.String(64), nullable=False, index=True),
        sa.Column("frame_number", sa.Integer(), nullable=False),
        sa.Column("person_count", sa.Integer(), nullable=False),
        sa.Column("density_score", sa.Float(), nullable=False),
        sa.Column("heatmap_path", sa.Text(), nullable=True),
    )

    op.create_table(
        "zone_snapshots",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("snapshot_id", sa.Integer(), sa.ForeignKey("crowd_snapshots.id"), nullable=False),
        sa.Column("time", sa.DateTime(timezone=True), nullable=False, index=True),
        sa.Column("camera_id", sa.String(64), nullable=False),
        sa.Column("zone_id", sa.String(64), nullable=False),
        sa.Column("zone_name", sa.String(128), nullable=False),
        sa.Column("count", sa.Integer(), nullable=False),
        sa.Column("threshold", sa.Integer(), nullable=False),
        sa.Column("is_violated", sa.Boolean(), nullable=False),
    )

    op.create_table(
        "alerts",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("time", sa.DateTime(timezone=True), nullable=False, index=True),
        sa.Column("camera_id", sa.String(64), nullable=False, index=True),
        sa.Column("zone_id", sa.String(64), nullable=False),
        sa.Column("zone_name", sa.String(128), nullable=False),
        sa.Column("count", sa.Integer(), nullable=False),
        sa.Column("threshold", sa.Integer(), nullable=False),
        sa.Column("severity", sa.String(16), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade():
    op.drop_table("alerts")
    op.drop_table("zone_snapshots")
    op.drop_table("crowd_snapshots")
    op.drop_table("users")
    op.drop_table("cameras")
