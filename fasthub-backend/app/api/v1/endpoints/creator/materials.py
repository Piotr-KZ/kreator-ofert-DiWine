"""
Creator: Materials endpoints (step 2).
"""

from uuid import UUID

from fastapi import APIRouter, Depends, Form, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_active_user, get_current_organization
from app.db.session import get_db
from app.models.organization import Organization
from app.models.project_material import ProjectMaterial
from app.models.user import User
from app.schemas.creator import LinkMaterial, MaterialResponse
from app.services.creator.project_service import ProjectService

router = APIRouter()


@router.post(
    "/{project_id}/materials",
    response_model=MaterialResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_material(
    project_id: UUID,
    file: UploadFile,
    type: str = Form(...),
    description: str = Form(None),
    org: Organization = Depends(get_current_organization),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Upload a material file (step 2 — drag & drop)."""
    svc = ProjectService(db)
    await svc.get_project_or_404(project_id, org.id)

    # Upload to FastHub Storage (S3/local)
    try:
        from fasthub_core.storage import upload_file
        file_url = await upload_file(file, folder=f"projects/{project_id}/materials")
    except ImportError:
        # Storage not yet configured — store placeholder
        file_url = f"/uploads/projects/{project_id}/materials/{file.filename}"

    content = await file.read()
    file_size = len(content)

    material = ProjectMaterial(
        project_id=project_id,
        type=type,
        file_url=file_url,
        original_filename=file.filename,
        file_size=file_size,
        mime_type=file.content_type,
        description=description,
    )
    db.add(material)
    await db.flush()
    await db.refresh(material)
    return material


@router.post(
    "/{project_id}/materials/link",
    response_model=MaterialResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_link_material(
    project_id: UUID,
    data: LinkMaterial,
    org: Organization = Depends(get_current_organization),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Add a link material (competition, inspiration, current site)."""
    svc = ProjectService(db)
    await svc.get_project_or_404(project_id, org.id)

    material = ProjectMaterial(
        project_id=project_id,
        type=data.type,
        external_url=data.url,
        description=data.description,
    )
    db.add(material)
    await db.flush()
    await db.refresh(material)
    return material


@router.get("/{project_id}/materials", response_model=list[MaterialResponse])
async def list_materials(
    project_id: UUID,
    org: Organization = Depends(get_current_organization),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """List project materials."""
    svc = ProjectService(db)
    project = await svc.get_project_or_404(project_id, org.id)
    return project.materials


@router.delete("/{project_id}/materials/{material_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_material(
    project_id: UUID,
    material_id: UUID,
    org: Organization = Depends(get_current_organization),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a material (file + record)."""
    svc = ProjectService(db)
    material = await svc.get_material_or_404(material_id, project_id, org.id)

    if material.file_url:
        try:
            from fasthub_core.storage import delete_file
            await delete_file(material.file_url)
        except ImportError:
            pass  # Storage not configured yet

    await db.delete(material)
    return None
