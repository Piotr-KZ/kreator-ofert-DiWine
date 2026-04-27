"""
ProjectContext — cumulative AI context that grows with each step.
Each AI step receives FULL context from all previous steps.
"""

import json

from app.models.project import Project


class ProjectContext:
    """Cumulative project context for AI prompts."""

    def __init__(self, project: Project):
        self.project = project
        self.brief = project.brief_json or {}
        self.style = project.style_json or {}
        self.site_type = project.site_type or "company"
        self.sections = sorted(project.sections, key=lambda s: s.position)
        self.visual_concept = project.visual_concept_json or {}

    def _base_context(self) -> str:
        """Brief + style — available from step 1."""
        return (
            f"BRIEF:\n"
            f"Firma: {self.brief.get('description', '')}\n"
            f"Klienci: {self.brief.get('target_audience', '')}\n"
            f"Wyroznik: {self.brief.get('usp', '')}\n"
            f"Ton: {self.brief.get('tone', 'profesjonalny')}\n"
            f"Typ strony: {self.site_type}\n"
            f"Kolor glowny: {self.style.get('primary_color', '#4F46E5')}\n"
            f"Kolor drugorzedny: {self.style.get('secondary_color', '#F59E0B')}\n"
        )

    def for_validation(self) -> str:
        """Context for step 2 (validation)."""
        return self._base_context()

    def for_structure(self) -> str:
        """Context for step 3 (structure)."""
        return self._base_context()

    def for_content(self, section) -> str:
        """Context for step 4 (content) — knows structure and neighbors."""
        ctx = self._base_context()

        # Section list
        sekcje = "\n".join([
            f"  {i+1}. {s.block_code}" for i, s in enumerate(self.sections)
        ])
        ctx += f"\nSTRUKTURA STRONY ({len(self.sections)} sekcji):\n{sekcje}\n"

        # Neighbors
        idx = next((i for i, s in enumerate(self.sections) if s.id == section.id), 0)

        prev_info = ""
        next_info = ""
        if idx > 0:
            prev = self.sections[idx - 1]
            prev_slots = prev.slots_json or {}
            prev_heading = prev_slots.get("heading", prev_slots.get("title", "(bez heading)"))
            prev_info = f"{prev.block_code}: {prev_heading}"
        if idx < len(self.sections) - 1:
            nxt = self.sections[idx + 1]
            next_info = f"{nxt.block_code}"

        ctx += (
            f"\nTA SEKCJA: {section.block_code} (pozycja {idx + 1} z {len(self.sections)})\n"
            f"Sekcja PRZED: {prev_info or '(brak — pierwsza)'}\n"
            f"Sekcja PO: {next_info or '(brak — ostatnia)'}\n"
            f"NIE POWTARZAJ tresci z sasiednich sekcji.\n\n"
            f"WSKAZOWKI WIZUALNE (krok 5 dobierze media):\n"
            f"- Sekcje oferty/uslug → prawdopodobnie ikony Lucide, generuj 3-6 pozycji\n"
            f"- Sekcje procesu → infografika krokow, generuj 3-5 krokow z numerami\n"
            f"- Hero → duze zdjecie z overlayem, heading max 8 slow\n"
            f"- CTA → czysty layout, 1 heading + 1 przycisk\n"
            f"- Opinie → avatary + cytaty, generuj 2-3 opinie z imieniem i firma\n"
            f"- Jesli slot to image → wpisz OPIS zdjecia po angielsku (nie URL)\n"
        )
        return ctx

    def for_visual(self) -> str:
        """Context for step 5 (visual concept) — knows content."""
        ctx = self._base_context()

        sekcje_info = []
        for s in self.sections:
            slots = s.slots_json or {}
            info = {
                "block_code": s.block_code,
                "heading": slots.get("heading", slots.get("title", "")),
            }
            # Count items (services, steps, opinions)
            for key in ["items", "services", "features", "steps", "opinions", "team"]:
                if key in slots and isinstance(slots[key], list):
                    info["items_count"] = len(slots[key])
                    break
            sekcje_info.append(info)

        ctx += (
            f"\nSEKCJE Z TRESCIAMI:\n"
            f"{json.dumps(sekcje_info, ensure_ascii=False, indent=2)}\n\n"
            f"Projektuj wizualizacje WIEDZAC jakie tresci sa:\n"
            f"- Jesli sekcja ma 3 uslugi → grid 3 kolumn z ikonami\n"
            f"- Jesli sekcja ma 5 krokow → infografika 5 krokow\n"
            f"- Jesli sekcja ma 1 cytat → duzy centered cytat\n"
            f"- Dobierz photo_query do KONTEKSTU tresci (nie generycznie) — ZAWSZE po angielsku\n"
        )
        return ctx
