"""
Pydantic schemas for Offer API.
"""

from pydantic import BaseModel
from typing import Optional


# ─── Client ───

class ClientCreate(BaseModel):
    company_name: str
    legal_form: Optional[str] = None
    nip: Optional[str] = None
    regon: Optional[str] = None
    # Rejestrowy
    reg_street: Optional[str] = None
    reg_number: Optional[str] = None
    reg_postal_code: Optional[str] = None
    reg_city: Optional[str] = None
    # Adresowy
    addr_same_as_reg: bool = True
    addr_street: Optional[str] = None
    addr_number: Optional[str] = None
    addr_postal_code: Optional[str] = None
    addr_city: Optional[str] = None
    # Kontakt firmy
    company_phone: Optional[str] = None
    company_email: Optional[str] = None
    company_www: Optional[str] = None
    # Osoba
    contact_person: Optional[str] = None
    contact_role: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    # Legacy
    address: Optional[str] = None
    delivery_address: Optional[str] = None


class ClientOut(BaseModel):
    id: str
    company_name: str
    legal_form: Optional[str] = None
    nip: Optional[str] = None
    regon: Optional[str] = None
    reg_street: Optional[str] = None
    reg_number: Optional[str] = None
    reg_postal_code: Optional[str] = None
    reg_city: Optional[str] = None
    contact_person: Optional[str] = None
    contact_role: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None

    class Config:
        from_attributes = True


# ─── Supplier ───

class SupplierCreate(BaseModel):
    name: str
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    delivery_days: int = 5
    address_street: Optional[str] = None
    address_number: Optional[str] = None
    address_postal_code: Optional[str] = None
    address_city: Optional[str] = None
    nip: Optional[str] = None
    www: Optional[str] = None


class SupplierOut(BaseModel):
    id: str
    name: str
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    delivery_days: int = 5
    address_street: Optional[str] = None
    address_number: Optional[str] = None
    address_postal_code: Optional[str] = None
    address_city: Optional[str] = None
    nip: Optional[str] = None
    www: Optional[str] = None

    class Config:
        from_attributes = True


# ─── Product ───

class ProductCreate(BaseModel):
    name: str
    category: str
    base_price: float
    wine_color: Optional[str] = None
    wine_type: Optional[str] = None
    slot_size: int = 1
    available_colors_json: Optional[list] = None
    stock_quantity: int = 0
    supplier_id: Optional[str] = None
    description: Optional[str] = None


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

class PackagingCreate(BaseModel):
    name: str
    packaging_type: str
    bottles: int = 1
    sweet_slots: int = 5
    price: float
    stock_quantity: int = 0


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

class DiscountRuleCreate(BaseModel):
    rule_type: str
    product_id: Optional[str] = None
    min_quantity: int
    max_quantity: int
    discount_percent: Optional[float] = None
    fixed_price: Optional[float] = None


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
