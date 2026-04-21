"""
Export endpoint — download generated site as HTML.
"""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse, Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.session import get_db
from app.models.project import Project
from app.services.creator.renderer import PageRenderer

router = APIRouter()


async def _get_project_full(project_id: str, db: AsyncSession) -> Project:
    result = await db.execute(
        select(Project)
        .options(selectinload(Project.sections), selectinload(Project.materials))
        .where(Project.id == project_id)
    )
    project = result.scalar_one_or_none()
    if not project:
        raise HTTPException(status_code=404, detail="Projekt nie znaleziony")
    return project


def _build_full_html(project: Project, html_body: str, css: str) -> str:
    """Build complete HTML page with inline CSS."""
    name = project.name or "Lab Creator"
    return f"""<!DOCTYPE html>
<html lang="pl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{name}</title>
    <script src="https://cdn.tailwindcss.com@3.4.17"></script>
    <style>
{css}
    </style>
</head>
<body>
{html_body}
</body>
</html>"""


@router.get("/projects/{project_id}/preview")
async def preview_project(
    project_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Preview rendered site as full HTML page."""
    project = await _get_project_full(project_id, db)
    renderer = PageRenderer()
    html_body, css = await renderer.render_project_html(db, project)
    full_html = _build_full_html(project, html_body, css)
    return HTMLResponse(content=full_html)


@router.get("/projects/{project_id}/export-html")
async def export_html(
    project_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Download project as single HTML file."""
    project = await _get_project_full(project_id, db)
    renderer = PageRenderer()
    html_body, css = await renderer.render_project_html(db, project)
    full_html = _build_full_html(project, html_body, css)

    filename = f"{project.name.replace(' ', '_')}.html"
    return Response(
        content=full_html.encode("utf-8"),
        media_type="text/html",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
