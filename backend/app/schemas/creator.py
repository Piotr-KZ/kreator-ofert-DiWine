"""
Pydantic schemas for Lab Creator API.
"""

from pydantic import BaseModel
from typing import Optional


class ProjectCreate(BaseModel):
    name: str
    site_type: str = "company_card"


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    site_type: Optional[str] = None
    current_step: Optional[int] = None
    brief_json: Optional[dict] = None
    style_json: Optional[dict] = None
    visual_concept_json: Optional[dict] = None


class BriefData(BaseModel):
    description: str = ""
    target_audience: str = ""
    usp: str = ""
    tone: str = "profesjonalny"


class StyleData(BaseModel):
    primary_color: str = "#4F46E5"
    secondary_color: str = "#F59E0B"


class SectionCreate(BaseModel):
    block_code: str
    position: Optional[int] = None


class SectionUpdate(BaseModel):
    slots_json: Optional[dict] = None
    variant: Optional[str] = None
    is_visible: Optional[bool] = None


class ReorderSections(BaseModel):
    section_ids: list[str]


class GenerateRequest(BaseModel):
    instruction: Optional[str] = None


class ChatMessage(BaseModel):
    message: str
    step: Optional[int] = None
