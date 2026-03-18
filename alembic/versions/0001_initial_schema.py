"""initial schema

Revision ID: 0001_initial
Revises: None
Create Date: 2026-03-16

"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "organizations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("status", sa.Enum("active", "suspended", name="orgstatus"), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )

    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=True),
        sa.Column("email_verified_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("email", name="uq_users_email"),
    )

    op.create_table(
        "org_members",
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), primary_key=True, nullable=False),
        sa.Column("org_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="CASCADE"), primary_key=True, nullable=False),
        sa.Column("role", sa.Enum("owner", "admin", "member", "viewer", name="orgrole"), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_org_members_org_id", "org_members", ["org_id"])

    op.create_table(
        "sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("org_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("token_hash", sa.LargeBinary(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("last_active_at", sa.DateTime(), nullable=False),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.Column("ip", sa.String(length=64), nullable=True),
        sa.Column("user_agent", sa.String(length=512), nullable=True),
        sa.Column("revoked_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_sessions_user_id", "sessions", ["user_id"])
    op.create_index("ix_sessions_org_id", "sessions", ["org_id"])

    op.create_table(
        "otp_challenges",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("code_hmac", sa.LargeBinary(), nullable=False),
        sa.Column("purpose", sa.Enum("login", name="otppurpose"), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.Column("attempts", sa.Integer(), nullable=False),
        sa.Column("consumed_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_otp_challenges_email", "otp_challenges", ["email"])

    op.create_table(
        "contracts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("org_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(length=300), nullable=False),
        sa.Column("counterparty", sa.String(length=300), nullable=True),
        sa.Column("status", sa.Enum("draft", "in_review", "approved", "sent", "executed", "archived", name="contractstatus"), nullable=False),
        sa.Column("owner_user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_contracts_org_id", "contracts", ["org_id"])
    op.create_index("ix_contracts_status", "contracts", ["status"])

    op.create_table(
        "contract_versions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("contract_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("contracts.id", ondelete="CASCADE"), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("pdf_object_key", sa.String(length=500), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("contract_id", "version", name="uq_contract_versions_contract_version"),
    )
    op.create_index("ix_contract_versions_contract_id", "contract_versions", ["contract_id"])

    op.create_table(
        "contract_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("contract_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("contracts.id", ondelete="CASCADE"), nullable=False),
        sa.Column("type", sa.Enum("created", "version_added", "approved", "sent", "status_changed", name="contracteventtype"), nullable=False),
        sa.Column("actor_user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_contract_events_contract_id", "contract_events", ["contract_id"])

    op.create_table(
        "contract_attachments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("contract_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("contracts.id", ondelete="CASCADE"), nullable=False),
        sa.Column("object_key", sa.String(length=800), nullable=False),
        sa.Column("filename", sa.String(length=300), nullable=False),
        sa.Column("content_type", sa.String(length=200), nullable=True),
        sa.Column("size_bytes", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_contract_attachments_contract_id", "contract_attachments", ["contract_id"])

    op.create_table(
        "products",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("org_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("org_id", "name", name="uq_products_org_name"),
    )
    op.create_index("ix_products_org_id", "products", ["org_id"])

    op.create_table(
        "licenses",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("org_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("product_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("products.id", ondelete="CASCADE"), nullable=False),
        sa.Column("customer_ref", sa.String(length=200), nullable=True),
        sa.Column("status", sa.Enum("active", "revoked", "expired", name="licensestatus"), nullable=False),
        sa.Column("issued_at", sa.DateTime(), nullable=False),
        sa.Column("expires_at", sa.DateTime(), nullable=True),
        sa.Column("max_seats", sa.Integer(), nullable=True),
        sa.Column("metadata_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
    )
    op.create_index("ix_licenses_org_id", "licenses", ["org_id"])
    op.create_index("ix_licenses_product_id", "licenses", ["product_id"])

    op.create_table(
        "license_signing_keys",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("org_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("kid", sa.String(length=100), nullable=False),
        sa.Column("public_key_pem", sa.Text(), nullable=False),
        sa.Column("private_key_pem", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("revoked_at", sa.DateTime(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.UniqueConstraint("org_id", "kid", name="uq_license_keys_org_kid"),
    )
    op.create_index("ix_license_keys_org_id", "license_signing_keys", ["org_id"])

    op.create_table(
        "activations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("license_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("licenses.id", ondelete="CASCADE"), nullable=False),
        sa.Column("machine_fingerprint_hash", sa.LargeBinary(), nullable=False),
        sa.Column("first_seen_at", sa.DateTime(), nullable=False),
        sa.Column("last_seen_at", sa.DateTime(), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.UniqueConstraint("license_id", "machine_fingerprint_hash", name="uq_activations_license_machine"),
    )
    op.create_index("ix_activations_license_id", "activations", ["license_id"])

    op.create_table(
        "revocations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("license_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("licenses.id", ondelete="CASCADE"), nullable=False),
        sa.Column("reason", sa.String(length=300), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_revocations_license_id", "revocations", ["license_id"])

    op.create_table(
        "invoices",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("org_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("customer_ref", sa.String(length=200), nullable=True),
        sa.Column("status", sa.Enum("draft", "open", "paid", "void", "past_due", name="invoicestatus"), nullable=False),
        sa.Column("currency", sa.String(length=10), nullable=False),
        sa.Column("due_date", sa.DateTime(), nullable=True),
        sa.Column("total_cents", sa.Integer(), nullable=False),
        sa.Column("provider", sa.String(length=50), nullable=False),
        sa.Column("provider_invoice_id", sa.String(length=200), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_invoices_org_id", "invoices", ["org_id"])
    op.create_index("ix_invoices_status", "invoices", ["status"])

    op.create_table(
        "invoice_items",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("invoice_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("invoices.id", ondelete="CASCADE"), nullable=False),
        sa.Column("description", sa.String(length=300), nullable=False),
        sa.Column("qty", sa.Integer(), nullable=False),
        sa.Column("unit_price_cents", sa.Integer(), nullable=False),
        sa.Column("amount_cents", sa.Integer(), nullable=False),
    )
    op.create_index("ix_invoice_items_invoice_id", "invoice_items", ["invoice_id"])

    op.create_table(
        "reminder_runs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("invoice_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("invoices.id", ondelete="CASCADE"), nullable=False),
        sa.Column("stage", sa.String(length=50), nullable=False),
        sa.Column("sent_at", sa.DateTime(), nullable=True),
        sa.Column("result", sa.String(length=300), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_reminder_runs_invoice_id", "reminder_runs", ["invoice_id"])


def downgrade() -> None:
    op.drop_index("ix_reminder_runs_invoice_id", table_name="reminder_runs")
    op.drop_table("reminder_runs")

    op.drop_index("ix_invoice_items_invoice_id", table_name="invoice_items")
    op.drop_table("invoice_items")

    op.drop_index("ix_invoices_status", table_name="invoices")
    op.drop_index("ix_invoices_org_id", table_name="invoices")
    op.drop_table("invoices")

    op.drop_index("ix_revocations_license_id", table_name="revocations")
    op.drop_table("revocations")

    op.drop_index("ix_activations_license_id", table_name="activations")
    op.drop_table("activations")

    op.drop_index("ix_license_keys_org_id", table_name="license_signing_keys")
    op.drop_table("license_signing_keys")

    op.drop_index("ix_licenses_product_id", table_name="licenses")
    op.drop_index("ix_licenses_org_id", table_name="licenses")
    op.drop_table("licenses")

    op.drop_index("ix_products_org_id", table_name="products")
    op.drop_table("products")

    op.drop_index("ix_contract_attachments_contract_id", table_name="contract_attachments")
    op.drop_table("contract_attachments")

    op.drop_index("ix_contract_events_contract_id", table_name="contract_events")
    op.drop_table("contract_events")

    op.drop_index("ix_contract_versions_contract_id", table_name="contract_versions")
    op.drop_table("contract_versions")

    op.drop_index("ix_contracts_status", table_name="contracts")
    op.drop_index("ix_contracts_org_id", table_name="contracts")
    op.drop_table("contracts")

    op.drop_index("ix_otp_challenges_email", table_name="otp_challenges")
    op.drop_table("otp_challenges")

    op.drop_index("ix_sessions_org_id", table_name="sessions")
    op.drop_index("ix_sessions_user_id", table_name="sessions")
    op.drop_table("sessions")

    op.drop_index("ix_org_members_org_id", table_name="org_members")
    op.drop_table("org_members")

    op.drop_table("users")
    op.drop_table("organizations")

    op.execute("DROP TYPE IF EXISTS invoicestatus")
    op.execute("DROP TYPE IF EXISTS licensestatus")
    op.execute("DROP TYPE IF EXISTS contracteventtype")
    op.execute("DROP TYPE IF EXISTS contractstatus")
    op.execute("DROP TYPE IF EXISTS otppurpose")
    op.execute("DROP TYPE IF EXISTS orgrole")
    op.execute("DROP TYPE IF EXISTS orgstatus")

