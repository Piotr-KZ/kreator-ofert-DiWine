"""
Testy modeli DB — Project, ProjectSection, ProjectMaterial, BlockTemplate.
"""

import pytest
import pytest_asyncio
from sqlalchemy import select

from app.models import BlockCategory, BlockTemplate, Project, ProjectMaterial, ProjectSection


# ─── Project CRUD ───

class TestProjectModel:

    @pytest.mark.asyncio
    async def test_create_project(self, db):
        project = Project(name="TestProjekt", site_type="company_card")
        db.add(project)
        await db.flush()

        assert project.id is not None
        assert project.name == "TestProjekt"
        assert project.site_type == "company_card"
        assert project.status == "draft"
        assert project.current_step == 1

    @pytest.mark.asyncio
    async def test_project_defaults(self, db):
        project = Project(name="Default")
        db.add(project)
        await db.flush()

        assert project.status == "draft"
        assert project.current_step == 1
        assert project.brief_json is None
        assert project.style_json is None
        assert project.visual_concept_json is None

    @pytest.mark.asyncio
    async def test_project_json_fields(self, db):
        project = Project(
            name="JSONTest",
            brief_json={"description": "Opis", "tone": "profesjonalny"},
            style_json={"primary_color": "#4F46E5"},
            visual_concept_json={"style": "modern_minimal"},
        )
        db.add(project)
        await db.flush()

        result = await db.execute(select(Project).where(Project.id == project.id))
        loaded = result.scalar_one()
        assert loaded.brief_json["description"] == "Opis"
        assert loaded.style_json["primary_color"] == "#4F46E5"
        assert loaded.visual_concept_json["style"] == "modern_minimal"

    @pytest.mark.asyncio
    async def test_project_timestamps(self, db):
        project = Project(name="Timestamps")
        db.add(project)
        await db.flush()

        assert project.created_at is not None
        assert project.updated_at is not None


# ─── ProjectSection ───

class TestProjectSectionModel:

    @pytest.mark.asyncio
    async def test_create_section(self, db):
        project = Project(name="P")
        db.add(project)
        await db.flush()

        section = ProjectSection(
            project_id=project.id,
            block_code="HE1",
            position=0,
        )
        db.add(section)
        await db.flush()

        assert section.id is not None
        assert section.block_code == "HE1"
        assert section.variant == "A"
        assert section.is_visible is True

    @pytest.mark.asyncio
    async def test_section_slots_json(self, db):
        project = Project(name="P")
        db.add(project)
        await db.flush()

        section = ProjectSection(
            project_id=project.id,
            block_code="HE1",
            position=0,
            slots_json={"heading": "Witaj", "items": [{"title": "A"}]},
        )
        db.add(section)
        await db.flush()

        result = await db.execute(select(ProjectSection).where(ProjectSection.id == section.id))
        loaded = result.scalar_one()
        assert loaded.slots_json["heading"] == "Witaj"
        assert len(loaded.slots_json["items"]) == 1

    @pytest.mark.asyncio
    async def test_cascade_delete_sections(self, db):
        project = Project(name="P")
        db.add(project)
        await db.flush()

        for i in range(3):
            db.add(ProjectSection(project_id=project.id, block_code=f"HE{i}", position=i))
        await db.flush()

        # Delete project
        await db.delete(project)
        await db.flush()

        result = await db.execute(select(ProjectSection))
        remaining = result.scalars().all()
        assert len(remaining) == 0


# ─── ProjectMaterial ───

class TestProjectMaterialModel:

    @pytest.mark.asyncio
    async def test_create_material(self, db):
        project = Project(name="P")
        db.add(project)
        await db.flush()

        material = ProjectMaterial(
            project_id=project.id,
            type="logo",
            file_url="/uploads/logo.png",
            original_filename="logo.png",
            file_size=12345,
            mime_type="image/png",
        )
        db.add(material)
        await db.flush()

        assert material.id is not None
        assert material.type == "logo"
        assert material.file_size == 12345


# ─── BlockTemplate ───

class TestBlockTemplateModel:

    @pytest.mark.asyncio
    async def test_seeded_categories(self, seeded_db):
        result = await seeded_db.execute(select(BlockCategory).order_by(BlockCategory.order))
        cats = result.scalars().all()
        codes = [c.code for c in cats]

        assert "NA" in codes
        assert "HE" in codes
        assert "KO" in codes
        assert len(cats) >= 7

    @pytest.mark.asyncio
    async def test_seeded_blocks(self, seeded_db):
        result = await seeded_db.execute(select(BlockTemplate).where(BlockTemplate.is_active == True))
        blocks = result.scalars().all()
        codes = [b.code for b in blocks]

        assert "NA1" in codes
        assert "HE1" in codes
        assert "OF1" in codes
        assert len(blocks) >= 6

    @pytest.mark.asyncio
    async def test_block_slots_definition(self, seeded_db):
        result = await seeded_db.execute(select(BlockTemplate).where(BlockTemplate.code == "HE1"))
        block = result.scalar_one()

        assert block.slots_definition is not None
        slot_ids = [s["id"] for s in block.slots_definition]
        assert "heading" in slot_ids
        assert "subheading" in slot_ids
