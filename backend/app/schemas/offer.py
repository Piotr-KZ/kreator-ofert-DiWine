"""
Pydantic schemas for Offer API.
"""

from pydantic import BaseModel
from typing import Optional


# ─── Client ───

class ClientCreate(BaseModel):
    company_name: str
    nip: Optional[str] = None
    contact_person: Optional[str] = None
    contact_role: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    delivery_address: Optional[str] = None


class ClientOut(BaseModel):
    id: str
    company_name: str
    nip: Optional[str] = None
    contact_person: Optional[str] = None
    contact_role: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None

    class Config:
        from_attributes = True


# ─── Product ───

class ProductOut(BaseModel):
    id: str
    name: str
    category: str
    base_price: float
    wine_color: Optional[str] = None
    wine_type: Optional[str] = None
    slot_size: int = 1
    available_colors_json: Optional[list] = None
    stock_quantity: int = 0
    image_url: Optional[str] = None
    is_active: bool = True

    class Config:
        from_attributes = True


# ─── Packaging ───

class PackagingOut(BaseModel):
    id: str
    name: str
    packaging_type: str
    bottles: int
    sweet_slots: int
    price: float
    stock_quantity: int = 0
    is_active: bool = True

    class Config:
        from_attributes = True


# ─── Offer ───

class OfferCreate(BaseModel):
    client_id: str
    occasion_code: Optional[str] = None
    quantity: int = 100
    deadline: Optional[str] = None
    delivery_address: Optional[str] = None
    source_email: Optional[str] = None


class OfferSetItemCreate(BaseModel):
    product_id: Optional[str] = None
    item_type: str  # wine, sweet, decoration, personalization
    color_code: Optional[str] = None
    quantity: int = 1
    unit_price: float


class OfferSetCreate(BaseModel):
    name: str
    budget_per_unit: Optional[float] = None
    packaging_id: Optional[str] = None
    items: list[OfferSetItemCreate] = []


class OfferSetItemOut(BaseModel):
    id: str
    product_id: Optional[str] = None
    item_type: str
    color_code: Optional[str] = None
    quantity: int
    unit_price: float

    class Config:
        from_attributes = True


class OfferSetOut(BaseModel):
    id: str
    name: str
    position: int
    budget_per_unit: Optional[float] = None
    packaging_id: Optional[str] = None
    unit_price: float
    total_price: float
    items: list[OfferSetItemOut] = []

    class Config:
        from_attributes = True


class OfferOut(BaseModel):
    id: str
    offer_number: str
    client_id: str
    status: str
    occasion_code: Optional[str] = None
    quantity: int
    deadline: Optional[str] = None
    delivery_address: Optional[str] = None
    sets: list[OfferSetOut] = []
    created_at: Optional[str] = None

    class Config:
        from_attributes = True


# ─── Discount ───

class DiscountRuleOut(BaseModel):
    id: str
    rule_type: str
    min_quantity: int
    max_quantity: int
    discount_percent: Optional[float] = None
    fixed_price: Optional[float] = None

    class Config:
        from_attributes = True


# ─── Color / Occasion ───

class ColorOut(BaseModel):
    code: str
    name: str
    hex_value: str

    class Config:
        from_attributes = True


class OccasionOut(BaseModel):
    code: str
    name: str
    allowed_colors_json: Optional[list] = None

    class Config:
        from_attributes = True
