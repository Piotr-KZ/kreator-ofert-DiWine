/**
 * tweaks.ts — CSS variables + Google Fonts loader dla Step5Visual.
 *
 * applyTweaks(el, brand) ustawia zmienne CSS na elemencie wrappera podglądu.
 * Renderery czytają var(--font-heading), var(--fh1), var(--cta-bg) itd.
 */

import type { Brand } from "@/types/lab";

// ─── Google Fonts loader ───────────────────────────────────────────────────────

const loadedFonts = new Set<string>();

export function loadGoogleFont(fontName: string) {
  if (!fontName || fontName === "Inter" || loadedFonts.has(fontName)) return;
  loadedFonts.add(fontName);
  const name = fontName.replace(/ /g, "+");
  const link = document.createElement("link");
  link.rel = "stylesheet";
  link.href = `https://fonts.googleapis.com/css2?family=${name}:ital,wght@0,400;0,500;0,600;0,700;1,400;1,500&display=swap`;
  document.head.appendChild(link);
}

// ─── applyTweaks ──────────────────────────────────────────────────────────────

export function applyTweaks(el: HTMLElement, brand: Brand) {
  const {
    fontHeading = "Instrument Serif",
    fontBody = "Inter",
    ctaColor = "#6366F1",
    ctaColor2 = "#EC4899",
    ctaTextColor = "#FFFFFF",
    ctaIsGradient = true,
    textColor = "#0F172A",
    borderRadius = 8,
    density = "normal",
  } = brand;

  // CTA background
  const ctaBg = ctaIsGradient
    ? `linear-gradient(135deg, ${ctaColor}, ${ctaColor2})`
    : (ctaColor as string);

  // Density → padding + font sizes
  const py =
    density === "compact" ? "3rem" : density === "spacious" ? "6.5rem" : "5rem";

  // Base font size per density
  const base =
    density === "compact" ? 15 : density === "spacious" ? 17 : 16;

  // Scale factor — gives h1 ≈ 56-68px range
  const s =
    density === "compact" ? 1.35 : density === "spacious" ? 1.42 : 1.38;

  const fh1 = Math.round(base * s * s * s * s); // ~57-65px
  const fh2 = Math.round(base * s * s * s);      // ~41-48px
  const fh3 = Math.round(base * s * s);          // ~30-34px
  const fbody = base;                             // 15-17px
  const fey = Math.round(base * 0.78);           // ~12px

  el.style.setProperty("--font-heading", `'${fontHeading}', serif`);
  el.style.setProperty("--font-body", `'${fontBody}', sans-serif`);
  el.style.setProperty("--brand-color", ctaColor as string);
  el.style.setProperty("--brand-color2", ctaColor2 as string);
  el.style.setProperty("--cta-bg", ctaBg);
  el.style.setProperty("--cta-text", ctaTextColor || "#FFFFFF");
  el.style.setProperty("--brand-text", textColor || "#0F172A");
  el.style.setProperty("--radius", `${borderRadius}px`);
  el.style.setProperty("--density-py", py);
  el.style.setProperty("--fh1", `${fh1}px`);
  el.style.setProperty("--fh2", `${fh2}px`);
  el.style.setProperty("--fh3", `${fh3}px`);
  el.style.setProperty("--fbody", `${fbody}px`);
  el.style.setProperty("--fey", `${fey}px`);
}
