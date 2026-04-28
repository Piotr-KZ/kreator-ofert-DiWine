# PLAN: Brief 45 — dokończenie

## Status: 90%+ gotowe

### Już zrobione (✅)
- Setup: Vite + React + TS + Tailwind + Zustand + dnd-kit + lucide-react
- Routing 5 etapów ze stepperem (LabLayout)
- Typy TS (Project, Page, Section, Brand, Block, Gradient w lab.ts)
- 40 klocków w blocks.ts + thumbnailRender (previews) + fullRender (WizRender)
- CATEGORIES z kolorami (20 kategorii)
- Step1 Brief + Styl (formularz)
- Step2 Walidacja AI (50/50 chat + ocena)
- Step3 Kreator (sidebar, cards, dnd, color picker, gradient, variant switch)
- Step4 Treści (inline edit, device switcher, AI panel)
- Step5 Wizualizacja (toolbar, tweaks, unsplash, device switcher)
- API client (client.ts — CRUD, AI, media, export)
- Store (labStore.ts — 346 linii)
- 35 unit testów PASS (lab.test.ts + previews.test.ts)

### Właśnie naprawione (✅)
- Build error: Step4Tresci.tsx — zbędny `}` po komentarzu
- Build error: WizRender.tsx — duplikat `export { EditCtx }`
- Vite build: PASS
- TSC: PASS

### Do zrobienia — testy komponentowe (Brief 45 wymaga 15 testów)

Mamy 35 unit testów → brakuje 6 testów komponentowych/store z listy Brief 45:

**KROK 1: Testy store (mockowane API)**
Plik: `src/store/labStore.test.ts`

1. `test_makiety_drag_drop` — addSection dodaje sekcję do store
2. `test_makiety_reorder` — reorderSections zmienia kolejność
3. `test_makiety_remove` — removeSection usuwa sekcję z listy
4. `test_kreator_color_picker` — updateSection zmienia bgColor
5. `test_kreator_variant_switch` — updateSection zmienia variant, zachowuje slots_json
6. `test_wizualizacja_tweaks` — updateBrand zmienia font/kolor globalnie

**Podejście:** Mock `@/api/client` (vi.mock), ustawić sections w store, testować akcje.

Testy z Brief 45 które już mamy pokryte:
- test_vite_builds → build PASS ✅
- test_typescript_no_errors → tsc PASS ✅
- test_block_library_40_blocks → lab.test.ts ✅
- test_all_blocks_have_thumbnail → previews.test.ts ✅
- test_all_blocks_have_fullrender → previews.test.ts (PV ma 40 entries) ✅
- test_brand_defaults → lab.test.ts ✅
- test_kreator_gradient → lab.test.ts (GRADIENT_PRESETS) ✅
- test_tresci_inline_edit → pokryte przez updateSlot w store teście
- test_tresci_device_switcher → dodamy do store testu (viewport state)

**Łącznie po: 41+ testów (35 istniejących + 6 nowych)**
