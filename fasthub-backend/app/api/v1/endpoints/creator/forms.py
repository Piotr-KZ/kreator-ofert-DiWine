"""
Creator: Form submission endpoints — public submit + protected list.
"""

from uuid import UUID

import json

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, field_validator
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_active_user, get_current_organization
from app.db.session import get_db
from app.models.form_submission import FormSubmission
from app.models.organization import Organization
from app.models.published_site import PublishedSite
from app.models.user import User
from app.schemas.creator import FormSubmissionResponse, FormSubmissionUpdate

# Public router (no auth) — registered with prefix=""
public_router = APIRouter()

# Protected router — registered with prefix="/projects"
router = APIRouter()


_MAX_FORM_DATA_SIZE = 64 * 1024  # 64 KB serialized


class FormSubmitData(BaseModel):
    data: dict

    @field_validator("data")
    @classmethod
    def validate_data_size(cls, v: dict) -> dict:
        serialized = json.dumps(v)
        if len(serialized) > _MAX_FORM_DATA_SIZE:
            raise ValueError(f"Form data too large (max {_MAX_FORM_DATA_SIZE // 1024} KB)")
        if len(v) > 50:
            raise ValueError("Too many form fields (max 50)")
        return v


@public_router.post("/sites/{subdomain}/form-submit", status_code=status.HTTP_201_CREATED)
async def submit_form(
    subdomain: str,
    body: FormSubmitData,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """PUBLIC endpoint — no auth. Saves form submission from published site."""
    result = await db.execute(
        select(PublishedSite).where(
            PublishedSite.subdomain == subdomain,
            PublishedSite.is_active == True,
        )
    )
    site = result.scalar_one_or_none()
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")

    submission = FormSubmission(
        site_id=site.id,
        organization_id=site.organization_id,
        data_json=body.data,
        ip=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    db.add(submission)
    await db.commit()
    await db.refresh(submission)

    return {"id": str(submission.id), "status": "saved"}


@router.get(
    "/{project_id}/form-submissions",
    response_model=list[FormSubmissionResponse],
)
async def list_form_submissions(
    project_id: UUID,
    org: Organization = Depends(get_current_organization),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """List form submissions for a project's published site."""
    result = await db.execute(
        select(PublishedSite).where(
            PublishedSite.project_id == project_id,
            PublishedSite.organization_id == org.id,
        )
    )
    site = result.scalar_one_or_none()
    if not site:
        return []

    result = await db.execute(
        select(FormSubmission)
        .where(FormSubmission.site_id == site.id)
        .order_by(FormSubmission.created_at.desc())
    )
    return result.scalars().all()


@router.patch("/{project_id}/form-submissions/{submission_id}")
async def update_form_submission(
    project_id: UUID,
    submission_id: UUID,
    body: FormSubmissionUpdate,
    org: Organization = Depends(get_current_organization),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """Mark form submission as read/answered."""
    # Verify project belongs to org
    result = await db.execute(
        select(PublishedSite).where(
            PublishedSite.project_id == project_id,
            PublishedSite.organization_id == org.id,
        )
    )
    site = result.scalar_one_or_none()
    if not site:
        raise HTTPException(status_code=404, detail="Site not found")

    result = await db.execute(
        select(FormSubmission).where(
            FormSubmission.id == submission_id,
            FormSubmission.site_id == site.id,
        )
    )
    submission = result.scalar_one_or_none()
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")

    if body.read is not None:
        submission.read = body.read
    await db.flush()
    await db.refresh(submission)
    return {"id": str(submission.id), "read": submission.read}
