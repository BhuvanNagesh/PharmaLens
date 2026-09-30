"""Enable deny-by-default RLS on every exposed application table."""

from typing import Sequence, Union

from alembic import op


revision: str = "002_enable_public_rls"
down_revision: Union[str, None] = "001_initial_schema"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_RLS_STATEMENTS = (
    "ALTER TABLE public.alembic_version ENABLE ROW LEVEL SECURITY",
    "ALTER TABLE public.documents ENABLE ROW LEVEL SECURITY",
    "ALTER TABLE public.compliance_templates ENABLE ROW LEVEL SECURITY",
    "ALTER TABLE public.template_sections ENABLE ROW LEVEL SECURITY",
    "ALTER TABLE public.analyses ENABLE ROW LEVEL SECURITY",
    "ALTER TABLE public.analysis_gaps ENABLE ROW LEVEL SECURITY",
    "ALTER TABLE public.corrective_actions ENABLE ROW LEVEL SECURITY",
    "ALTER TABLE public.audit_logs ENABLE ROW LEVEL SECURITY",
)


def upgrade() -> None:
    """Enable RLS without adding public data-access policies."""
    for statement in _RLS_STATEMENTS:
        op.execute(statement)


def downgrade() -> None:
    """Disable RLS when explicitly rolling back this security migration."""
    for statement in reversed(_RLS_STATEMENTS):
        op.execute(statement.replace(" ENABLE ", " DISABLE "))
