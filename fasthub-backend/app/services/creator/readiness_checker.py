"""
ReadinessChecker — 15 programmatic checks in 4 categories.
Brief 35: step 8 — pre-publish checklist.
"""

import json
from typing import Optional

from app.models.project import Project


class ReadinessChecker:
    """Run pre-publish checks on a project."""

    def check(self, project: Project) -> dict:
        """Run all checks. Returns {checks, can_publish, score}."""
        checks = []

        checks.extend(self._content_checks(project))
        checks.extend(self._tech_checks(project))
        checks.extend(self._legal_checks(project))
        checks.extend(self._seo_checks(project))

        has_error = any(c["status"] == "error" for c in checks)
        passed = sum(1 for c in checks if c["status"] == "pass")

        return {
            "checks": checks,
            "can_publish": not has_error,
            "score": passed,
        }

    # ─── Content (4 checks) ───

    def _content_checks(self, project: Project) -> list[dict]:
        checks = []
        sections = project.sections if project.sections else []

        # 1. sections_filled
        empty_sections = []
        for s in sections:
            if s.is_visible and not s.slots_json:
                empty_sections.append(s.block_code)

        if empty_sections:
            checks.append({
                "key": "sections_filled",
                "status": "warn",
                "message": f"Sekcje bez treści: {', '.join(empty_sections)}",
                "suggestion": "Uzupełnij treść w edytorze (krok 6)",
                "fix_tab": None,
            })
        else:
            checks.append({
                "key": "sections_filled",
                "status": "pass",
                "message": "Wszystkie sekcje mają treść",
            })

        # 2. headings
        has_heading = any(
            s.slots_json and s.slots_json.get("title")
            for s in sections if s.is_visible
        )
        checks.append({
            "key": "headings",
            "status": "pass" if has_heading else "warn",
            "message": "Nagłówki wypełnione" if has_heading else "Brak nagłówków na stronie",
            "suggestion": None if has_heading else "Dodaj nagłówki do sekcji",
        })

        # 3. alt_texts (check if image slots have descriptions)
        missing_alt = 0
        for s in sections:
            if s.is_visible and s.slots_json:
                for key, val in s.slots_json.items():
                    if "image" in key.lower() and isinstance(val, str) and val:
                        alt_key = f"{key}_alt"
                        if not s.slots_json.get(alt_key):
                            missing_alt += 1

        if missing_alt > 0:
            checks.append({
                "key": "alt_texts",
                "status": "warn",
                "message": f"{missing_alt} obrazów bez opisu ALT",
                "suggestion": "Dodaj opisy alternatywne do zdjęć (SEO + dostępność)",
            })
        else:
            checks.append({
                "key": "alt_texts",
                "status": "pass",
                "message": "Opisy ALT obrazów OK",
            })

        # 4. cta_present
        has_cta = any(
            s.slots_json and (s.slots_json.get("cta_text") or s.slots_json.get("button_text"))
            for s in sections if s.is_visible
        )
        checks.append({
            "key": "cta_present",
            "status": "pass" if has_cta else "warn",
            "message": "CTA (wezwanie do działania) obecne" if has_cta else "Brak przycisku CTA na stronie",
            "suggestion": None if has_cta else "Dodaj przycisk CTA w sekcji Hero lub kontaktowej",
        })

        return checks

    # ─── Tech (4 checks) ───

    def _tech_checks(self, project: Project) -> list[dict]:
        checks = []
        config = project.config_json or {}
        forms = config.get("forms", {})

        # 5. mobile_responsive (always pass — templates are responsive)
        checks.append({
            "key": "mobile_responsive",
            "status": "pass",
            "message": "Szablony responsywne (mobile OK)",
        })

        # 6. form_email
        contact_email = forms.get("contact_email")
        has_form_section = any(
            "form" in (s.block_code or "").lower() or "contact" in (s.block_code or "").lower()
            for s in (project.sections or []) if s.is_visible
        )

        if has_form_section and not contact_email:
            checks.append({
                "key": "form_email",
                "status": "error",
                "message": "Formularz kontaktowy nie ma ustawionego e-maila",
                "suggestion": "Ustaw e-mail w konfiguracji formularzy (krok 7)",
                "fix_tab": "forms",
            })
        else:
            checks.append({
                "key": "form_email",
                "status": "pass",
                "message": "E-mail formularza skonfigurowany" if contact_email else "Brak formularza kontaktowego",
            })

        # 7. sitemap_possible (always pass)
        checks.append({
            "key": "sitemap_possible",
            "status": "pass",
            "message": "Sitemap zostanie wygenerowany automatycznie",
        })

        # 8. page_speed (always pass — static HTML)
        checks.append({
            "key": "page_speed",
            "status": "pass",
            "message": "Statyczny HTML — szybkie ładowanie",
        })

        return checks

    # ─── Legal (3 checks) ───

    def _legal_checks(self, project: Project) -> list[dict]:
        checks = []
        config = project.config_json or {}
        legal = config.get("legal", {})

        # 9. privacy_policy
        pp = legal.get("privacy_policy", {})
        pp_source = pp.get("source", "none") if isinstance(pp, dict) else "none"
        has_pp = pp_source in ("ai", "own") and pp.get("html")

        checks.append({
            "key": "privacy_policy",
            "status": "pass" if has_pp else "error",
            "message": "Polityka prywatności dodana" if has_pp else "Brak polityki prywatności (wymagana GDPR)",
            "suggestion": None if has_pp else "Wygeneruj lub wgraj politykę prywatności w zakładce Prawo",
            "fix_tab": None if has_pp else "legal",
        })

        # 10. cookie_banner
        cb = legal.get("cookie_banner", {})
        cb_enabled = cb.get("enabled", False) if isinstance(cb, dict) else False

        checks.append({
            "key": "cookie_banner",
            "status": "pass" if cb_enabled else "warn",
            "message": "Baner cookies włączony" if cb_enabled else "Baner cookies wyłączony",
            "suggestion": None if cb_enabled else "Rozważ włączenie banera cookies (GDPR)",
            "fix_tab": None if cb_enabled else "legal",
        })

        # 11. rodo
        rodo = legal.get("rodo", {})
        rodo_enabled = rodo.get("enabled", False) if isinstance(rodo, dict) else False

        checks.append({
            "key": "rodo",
            "status": "pass" if rodo_enabled else "warn",
            "message": "Klauzula RODO włączona" if rodo_enabled else "Klauzula RODO wyłączona",
            "suggestion": None if rodo_enabled else "Dodaj klauzulę RODO przy formularzach",
            "fix_tab": None if rodo_enabled else "legal",
        })

        return checks

    # ─── SEO (4 checks) ───

    def _seo_checks(self, project: Project) -> list[dict]:
        checks = []
        config = project.config_json or {}
        seo = config.get("seo", {})
        tracking = seo.get("tracking", {}) if isinstance(seo, dict) else {}

        # 12. meta_title
        meta_title = seo.get("meta_title", "") if isinstance(seo, dict) else ""
        checks.append({
            "key": "meta_title",
            "status": "pass" if meta_title else "warn",
            "message": f"Meta title: \"{meta_title[:40]}...\"" if meta_title else "Brak meta title",
            "suggestion": None if meta_title else "Dodaj meta title (60 znaków) w zakładce SEO",
            "fix_tab": None if meta_title else "seo",
        })

        # 13. meta_description
        meta_desc = seo.get("meta_description", "") if isinstance(seo, dict) else ""
        checks.append({
            "key": "meta_description",
            "status": "pass" if meta_desc else "warn",
            "message": f"Meta description: \"{meta_desc[:50]}...\"" if meta_desc else "Brak meta description",
            "suggestion": None if meta_desc else "Dodaj meta description (160 znaków) w zakładce SEO",
            "fix_tab": None if meta_desc else "seo",
        })

        # 14. og_tags
        og_title = seo.get("og_title", "") if isinstance(seo, dict) else ""
        checks.append({
            "key": "og_tags",
            "status": "pass" if og_title else "warn",
            "message": "Open Graph tagi ustawione" if og_title else "Brak tagów Open Graph",
            "suggestion": None if og_title else "Dodaj OG title i description dla lepszego udostępniania w social media",
            "fix_tab": None if og_title else "seo",
        })

        # 15. analytics
        has_analytics = bool(
            tracking.get("ga4_id") or tracking.get("gtm_id") or tracking.get("fb_pixel_id")
        ) if isinstance(tracking, dict) else False

        checks.append({
            "key": "analytics",
            "status": "pass" if has_analytics else "warn",
            "message": "Analityka skonfigurowana" if has_analytics else "Brak narzędzi analitycznych",
            "suggestion": None if has_analytics else "Dodaj GA4 lub GTM aby śledzić ruch na stronie",
            "fix_tab": None if has_analytics else "seo",
        })

        return checks
