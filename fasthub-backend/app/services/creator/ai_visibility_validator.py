"""
AIVisibilityValidator — cross-validate ai_visibility data against brief.
Brief 41: detects experience > company age (positive signal).
"""

import re
from datetime import datetime


class AIVisibilityValidator:
    """Validate AI Visibility data against brief for consistency."""

    def validate(self, ai_data: dict, brief_data: dict) -> list[dict]:
        """Run validation checks. Returns list of findings."""
        findings = []

        # 1. Experience > company age check
        founded_year = self._extract_year(brief_data.get("founded_year"))
        if founded_year:
            people = ai_data.get("people") or []
            for person in people:
                name = person.get("name", "Unknown")
                doswiadczenie = (person.get("categories") or {}).get("doswiadczenie") or []
                for exp in doswiadczenie:
                    exp_year = self._extract_earliest_year(exp.get("period"))
                    if exp_year and exp_year < founded_year:
                        years_before = founded_year - exp_year
                        findings.append({
                            "field": f"people.{name}.doswiadczenie",
                            "type": "experience_exceeds_company_age",
                            "message": (
                                f"{name} ma doświadczenie od {exp_year} "
                                f"({years_before} lat przed założeniem firmy w {founded_year}) — "
                                f"to wzmacnia profil ekspercki w Schema.org"
                            ),
                            "severity": "success",
                        })

        # 2. Missing description warning
        if not ai_data.get("description"):
            findings.append({
                "field": "description",
                "type": "missing_description",
                "message": "Brak opisu AI — uzupełnij aby wygenerować lepszy llms.txt",
                "severity": "warn",
            })

        # 3. No social/website links
        has_links = bool(ai_data.get("social_profiles") or ai_data.get("websites"))
        if not has_links:
            findings.append({
                "field": "social_profiles",
                "type": "missing_links",
                "message": "Brak linków (social/websites) — dodaj aby Schema.org zawierała sameAs",
                "severity": "warn",
            })

        return findings

    @staticmethod
    def _extract_year(value) -> int | None:
        """Extract year from string or int."""
        if isinstance(value, int) and 1900 < value < 2100:
            return value
        if isinstance(value, str):
            match = re.search(r'(?:19|20)\d{2}', value)
            if match:
                return int(match.group())
        return None

    @staticmethod
    def _extract_earliest_year(period: str | None) -> int | None:
        """Extract earliest year from period string like '2015-2020' or '2018'."""
        if not period:
            return None
        years = re.findall(r'(?:19|20)\d{2}', period)
        if years:
            return min(int(y) for y in years)
        return None
