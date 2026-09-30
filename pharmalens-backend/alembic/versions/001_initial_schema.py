"""Create the initial PharmaLens database schema."""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


revision: str = "001_initial_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create all seven ORM-backed application tables and indexes."""
    op.create_table(
        "documents",
        sa.Column("filename", sa.String(length=255), nullable=False),
        sa.Column("file_type", sa.String(length=10), nullable=False),
        sa.Column("file_size_bytes", sa.BigInteger(), nullable=False),
        sa.Column("storage_path", sa.String(length=500), nullable=True),
        sa.Column("extracted_text", sa.Text(), nullable=False),
        sa.Column("uploaded_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "file_type IN ('pdf', 'docx')",
            name="ck_documents_file_type",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_documents_uploaded_at", "documents", ["uploaded_at"])

    op.create_table(
        "compliance_templates",
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("version", sa.String(length=50), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("governing_body", sa.String(length=10), nullable=False),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "governing_body IN ('FDA', 'EMA', 'WHO', 'ICH')",
            name="ck_compliance_templates_governing_body",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_compliance_templates_governing_body",
        "compliance_templates",
        ["governing_body"],
    )

    op.create_table(
        "template_sections",
        sa.Column("template_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("section_code", sa.String(length=50), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("requirement_text", sa.Text(), nullable=False),
        sa.Column("mandatory", sa.Boolean(), nullable=False),
        sa.Column("order_index", sa.Integer(), nullable=False),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["template_id"],
            ["compliance_templates.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_template_sections_template_id",
        "template_sections",
        ["template_id"],
    )
    op.create_index(
        "ix_template_sections_template_order",
        "template_sections",
        ["template_id", "order_index"],
    )

    op.create_table(
        "analyses",
        sa.Column("document_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("template_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("compliance_score", sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column("critical_gaps_count", sa.Integer(), nullable=False),
        sa.Column("major_gaps_count", sa.Integer(), nullable=False),
        sa.Column("minor_gaps_count", sa.Integer(), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "status IN ('pending', 'processing', 'completed', 'failed')",
            name="ck_analyses_status",
        ),
        sa.ForeignKeyConstraint(
            ["document_id"],
            ["documents.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["template_id"],
            ["compliance_templates.id"],
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_analyses_document_id", "analyses", ["document_id"])
    op.create_index("ix_analyses_template_id", "analyses", ["template_id"])
    op.create_index("ix_analyses_status", "analyses", ["status"])

    op.create_table(
        "analysis_gaps",
        sa.Column("analysis_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("template_section_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("severity", sa.String(length=20), nullable=False),
        sa.Column("gap_type", sa.String(length=50), nullable=False),
        sa.Column("document_excerpt", sa.Text(), nullable=False),
        sa.Column("gap_description", sa.Text(), nullable=False),
        sa.Column("remediation_guidance", sa.Text(), nullable=False),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "severity IN ('critical', 'major', 'minor')",
            name="ck_analysis_gaps_severity",
        ),
        sa.CheckConstraint(
            "gap_type IN ('missing', 'incomplete', 'non_compliant')",
            name="ck_analysis_gaps_gap_type",
        ),
        sa.ForeignKeyConstraint(
            ["analysis_id"],
            ["analyses.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["template_section_id"],
            ["template_sections.id"],
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_analysis_gaps_analysis_id", "analysis_gaps", ["analysis_id"])
    op.create_index("ix_analysis_gaps_severity", "analysis_gaps", ["severity"])

    op.create_table(
        "corrective_actions",
        sa.Column("analysis_gap_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("action_description", sa.Text(), nullable=False),
        sa.Column("priority", sa.String(length=20), nullable=False),
        sa.Column("regulatory_reference", sa.String(length=100), nullable=False),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "priority IN ('immediate', 'short_term', 'long_term')",
            name="ck_corrective_actions_priority",
        ),
        sa.ForeignKeyConstraint(
            ["analysis_gap_id"],
            ["analysis_gaps.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_corrective_actions_analysis_gap_id",
        "corrective_actions",
        ["analysis_gap_id"],
    )

    op.create_table(
        "audit_logs",
        sa.Column("entity_type", sa.String(length=50), nullable=False),
        sa.Column("entity_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("action", sa.String(length=50), nullable=False),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_audit_logs_entity",
        "audit_logs",
        ["entity_type", "entity_id"],
    )
    op.create_index("ix_audit_logs_timestamp", "audit_logs", ["timestamp"])


def downgrade() -> None:
    """Remove the initial PharmaLens database schema."""
    op.drop_index("ix_audit_logs_timestamp", table_name="audit_logs")
    op.drop_index("ix_audit_logs_entity", table_name="audit_logs")
    op.drop_table("audit_logs")

    op.drop_index(
        "ix_corrective_actions_analysis_gap_id",
        table_name="corrective_actions",
    )
    op.drop_table("corrective_actions")

    op.drop_index("ix_analysis_gaps_severity", table_name="analysis_gaps")
    op.drop_index("ix_analysis_gaps_analysis_id", table_name="analysis_gaps")
    op.drop_table("analysis_gaps")

    op.drop_index("ix_analyses_status", table_name="analyses")
    op.drop_index("ix_analyses_template_id", table_name="analyses")
    op.drop_index("ix_analyses_document_id", table_name="analyses")
    op.drop_table("analyses")

    op.drop_index(
        "ix_template_sections_template_order",
        table_name="template_sections",
    )
    op.drop_index("ix_template_sections_template_id", table_name="template_sections")
    op.drop_table("template_sections")

    op.drop_index(
        "ix_compliance_templates_governing_body",
        table_name="compliance_templates",
    )
    op.drop_table("compliance_templates")

    op.drop_index("ix_documents_uploaded_at", table_name="documents")
    op.drop_table("documents")
