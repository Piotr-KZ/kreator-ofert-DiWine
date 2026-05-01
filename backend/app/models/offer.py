"""
Offer module models — clients, products, packaging, discounts, offers, sets.
"""

from sqlalchemy import Boolean, Column, Enum, Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import relationship

from app.db.base import BaseModel


# ─── KLIENT ───

class Client(BaseModel):
    __tablename__ = "clients"

    company_name = Column(String(255), nullable=False)
    nip = Column(String(20))
    regon = Column(String(14))
    contact_person = Column(String(255))
    contact_role = Column(String(100))
    email = Column(String(255))
    phone = Column(String(50))

    # Forma prawna
    legal_form = Column(String(50))  # Sp. z o.o., S.A., etc.

    # Adres rejestrowy
    reg_street = Column(String(255))
    reg_number = Column(String(20))
    reg_postal_code = Column(String(10))
    reg_city = Column(String(100))

    # Adres korespondencyjny (jeśli inny)
    addr_same_as_reg = Column(Boolean, default=True)
    addr_street = Column(String(255))
    addr_number = Column(String(20))
    addr_postal_code = Column(String(10))
    addr_city = Column(String(100))

    # Kontakt firmy
    company_phone = Column(String(50))
    company_email = Column(String(255))
    company_www = Column(String(500))

    # Legacy (combined address for backward compatibility)
    address = Column(Text)
    delivery_address = Column(Text)

    # Indywidualny rabat VIP (nadpisuje tabelę)
    vip_discount_percent = Column(Float, nullable=True)  # np. 15.0
    custom_prices_json = Column(JSON, nullable=True)  # [{product_id, price}]

    # Integracja
    fakturownia_id = Column(String(50), nullable=True)

    offers = relationship("Offer", back_populates="client", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Client {self.company_name}>"


# ─── DOSTAWCA ───

class Supplier(BaseModel):
    __tablename__ = "suppliers"

    name = Column(String(255), nullable=False)
    contact_email = Column(String(255))
    contact_phone = Column(String(50))
    delivery_days = Column(Integer, default=5)  # domyślny czas dostawy w dniach

    products = relationship("Product", back_populates="supplier")

    def __repr__(self):
        return f"<Supplier {self.name}>"


# ─── OKAZJA ───

class Occasion(BaseModel):
    __tablename__ = "occasions"

    code = Column(String(20), unique=True, nullable=False, index=True)  # christmas, easter
    name = Column(String(100), nullable=False)  # Boże Narodzenie
    allowed_colors_json = Column(JSON, nullable=True)  # ["red","gold","green"] lub null = wszystkie
    is_active = Column(Boolean, default=True)

    def __repr__(self):
        return f"<Occasion {self.code}: {self.name}>"


# ─── PRODUKT ───

class Product(BaseModel):
    __tablename__ = "products"

    name = Column(String(255), nullable=False)
    category = Column(String(20), nullable=False, index=True)  # wine, sweet, decoration, personalization

    base_price = Column(Float, nullable=False)

    # Wino
    wine_color = Column(String(20), nullable=True)  # czerwone, białe, różowe, pomarańczowe
    wine_type = Column(String(20), nullable=True)   # wytrawne, półwytrawne, półsłodkie, słodkie

    # Słodycze/dekoracje
    slot_size = Column(Integer, default=1)  # ile slotów zajmuje w opakowaniu
    available_colors_json = Column(JSON, nullable=True)  # ["red","gold","green"]

    # Personalizacja
    # ceny zależne od ilości trzymane w DiscountRule z type="personalization"

    # Stan magazynowy
    stock_quantity = Column(Integer, default=0)
    restock_days = Column(Integer, default=5)

    # Dostawca
    supplier_id = Column(String(36), ForeignKey("suppliers.id"), nullable=True)

    # Media
    image_url = Column(String(500), nullable=True)
    description = Column(Text, nullable=True)

    is_active = Column(Boolean, default=True)

    supplier = relationship("Supplier", back_populates="products")

    def __repr__(self):
        return f"<Product {self.name} ({self.category})>"


# ─── OPAKOWANIE ───

class Packaging(BaseModel):
    __tablename__ = "packagings"

    name = Column(String(255), nullable=False)
    packaging_type = Column(String(50), nullable=False)  # pudełko_czarne, kraft, skrzynka, tuba, box_xl

    bottles = Column(Integer, nullable=False, default=1)  # ile butelek mieści
    sweet_slots = Column(Integer, nullable=False, default=5)  # ile slotów na słodycze

    price = Column(Float, nullable=False)
    stock_quantity = Column(Integer, default=0)

    image_url = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True)

    def __repr__(self):
        return f"<Packaging {self.name} ({self.bottles}b/{self.sweet_slots}s)>"


