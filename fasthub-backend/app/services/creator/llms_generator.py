"""
LlmsGenerator — generate llms.txt for AI agents.
Brief 41: structured text file at site root per llmstxt.org spec.
"""


class LlmsGenerator:
    """Generate llms.txt from project brief + ai_visibility data."""

    CATEGORY_HEADERS = {
        "produkty": "Products",
        "uslugi": "Services",
        "projekty": "Projects",
        "metodyki": "Methodology",
        "certyfikaty": "Credentials",
        "opinie": "Reviews",
        "artykuly": "Publications",
        "oddzialy": "Locations",
        "sukcesy": "Achievements",
    }

    PERSON_CATEGORY_HEADERS = {
        "kompetencje": "Expertise",
        "doswiadczenie": "Career History",
        "wyksztalcenie": "Education",
        "certyfikaty": "Credentials",
        "sukcesy": "Achievements",
    }

    def generate(self, project) -> str:
        """Generate llms.txt content from project data."""
        brief = project.brief_json or {}
        ai = project.ai_visibility or {}

        lines = []

        # Title
        company = brief.get("company_name") or project.name or "Website"
        lines.append(f"# {company}")
        lines.append("")

        # About
        description = ai.get("description") or brief.get("description") or ""
        if description:
            lines.append("## About")
            lines.append(description)
            lines.append("")

        # Industry
        industry = brief.get("industry")
        if industry:
            lines.append(f"> Industry: {industry}")
            lines.append("")

        # Links (social + websites)
        links = []
        for link in (ai.get("social_profiles") or []):
            name = link.get("name", "")
            url = link.get("url", "")
            if name and url:
                links.append(f"- [{name}]({url})")

        for link in (ai.get("websites") or []):
            name = link.get("name", "")
            url = link.get("url", "")
            if name and url:
                links.append(f"- [{name}]({url})")

        if links:
            lines.append("## Links")
            lines.extend(links)
            lines.append("")

        # Categories
        categories = ai.get("categories") or {}
        for cat_key, items in categories.items():
            if not isinstance(items, list) or not items:
                continue
            header = self.CATEGORY_HEADERS.get(cat_key, cat_key.title())
            lines.append(f"## {header}")
            for item in items:
                name = item.get("name", "")
                desc = item.get("description", "")
                if name:
                    if desc:
                        lines.append(f"- **{name}**: {desc}")
                    else:
                        lines.append(f"- {name}")
            lines.append("")

        # People
        people = ai.get("people") or []
        for person in people:
            name = person.get("name", "")
            title = person.get("title", "")
            if not name:
                continue

            header = f"## Key Person: {name}"
            if title:
                header += f" ({title})"
            lines.append(header)

            person_cats = person.get("categories") or {}
            for pcat_key, pcat_items in person_cats.items():
                if not isinstance(pcat_items, list) or not pcat_items:
                    continue
                pheader = self.PERSON_CATEGORY_HEADERS.get(pcat_key, pcat_key.title())
                lines.append(f"### {pheader}")
                for pitem in pcat_items:
                    pname = pitem.get("name", "")
                    pdesc = pitem.get("description", "")
                    pperiod = pitem.get("period", "")
                    pschool = pitem.get("school", "")
                    if pname:
                        parts = [f"**{pname}**"]
                        if pperiod:
                            parts.append(f"({pperiod})")
                        if pschool:
                            parts.append(f"@ {pschool}")
                        if pdesc:
                            parts.append(f"— {pdesc}")
                        lines.append(f"- {' '.join(parts)}")
                lines.append("")

        # Contact
        contact_parts = []
        contact_email = brief.get("contact_email") or (
            (project.config_json or {}).get("forms", {}) or {}
        ).get("contact_email")
        if contact_email:
            contact_parts.append(f"- Email: {contact_email}")

        contact_phone = brief.get("contact_phone")
        if contact_phone:
            contact_parts.append(f"- Phone: {contact_phone}")

        config = project.config_json or {}
        hosting = config.get("hosting", {}) or {}
        domain = hosting.get("custom_domain") or hosting.get("subdomain") or project.domain
        if domain:
            contact_parts.append(f"- Website: https://{domain}")

        if contact_parts:
            lines.append("## Contact")
            lines.extend(contact_parts)
            lines.append("")

        return "\n".join(lines).strip() + "\n"
