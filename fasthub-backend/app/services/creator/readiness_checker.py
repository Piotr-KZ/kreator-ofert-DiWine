"""
ReadinessChecker — programmatic checks in 5 categories.
Brief 35: step 8 — pre-publish checklist.
Includes WCAG contrast checking (item 39) and CWV hints.
"""

import json
import math
from typing import Optional

from app.models.project import Project


class ReadinessChecker:
    """Run pre-publish checks on a project."""

    def check(self, project: Project) -> dict:
        """Run all checks. Returns {checks, skipped, can_publish, score}."""
        from app.services.creator.site_type_config import get_site_type_config

        type_config = get_site_type_config(project.site_type)
        skip_keys = set(type_config.readiness_skip_checks)
        modify_rules = type_config.readiness_modify_checks

        all_checks = []
        all_checks.extend(self._content_checks(project, modify_rules))
        all_checks.extend(self._tech_checks(project))
        all_checks.extend(self._legal_checks(project))
        all_checks.extend(self._seo_checks(project))
        all_checks.extend(self._accessibility_checks(project))
        all_checks.extend(self._ai_visibility_checks(project))

        # Filter out skipped checks
        checks = [c for c in all_checks if c["key"] not in skip_keys]
        skipped = [
            {"key": c["key"], "status": "skip",
             "message": f"Pominieto - nieistotne dla typu: {type_config.label}"}
            for c in all_checks if c["key"] in skip_keys
        ]

        has_error = any(c["status"] == "error" for c in checks)
        passed = sum(1 for c in checks if c["status"] == "pass")

        return {
            "checks": checks,
            "skipped": skipped,
            "can_publish": not has_error,
            "score": passed,
        }

    # ─── Content (4 checks) ───

    def _content_checks(self, project: Project, modify_rules: dict | None = None) -> list[dict]:
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

        # 4. cta_present (with per-type modify rules for LP)
        cta_rule = (modify_rules or {}).get("cta_present", {})
        min_cta = cta_rule.get("min_cta_count", 1)

        cta_count = sum(
            1 for s in sections
            if s.is_visible and s.slots_json
            and (s.slots_json.get("cta_text") or s.slots_json.get("button_text"))
        )

        if min_cta > 1:
            # LP mode — require multiple CTAs
            if cta_count >= min_cta:
                checks.append({
                    "key": "cta_present",
                    "status": "pass",
                    "message": f"CTA obecne ({cta_count}x) — OK dla landing page",
                })
            else:
                checks.append({
                    "key": "cta_present",
                    "status": "warn",
                    "message": cta_rule.get("fail_message", f"Wymagane minimum {min_cta} CTA"),
                    "suggestion": "Dodaj więcej sekcji CTA (np. Hero + sekcja końcowa)",
                })
        else:
            # Standard mode — single CTA check
            checks.append({
                "key": "cta_present",
                "status": "pass" if cta_count > 0 else "warn",
                "message": "CTA (wezwanie do działania) obecne" if cta_count > 0 else "Brak przycisku CTA na stronie",
                "suggestion": None if cta_count > 0 else "Dodaj przycisk CTA w sekcji Hero lub kontaktowej",
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

    # ─── Accessibility / WCAG (checks) ───

    def _accessibility_checks(self, project: Project) -> list[dict]:
        """WCAG 2.1 AA accessibility checks."""
        checks = []
        style = project.style_json or {}

        # 16. Contrast ratio check (WCAG 2.1 AA requires 4.5:1 for normal text)
        primary = style.get("color_primary", "#4F46E5")
        text_color = "#1f2937"  # default body text
        bg_color = "#ffffff"  # default background

        # Check primary color on white background (buttons, links)
        primary_ratio = self._contrast_ratio(primary, bg_color)
        text_ratio = self._contrast_ratio(text_color, bg_color)

        contrast_issues = []
        if primary_ratio < 4.5:
            contrast_issues.append(
                f"Kolor główny ({primary}) na białym tle: {primary_ratio:.1f}:1 (wymóg 4.5:1)"
            )

        if contrast_issues:
            checks.append({
                "key": "wcag_contrast",
                "status": "warn",
                "message": f"Problemy z kontrastem WCAG: {'; '.join(contrast_issues)}",
                "suggestion": "Zmień kolor na ciemniejszy lub użyj ciemnego tła pod jasnymi elementami",
                "fix_tab": None,
            })
        else:
            checks.append({
                "key": "wcag_contrast",
                "status": "pass",
                "message": f"Kontrast kolorów OK (główny: {primary_ratio:.1f}:1)",
            })

        # 17. Alt text completeness (enhanced — already basic check in content)
        sections = project.sections if project.sections else []
        images_without_alt = []
        for s in sections:
            if s.is_visible and s.slots_json:
                for key, val in s.slots_json.items():
                    if "image" in key.lower() and isinstance(val, str) and val:
                        alt_key = f"{key}_alt"
                        if not s.slots_json.get(alt_key):
                            images_without_alt.append(f"{s.block_code}:{key}")

        if images_without_alt:
            checks.append({
                "key": "wcag_alt_texts",
                "status": "warn",
                "message": f"{len(images_without_alt)} obrazów bez tekstu ALT (WCAG 1.1.1)",
                "suggestion": "Użyj 'AI zaproponuj ALT' w kroku 8 aby automatycznie wygenerować opisy",
            })
        else:
            checks.append({
                "key": "wcag_alt_texts",
                "status": "pass",
                "message": "Wszystkie obrazy mają tekst ALT (WCAG 1.1.1)",
            })

        # 18. Schema markup present
        brief = project.brief_json or {}
        has_company = bool(brief.get("company_name"))
        checks.append({
            "key": "schema_markup",
            "status": "pass" if has_company else "warn",
            "message": "Schema.org JSON-LD zostanie dodany automatycznie" if has_company
                else "Uzupełnij nazwę firmy w briefie — Schema.org wymaga nazwy",
            "suggestion": None if has_company else "Wróć do kroku 1 i uzupełnij nazwę firmy",
        })

        # 19. Heading hierarchy (H1 should exist, only one H1)
        h1_count = 0
        for s in sections:
            if s.is_visible and s.slots_json:
                if s.block_code.startswith("HE"):  # Hero sections
                    h1_count += 1

        if h1_count == 0:
            checks.append({
                "key": "wcag_heading_hierarchy",
                "status": "warn",
                "message": "Brak sekcji Hero (H1) — strona powinna mieć dokładnie jeden nagłówek H1",
                "suggestion": "Dodaj sekcję Hero na początku strony",
            })
        elif h1_count > 1:
            checks.append({
                "key": "wcag_heading_hierarchy",
                "status": "warn",
                "message": f"Znaleziono {h1_count} sekcji Hero — strona powinna mieć tylko jeden H1 (WCAG 1.3.1)",
                "suggestion": "Zostaw jedną sekcję Hero na początku, pozostałe zmień na inny typ",
            })
        else:
            checks.append({
                "key": "wcag_heading_hierarchy",
                "status": "pass",
                "message": "Hierarchia nagłówków OK — 1 x H1 (Hero)",
            })

        # 20. Form labels & RODO (accessibility of forms)
        config = project.config_json or {}
        has_form_section = any(
            "form" in (s.block_code or "").lower() or "contact" in (s.block_code or "").lower()
            for s in sections if s.is_visible
        )
        legal = config.get("legal", {}) or {}
        rodo = legal.get("rodo", {})
        rodo_enabled = rodo.get("enabled", False) if isinstance(rodo, dict) else False

        if has_form_section and not rodo_enabled:
            checks.append({
                "key": "wcag_form_accessibility",
                "status": "warn",
                "message": "Formularz bez klauzuli RODO — wymagane dla dostępności i GDPR",
                "suggestion": "Włącz klauzulę RODO w zakładce Prawo (krok 7)",
                "fix_tab": "legal",
            })
        else:
            checks.append({
                "key": "wcag_form_accessibility",
                "status": "pass",
                "message": "Formularze zgodne z WCAG" if has_form_section else "Brak formularzy (OK)",
            })

        # 21. Color secondary contrast
        secondary = style.get("color_secondary", "#64748B")
        secondary_ratio = self._contrast_ratio(secondary, bg_color)
        if secondary_ratio < 3.0:
            checks.append({
                "key": "wcag_secondary_contrast",
                "status": "warn",
                "message": f"Kolor drugorzędny ({secondary}) ma niski kontrast: {secondary_ratio:.1f}:1 (min 3:1 dla dużego tekstu)",
                "suggestion": "Rozważ ciemniejszy kolor drugorzędny",
            })
        else:
            checks.append({
                "key": "wcag_secondary_contrast",
                "status": "pass",
                "message": f"Kolor drugorzędny: kontrast OK ({secondary_ratio:.1f}:1)",
            })

        return checks

    # ─── AI Visibility (6 checks, Brief 41) ───

    def _ai_visibility_checks(self, project: Project) -> list[dict]:
        """AI Visibility pre-publish checks."""
        checks = []
        ai = project.ai_visibility or {}
        brief = project.brief_json or {}
        sections = project.sections if project.sections else []

        # 1. llms_txt_ready — description filled → llms.txt will be generated
        description = ai.get("description") or brief.get("description")
        checks.append({
            "key": "llms_txt_ready",
            "status": "pass" if description else "info",
            "message": "llms.txt zostanie wygenerowany z opisem firmy" if description
                else "Uzupełnij opis w AI Visibility aby wzbogacić llms.txt",
            "suggestion": None if description else "Dodaj opis w zakładce AI Visibility (krok 7)",
            "fix_tab": None if description else "ai_visibility",
        })

        # 2. schema_sameas — at least 1 link for sameAs
        social_profiles = ai.get("social_profiles") or []
        websites = ai.get("websites") or []
        config = project.config_json or {}
        social = config.get("social", {}) or {}
        social_links = [v for v in social.values() if isinstance(v, str) and v.startswith("http")]
        has_links = bool(social_profiles or websites or social_links)

        checks.append({
            "key": "schema_sameas",
            "status": "pass" if has_links else "warn",
            "message": "Linki sameAs w Schema.org — AI rozpozna powiązane profile" if has_links
                else "Brak linków (social/websites) — dodaj aby Schema.org zawierała sameAs",
            "suggestion": None if has_links else "Dodaj profile social media lub linki w AI Visibility",
            "fix_tab": None if has_links else "ai_visibility",
        })

        # 3. schema_person — at least 1 person
        people = ai.get("people") or []
        checks.append({
            "key": "schema_person",
            "status": "pass" if people else "info",
            "message": f"Schema.org Person: {len(people)} osób dodanych" if people
                else "Dodaj kluczowe osoby w AI Visibility → Person w Schema.org",
            "suggestion": None if people else "Dodaj osoby (np. CEO, eksperci) w zakładce AI Visibility",
            "fix_tab": None if people else "ai_visibility",
        })

        # 4. schema_service_product — at least 1 service/product
        categories = ai.get("categories") or {}
        services = categories.get("uslugi") or []
        products = categories.get("produkty") or []
        has_offerings = bool(services or products)

        checks.append({
            "key": "schema_service_product",
            "status": "pass" if has_offerings else "warn",
            "message": f"Schema.org: {len(services)} usług, {len(products)} produktów" if has_offerings
                else "Brak usług/produktów — dodaj aby AI lepiej rozumiały ofertę",
            "suggestion": None if has_offerings else "Dodaj usługi lub produkty w AI Visibility",
            "fix_tab": None if has_offerings else "ai_visibility",
        })

        # 5. schema_faq — FAQ section present → FAQPage schema
        has_faq = any(s.is_visible and s.block_code.startswith("FA") for s in sections)
        checks.append({
            "key": "schema_faq",
            "status": "pass" if has_faq else "info",
            "message": "Sekcja FAQ → FAQPage w Schema.org (AI odpowie na pytania klientów)" if has_faq
                else "Dodaj sekcję FAQ — AI chatboty będą mogły odpowiadać na pytania klientów",
        })

        # 6. ai_experience_check — person experience > company age
        import re
        founded_year = None
        fy_raw = brief.get("founded_year")
        if isinstance(fy_raw, int) and 1900 < fy_raw < 2100:
            founded_year = fy_raw
        elif isinstance(fy_raw, str):
            match = re.search(r'(?:19|20)\d{2}', fy_raw)
            if match:
                founded_year = int(match.group())

        exp_exceeds = False
        if founded_year and people:
            for person in people:
                doswiadczenie = (person.get("categories") or {}).get("doswiadczenie") or []
                for exp in doswiadczenie:
                    period = exp.get("period", "")
                    years = re.findall(r'(?:19|20)\d{2}', str(period))
                    if years and min(int(y) for y in years) < founded_year:
                        exp_exceeds = True
                        break

        if exp_exceeds:
            checks.append({
                "key": "ai_experience_check",
                "status": "pass",
                "message": "Doświadczenie kluczowej osoby przekracza wiek firmy — wzmacnia profil ekspercki",
            })

        return checks

    # ─── WCAG Helpers ───

    @staticmethod
    def _hex_to_rgb(hex_color: str) -> tuple[float, float, float]:
        """Convert hex color to RGB (0-255)."""
        h = hex_color.lstrip("#")
        if len(h) != 6:
            return (0, 0, 0)
        return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16))

    @staticmethod
    def _relative_luminance(r: float, g: float, b: float) -> float:
        """Calculate relative luminance per WCAG 2.1."""
        def linearize(c: float) -> float:
            c = c / 255.0
            return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
        return 0.2126 * linearize(r) + 0.7152 * linearize(g) + 0.0722 * linearize(b)

    @classmethod
    def _contrast_ratio(cls, color1: str, color2: str) -> float:
        """Calculate WCAG contrast ratio between two hex colors."""
        r1, g1, b1 = cls._hex_to_rgb(color1)
        r2, g2, b2 = cls._hex_to_rgb(color2)
        l1 = cls._relative_luminance(r1, g1, b1)
        l2 = cls._relative_luminance(r2, g2, b2)
        lighter = max(l1, l2)
        darker = min(l1, l2)
        return (lighter + 0.05) / (darker + 0.05)
