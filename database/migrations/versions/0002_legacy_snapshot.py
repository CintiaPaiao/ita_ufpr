"""Add legacy academic snapshot table for ITA-2025-compatible input."""
from alembic import op
from src.models.models import LegacyAcademicSnapshot
revision="0002_legacy_snapshot"
down_revision="0001_initial"
branch_labels=None
depends_on=None

def upgrade():
    LegacyAcademicSnapshot.__table__.create(op.get_bind(), checkfirst=True)

def downgrade():
    LegacyAcademicSnapshot.__table__.drop(op.get_bind(), checkfirst=True)