# ─── REGUŁY RABATOWE ───

class DiscountRule(BaseModel):
    __tablename__ = "discount_rules"

    rule_type = Column(String(20), nullable=False, index=True)  # wine, personalization
    product_id = Column(String(36), ForeignKey("products.id"), nullable=True)  # null = dotyczy całej kategorii

    min_quantity = Column(Integer, nullable=False)
    max_quantity = Column(Integer, nullable=False)  # 99999 = bez limitu
    discount_percent = Column(Float, nullable=True)   # rabat procentowy (dla win)
    fixed_price = Column(Float, nullable=True)        # stała cena (dla personalizacji)

    def __repr__(self):
        return f"<DiscountRule {self.rule_type} {self.min_quantity}-{self.max_quantity}>"


# ─── KOLOR ───

class Color(BaseModel):
    __tablename__ = "colors"

    code = Column(String(20), unique=True, nullable=False, index=True)  # red, gold, green
    name = Column(String(50), nullable=False)  # Czerwony, Złoty
    hex_value = Column(String(7), nullable=False)  # #DC2626

    def __repr__(self):
        return f"<Color {self.code}: {self.name}>"


# ─── OFERTA ───

class Offer(BaseModel):
    __tablename__ = "offers"

    offer_number = Column(String(30), unique=True, nullable=False, index=True)  # OF/2026/05/0001

    client_id = Column(String(36), ForeignKey("clients.id"), nullable=False)

    status = Column(String(20), default="draft", index=True)  # draft, sent, viewed, accepted, rejected, expired

    occasion_code = Column(String(20), nullable=True)  # christmas, easter, universal
    quantity = Column(Integer, nullable=False)  # ilość prezentów

    # Daty
    deadline = Column(String(20), nullable=True)  # termin realizacji
    expires_at = Column(String(20), nullable=True)  # data ważności oferty

    # Dostawa
    delivery_address = Column(Text, nullable=True)

    # Źródło — oryginalny email
    source_email = Column(Text, nullable=True)
    parsed_data_json = Column(JSON, nullable=True)  # dane sparsowane przez AI

    # Token do strony ofertowej (etap 2)
    public_token = Column(String(64), nullable=True, unique=True, index=True)

    # Powiązanie z projektem (stroną ofertową — etap 2)
    project_id = Column(String(36), ForeignKey("projects.id"), nullable=True)

    # PDF
    pdf_url = Column(String(500), nullable=True)

    # Relacje
    client = relationship("Client", back_populates="offers")
    sets = relationship("OfferSet", back_populates="offer", cascade="all, delete-orphan", order_by="OfferSet.position")

    def __repr__(self):
        return f"<Offer {self.offer_number} ({self.status})>"


# ─── ZESTAW PREZENTOWY ───

class OfferSet(BaseModel):
    __tablename__ = "offer_sets"

    offer_id = Column(String(36), ForeignKey("offers.id", ondelete="CASCADE"), nullable=False, index=True)

    name = Column(String(255), nullable=False)  # "Wariant Premium"
    position = Column(Integer, default=0)
    budget_per_unit = Column(Float, nullable=True)  # limit cenowy na sztukę

    packaging_id = Column(String(36), ForeignKey("packagings.id"), nullable=True)

    # Kalkulowane
    unit_price = Column(Float, default=0)  # cena za sztukę (suma items)
    total_price = Column(Float, default=0)  # unit_price * quantity

    # Relacje
    offer = relationship("Offer", back_populates="sets")
    packaging = relationship("Packaging")
    items = relationship("OfferSetItem", back_populates="offer_set", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<OfferSet {self.name} ({self.unit_price} zł)>"


# ─── POZYCJA W ZESTAWIE ───

class OfferSetItem(BaseModel):
    __tablename__ = "offer_set_items"

    offer_set_id = Column(String(36), ForeignKey("offer_sets.id", ondelete="CASCADE"), nullable=False, index=True)

    product_id = Column(String(36), ForeignKey("products.id"), nullable=True)  # null dla opakowania

    item_type = Column(String(20), nullable=False)  # wine, sweet, decoration, personalization

    color_code = Column(String(20), nullable=True)  # red, gold — wybrany kolor

    quantity = Column(Integer, default=1)  # ile sztuk tego produktu w zestawie (zazwyczaj 1)
    unit_price = Column(Float, nullable=False)  # cena za sztukę (po rabacie)

    # Relacje
    offer_set = relationship("OfferSet", back_populates="items")
    product = relationship("Product")

    def __repr__(self):
        return f"<OfferSetItem {self.item_type} ({self.unit_price} zł)>"
