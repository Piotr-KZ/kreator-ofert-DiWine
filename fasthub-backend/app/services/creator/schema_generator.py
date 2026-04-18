"""
SchemaGenerator — rozbudowane Schema.org JSON-LD z brief + ai_visibility.
Brief 41: generuje Organization/LocalBusiness, Person, Service/Product, FAQPage, WebSite.
"""

from typing import Optional


class SchemaGenerator:
    """Generate rich Schema.org JSON-LD from project data."""

    CATEGORY_SCHEMA_MAP = {
        "produkty": ("Product", "makesOffer"),
        "uslugi": ("Service", "makesOffer"),
        "projekty": ("CreativeWork", "workExample"),
        "metodyki": ("HowTo", None),
        "certyfikaty": ("EducationalOccupationalCredential", "hasCredential"),
        "opinie": ("Review", "review"),
        "artykuly": ("Article", "subjectOf"),
        "oddzialy": ("Organization", "subOrganization"),
        "sukcesy": (None, "award"),
    }

    def generate(self, project) -> list[dict]:
        """Generate all Schema.org entities for a project."""
        brief = project.brief_json or {}
        ai = project.ai_visibility or {}
        config = project.config_json or {}

        schemas = []

        # 1. Organization / LocalBusiness
        org_schema = self._build_organization(project, brief, ai, config)
        schemas.append(org_schema)

        # 2. Person[] from people
        people = ai.get("people") or []
        for person in people:
            person_schema = self._build_person(person, org_schema.get("@id"))
            if person_schema:
                schemas.append(person_schema)

        # 3. Category items → Service, Product, etc.
        categories = ai.get("categories") or {}
        cat_items = []
        for cat_key, items in categories.items():
            if not isinstance(items, list):
                continue
            for item in items:
                cat_schema = self._build_category_item(cat_key, item, org_schema.get("@id"))
                if cat_schema:
                    cat_items.append(cat_schema)
                    schemas.append(cat_schema)

        # Attach category items to organization via appropriate properties
        self._attach_category_items_to_org(org_schema, categories, cat_items)

        # 4. FAQPage from FAQ sections
        faq_schema = self._build_faq(project)
        if faq_schema:
            schemas.append(faq_schema)

        # 5. WebSite
        website = self._build_website(project, brief, config)
        if website:
            schemas.append(website)

        return schemas

    def _build_organization(self, project, brief: dict, ai: dict, config: dict) -> dict:
        """Build Organization/LocalBusiness schema."""
        hosting = config.get("hosting", {}) or {}
        social = config.get("social", {}) or {}

        domain = hosting.get("custom_domain") or hosting.get("subdomain") or project.domain or ""
        base_url = f"https://{domain}" if domain else ""

        company_name = brief.get("company_name") or project.name or ""
        description = ai.get("description") or brief.get("description") or ""
        industry = brief.get("industry") or ""
        site_type = brief.get("site_type") or project.site_type or "website"

        schema_type = "LocalBusiness"
        if site_type in ("portfolio", "cv"):
            schema_type = "Person"
        elif site_type in ("saas", "app"):
            schema_type = "SoftwareApplication"

        schema = {
            "@context": "https://schema.org",
            "@type": schema_type,
            "@id": f"{base_url}/#organization" if base_url else "#organization",
            "name": company_name,
        }

        if description:
            schema["description"] = description[:500]

        if base_url:
            schema["url"] = base_url

        if industry:
            schema["industry"] = industry

        # sameAs from social + ai_visibility links
        same_as = []
        for v in social.values():
            if isinstance(v, str) and v.startswith("http"):
                same_as.append(v)

        for link in (ai.get("social_profiles") or []):
            url = link.get("url", "")
            if url and url not in same_as:
                same_as.append(url)

        for link in (ai.get("websites") or []):
            url = link.get("url", "")
            if url and url not in same_as:
                same_as.append(url)

        if same_as:
            schema["sameAs"] = same_as

        # Contact from brief
        brief_email = brief.get("contact_email") or (config.get("forms", {}) or {}).get("contact_email")
        brief_phone = brief.get("contact_phone")

        if brief_email or brief_phone:
            contact = {"@type": "ContactPoint"}
            if brief_email:
                contact["email"] = brief_email
            if brief_phone:
                contact["telephone"] = brief_phone
            schema["contactPoint"] = contact

        return schema

    def _build_person(self, person_data: dict, org_id: Optional[str]) -> Optional[dict]:
        """Build Person schema from ai_visibility person."""
        name = person_data.get("name")
        if not name:
            return None

        schema = {
            "@context": "https://schema.org",
            "@type": "Person",
            "name": name,
        }

        title = person_data.get("title")
        if title:
            schema["jobTitle"] = title

        if org_id:
            schema["worksFor"] = {"@id": org_id}

        categories = person_data.get("categories") or {}

        # kompetencje → knowsAbout
        kompetencje = categories.get("kompetencje") or []
        if kompetencje:
            schema["knowsAbout"] = [k.get("name") for k in kompetencje if k.get("name")]

        # doswiadczenie → hasOccupation
        doswiadczenie = categories.get("doswiadczenie") or []
        if doswiadczenie:
            occupations = []
            for exp in doswiadczenie:
                occ = {"@type": "Occupation", "name": exp.get("name", "")}
                if exp.get("description"):
                    occ["description"] = exp["description"]
                if exp.get("period"):
                    occ["occupationalCategory"] = exp["period"]
                occupations.append(occ)
            schema["hasOccupation"] = occupations

        # wyksztalcenie → alumniOf
        wyksztalcenie = categories.get("wyksztalcenie") or []
        if wyksztalcenie:
            alumni = []
            for edu in wyksztalcenie:
                org = {"@type": "EducationalOrganization", "name": edu.get("school") or edu.get("name", "")}
                alumni.append(org)
            schema["alumniOf"] = alumni

        # certyfikaty → hasCredential
        certyfikaty = categories.get("certyfikaty") or []
        if certyfikaty:
            creds = []
            for cert in certyfikaty:
                cred = {"@type": "EducationalOccupationalCredential", "name": cert.get("name", "")}
                if cert.get("description"):
                    cred["description"] = cert["description"]
                creds.append(cred)
            schema["hasCredential"] = creds

        # sukcesy → award
        sukcesy = categories.get("sukcesy") or []
        if sukcesy:
            schema["award"] = [s.get("name") for s in sukcesy if s.get("name")]

        return schema

    def _build_category_item(self, cat_key: str, item: dict, org_id: Optional[str]) -> Optional[dict]:
        """Build schema for a single category item."""
        mapping = self.CATEGORY_SCHEMA_MAP.get(cat_key)
        if not mapping:
            return None

        schema_type, _ = mapping
        if not schema_type:
            return None

        name = item.get("name")
        if not name:
            return None

        schema = {
            "@context": "https://schema.org",
            "@type": schema_type,
            "name": name,
        }

        if item.get("description"):
            schema["description"] = item["description"]

        if org_id and schema_type in ("Service", "Product"):
            schema["provider"] = {"@id": org_id}

        return schema

    def _attach_category_items_to_org(self, org_schema: dict, categories: dict, cat_items: list[dict]) -> None:
        """Attach category items to organization via appropriate Schema properties."""
        for cat_key, items in categories.items():
            mapping = self.CATEGORY_SCHEMA_MAP.get(cat_key)
            if not mapping or not items:
                continue
            schema_type, prop = mapping
            if not prop:
                continue

            if prop == "award":
                org_schema["award"] = [i.get("name") for i in items if i.get("name")]
            elif prop == "review":
                reviews = []
                for item in items:
                    review = {"@type": "Review", "reviewBody": item.get("description") or item.get("name", "")}
                    if item.get("name"):
                        review["author"] = {"@type": "Person", "name": item["name"]}
                    reviews.append(review)
                org_schema["review"] = reviews

    def _build_faq(self, project) -> Optional[dict]:
        """Build FAQPage schema from FAQ sections."""
        sections = project.sections if project.sections else []
        faq_items = []

        for s in sections:
            if not s.is_visible or not s.block_code.startswith("FA"):
                continue
            slots = s.slots_json or {}
            items = slots.get("faq_items") or slots.get("items") or []
            if not isinstance(items, list):
                continue
            for item in items:
                q = item.get("question") or item.get("q")
                a = item.get("answer") or item.get("a")
                if q and a:
                    faq_items.append({
                        "@type": "Question",
                        "name": q,
                        "acceptedAnswer": {
                            "@type": "Answer",
                            "text": a,
                        },
                    })

        if not faq_items:
            return None

        return {
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "mainEntity": faq_items,
        }

    def _build_website(self, project, brief: dict, config: dict) -> Optional[dict]:
        """Build WebSite schema."""
        hosting = config.get("hosting", {}) or {}
        domain = hosting.get("custom_domain") or hosting.get("subdomain") or project.domain or ""
        if not domain:
            return None

        base_url = f"https://{domain}"
        return {
            "@context": "https://schema.org",
            "@type": "WebSite",
            "url": base_url,
            "name": brief.get("company_name") or project.name or "",
        }
