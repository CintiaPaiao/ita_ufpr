"""Add legacy process event preservation table."""
from alembic import op
import sqlalchemy as sa

revision = "0003_legacy_process_events"
down_revision = "0002_legacy_snapshot"
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    insp = sa.inspect(bind)
    if "eventos_processo_legado" in insp.get_table_names():
        return
    op.create_table(
        "eventos_processo_legado",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("student_id", sa.Integer(), sa.ForeignKey("estudantes.id"), nullable=False, index=True),
        sa.Column("cycle_id", sa.Integer(), sa.ForeignKey("ciclos.id"), nullable=False, index=True),
        sa.Column("source_name", sa.String(240)),
        sa.Column("responsavel_2024", sa.String(160)),
        sa.Column("responsavel_2025_1", sa.String(160)),
        sa.Column("observacoes_1", sa.Text()),
        sa.Column("parecer_1", sa.String(200)),
        sa.Column("situacao_1", sa.String(120)),
        sa.Column("respondeu_recurso_final", sa.String(80)),
        sa.Column("observacoes_2", sa.Text()),
        sa.Column("parecer_2", sa.String(200)),
        sa.Column("situacao_2", sa.String(120)),
        sa.Column("raw_json", sa.Text()),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("student_id", "cycle_id", name="uq_legacy_process_student_cycle"),
    )


def downgrade():
    bind = op.get_bind()
    insp = sa.inspect(bind)
    if "eventos_processo_legado" in insp.get_table_names():
        op.drop_table("eventos_processo_legado")
