"""
CompanySettings — single-record table for DiWine company data.
Used on orders, invoices, offer headers.
"""

from sqlalchemy import Column, String, Text
from app.db.base import BaseModel


class CompanySettings(BaseModel):
    __tablename__ = "company_settings"

    # Dane rejestrowe
    name = Column(String(255), default="DiWine")
    legal_form = Column(String(50), default="")
    nip = Column(String(20), default="")
    regon = Column(String(14), default="")

    # Adres rejestrowy
    reg_street = Column(String(255), default="")
    reg_number = Column(String(20), default="")
    reg_postal = Column(String(10), default="")
    reg_city = Column(String(100), default="")

    # Kontakt firmy
    email = Column(String(255), default="")
    phone = Column(String(50), default="")
    www = Column(String(500), default="")

    # Osoba zamawiająca
    person_first_name = Column(String(100), default="")
    person_last_name = Column(String(100), default="")
    person_role = Column(String(100), default="")
    person_phone = Column(String(50), default="")
    person_email = Column(String(255), default="")

    # Logo URL
    logo_url = Column(String(500), default="")

    # Fakturownia
    fakturownia_token = Column(String(255), default="")
    fakturownia_account = Column(String(100), default="")  # subdomain
