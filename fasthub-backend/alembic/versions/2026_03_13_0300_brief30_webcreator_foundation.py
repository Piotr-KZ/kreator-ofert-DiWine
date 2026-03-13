"""Brief 30: WebCreator foundation — all creator tables"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB

revision = "brief30_webcreator"
down_revision = "brief27_dunning_pay_wh"
branch_labels = None
depends_on = None


def upgrade():
    # 1. block_categories
    op.create_table(
        "block_categories",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("code", sa.String(5), unique=True, nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("icon", sa.String(50), nullable=True),
        sa.Column("order", sa.Integer, default=0),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
    )

    # 2. block_templates
    op.create_table(
        "block_templates",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("code", sa.String(10), unique=True, nullable=False),
        sa.Column("category_code", sa.String(5), sa.ForeignKey("block_categories.code"), nullable=False),
        sa.Column("name", sa.String(255), nullable=True),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("html_template", sa.Text, nullable=False),
        sa.Column("css", sa.Text, nullable=True),
        sa.Column("slots_definition", JSONB, nullable=False),
        sa.Column("media_type", sa.String(20), nullable=True),
        sa.Column("layout_type", sa.String(30), nullable=True),
        sa.Column("photo_shape", sa.String(20), nullable=True),
        sa.Column("text_style", sa.String(20), nullable=True),
        sa.Column("variants", JSONB, nullable=True),
        sa.Column("size", sa.String(1), server_default="M"),
        sa.Column("responsive", sa.Boolean, server_default="true"),
        sa.Column("is_active", sa.Boolean, server_default="true"),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_bt_code", "block_templates", ["code"], unique=True)
    op.create_index("ix_bt_category", "block_templates", ["category_code"])
    op.create_index("ix_bt_media_layout", "block_templates", ["media_type", "layout_type"])

    # 3. projects
    op.create_table(
        "projects",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("organization_id", UUID(as_uuid=True), sa.ForeignKey("organizations.id"), nullable=False),
        sa.Column("created_by", UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("site_type", sa.String(50), nullable=True),
        sa.Column("status", sa.String(20), server_default="draft"),
        sa.Column("current_step", sa.Integer, server_default="1"),
        sa.Column("brief_json", JSONB, nullable=True),
        sa.Column("materials_meta", JSONB, nullable=True),
        sa.Column("style_json", JSONB, nullable=True),
        sa.Column("validation_json", JSONB, nullable=True),
        sa.Column("config_json", JSONB, nullable=True),
        sa.Column("check_json", JSONB, nullable=True),
        sa.Column("domain", sa.String(255), nullable=True),
        sa.Column("custom_domain", sa.String(255), nullable=True),
        sa.Column("published_at", sa.DateTime, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_proj_org", "projects", ["organization_id"])
    op.create_index("ix_proj_status", "projects", ["status"])

    # 4. project_sections
    op.create_table(
        "project_sections",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("project_id", UUID(as_uuid=True), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("block_code", sa.String(10), nullable=False),
        sa.Column("position", sa.Integer, nullable=False),
        sa.Column("variant", sa.String(1), server_default="A"),
        sa.Column("slots_json", JSONB, nullable=True),
        sa.Column("variant_config", JSONB, nullable=True),
        sa.Column("is_visible", sa.Boolean, server_default="true"),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_ps_project", "project_sections", ["project_id"])

    # 5. project_materials
    op.create_table(
        "project_materials",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("project_id", UUID(as_uuid=True), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("type", sa.String(20), nullable=False),
        sa.Column("file_url", sa.String(500), nullable=True),
        sa.Column("original_filename", sa.String(255), nullable=True),
        sa.Column("file_size", sa.Integer, nullable=True),
        sa.Column("mime_type", sa.String(100), nullable=True),
        sa.Column("external_url", sa.String(500), nullable=True),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("ai_extracted_text", sa.Text, nullable=True),
        sa.Column("metadata_json", JSONB, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_pm_project", "project_materials", ["project_id"])

    # 6. ai_conversations
    op.create_table(
        "ai_conversations",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("project_id", UUID(as_uuid=True), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("context", sa.String(30), nullable=False),
        sa.Column("messages_json", JSONB, server_default="[]"),
        sa.Column("model_used", sa.String(50), nullable=True),
        sa.Column("total_tokens_in", sa.Integer, server_default="0"),
        sa.Column("total_tokens_out", sa.Integer, server_default="0"),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_ac_project", "ai_conversations", ["project_id"])

    # 7. ai_generation_logs
    op.create_table(
        "ai_generation_logs",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("project_id", UUID(as_uuid=True), sa.ForeignKey("projects.id", ondelete="SET NULL"), nullable=True),
        sa.Column("organization_id", UUID(as_uuid=True), sa.ForeignKey("organizations.id"), nullable=False),
        sa.Column("action", sa.String(30), nullable=False),
        sa.Column("model", sa.String(50), nullable=False),
        sa.Column("prompt_preview", sa.String(500), nullable=True),
        sa.Column("tokens_in", sa.Integer, server_default="0"),
        sa.Column("tokens_out", sa.Integer, server_default="0"),
        sa.Column("cost_usd", sa.Float, server_default="0.0"),
        sa.Column("duration_ms", sa.Integer, nullable=True),
        sa.Column("screenshots_count", sa.Integer, server_default="0"),
        sa.Column("iterations", sa.Integer, server_default="1"),
        sa.Column("success", sa.Boolean, server_default="true"),
        sa.Column("error_message", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_agl_org", "ai_generation_logs", ["organization_id"])
    op.create_index("ix_agl_project", "ai_generation_logs", ["project_id"])

    # 8. published_sites
    op.create_table(
        "published_sites",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("project_id", UUID(as_uuid=True), sa.ForeignKey("projects.id"), unique=True, nullable=False),
        sa.Column("organization_id", UUID(as_uuid=True), sa.ForeignKey("organizations.id"), nullable=False),
        sa.Column("subdomain", sa.String(100), unique=True, nullable=True),
        sa.Column("custom_domain", sa.String(255), unique=True, nullable=True),
        sa.Column("ssl_status", sa.String(20), server_default="pending"),
        sa.Column("html_snapshot", sa.Text, nullable=True),
        sa.Column("css_snapshot", sa.Text, nullable=True),
        sa.Column("assets_json", JSONB, nullable=True),
        sa.Column("seo_json", JSONB, nullable=True),
        sa.Column("tracking_json", JSONB, nullable=True),
        sa.Column("legal_json", JSONB, nullable=True),
        sa.Column("forms_json", JSONB, nullable=True),
        sa.Column("is_active", sa.Boolean, server_default="true"),
        sa.Column("published_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("last_updated_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_ps_org", "published_sites", ["organization_id"])
    op.create_index("ix_ps_subdomain", "published_sites", ["subdomain"], unique=True)


def downgrade():
    op.drop_table("published_sites")
    op.drop_table("ai_generation_logs")
    op.drop_table("ai_conversations")
    op.drop_table("project_materials")
    op.drop_table("project_sections")
    op.drop_table("projects")
    op.drop_table("block_templates")
    op.drop_table("block_categories")
