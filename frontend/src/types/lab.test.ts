import { describe, it, expect } from 'vitest';
import {
  BLOCK_LIBRARY,
  CATEGORIES,
  GRADIENT_PRESETS,
  GRADIENT_ANGLES,
  DEFAULT_BRAND,
  FONT_OPTIONS,
  bgColorToCSS,
  isDark,
} from './lab';
import type { Gradient } from './lab';

// ── BLOCK_LIBRARY ──────────────────────────────────────────────

describe('BLOCK_LIBRARY', () => {
  it('has exactly 40 blocks', () => {
    expect(BLOCK_LIBRARY).toHaveLength(40);
  });

  it('all blocks have required fields: code, cat, name, size', () => {
    for (const b of BLOCK_LIBRARY) {
      expect(b.code, `block ${b.code} missing code`).toBeTruthy();
      expect(b.cat, `block ${b.code} missing cat`).toBeTruthy();
      expect(b.name, `block ${b.code} missing name`).toBeTruthy();
      expect(['S', 'M', 'L']).toContain(b.size);
    }
  });

  it('all block codes are unique', () => {
    const codes = BLOCK_LIBRARY.map(b => b.code);
    const unique = new Set(codes);
    expect(unique.size).toBe(codes.length);
  });
});

// ── CATEGORIES ─────────────────────────────────────────────────

describe('CATEGORIES', () => {
  it('has exactly 20 categories', () => {
    expect(Object.keys(CATEGORIES)).toHaveLength(20);
  });

  it('every block cat exists in CATEGORIES', () => {
    for (const b of BLOCK_LIBRARY) {
      expect(CATEGORIES[b.cat], `category ${b.cat} missing`).toBeDefined();
    }
  });

  it('all categories have name and color', () => {
    for (const [key, cat] of Object.entries(CATEGORIES)) {
      expect(cat.name, `cat ${key} missing name`).toBeTruthy();
      expect(cat.color, `cat ${key} missing color`).toMatch(/^#[0-9A-Fa-f]{6}$/);
    }
  });
});

// ── DEFAULT_BRAND ──────────────────────────────────────────────

describe('DEFAULT_BRAND', () => {
  it('has all required fields', () => {
    expect(DEFAULT_BRAND.bgColor).toBeTruthy();
    expect(DEFAULT_BRAND.ctaColor).toBeTruthy();
    expect(DEFAULT_BRAND.ctaColor2).toBeTruthy();
    expect(DEFAULT_BRAND.fontHeading).toBeTruthy();
    expect(DEFAULT_BRAND.fontBody).toBeTruthy();
    expect(['compact', 'normal', 'spacious']).toContain(DEFAULT_BRAND.density);
  });

  it('palette has 6 entries', () => {
    expect(DEFAULT_BRAND.palette).toHaveLength(6);
  });

  it('all palette entries are valid hex', () => {
    for (const color of DEFAULT_BRAND.palette) {
      expect(color).toMatch(/^#[0-9A-Fa-f]{6}$/);
    }
  });
});

// ── bgColorToCSS ───────────────────────────────────────────────

describe('bgColorToCSS', () => {
  it('returns default fallback for null', () => {
    expect(bgColorToCSS(null)).toBe('#FFFFFF');
  });

  it('returns default fallback for undefined', () => {
    expect(bgColorToCSS(undefined)).toBe('#FFFFFF');
  });

  it('returns custom fallback when provided', () => {
    expect(bgColorToCSS(null, '#000000')).toBe('#000000');
  });

  it('returns the string as-is for hex color', () => {
    expect(bgColorToCSS('#6366F1')).toBe('#6366F1');
  });

  it('returns linear-gradient for Gradient object', () => {
    const g: Gradient = { type: 'gradient', angle: '135deg', c1: '#6366F1', c2: '#EC4899' };
    expect(bgColorToCSS(g)).toBe('linear-gradient(135deg, #6366F1, #EC4899)');
  });

  it('gradient uses the correct angle from the object', () => {
    const g: Gradient = { type: 'gradient', angle: '45deg', c1: '#10B981', c2: '#06B6D4' };
    expect(bgColorToCSS(g)).toBe('linear-gradient(45deg, #10B981, #06B6D4)');
  });
});

// ── isDark ─────────────────────────────────────────────────────

describe('isDark', () => {
  it('returns true for black', () => {
    expect(isDark('#000000')).toBe(true);
  });

  it('returns false for white', () => {
    expect(isDark('#FFFFFF')).toBe(false);
  });

  it('returns true for dark navy (#0F172A)', () => {
    expect(isDark('#0F172A')).toBe(true);
  });

  it('returns false for light gray (#F1F5F9)', () => {
    expect(isDark('#F1F5F9')).toBe(false);
  });

  it('returns false for short/invalid hex', () => {
    expect(isDark('#FFF')).toBe(false);
  });
});

// ── GRADIENT_PRESETS & GRADIENT_ANGLES ────────────────────────

describe('GRADIENT_PRESETS', () => {
  it('has exactly 8 presets', () => {
    expect(GRADIENT_PRESETS).toHaveLength(8);
  });

  it('all presets have c1, c2, label', () => {
    for (const p of GRADIENT_PRESETS) {
      expect(p.c1).toMatch(/^#[0-9A-Fa-f]{6}$/);
      expect(p.c2).toMatch(/^#[0-9A-Fa-f]{6}$/);
      expect(p.label).toBeTruthy();
    }
  });
});

describe('GRADIENT_ANGLES', () => {
  it('has exactly 8 angle options', () => {
    expect(GRADIENT_ANGLES).toHaveLength(8);
  });

  it('all angles have label and value ending in deg', () => {
    for (const a of GRADIENT_ANGLES) {
      expect(a.label).toBeTruthy();
      expect(a.value).toMatch(/^\d+deg$/);
    }
  });
});

// ── Etap E — dodatkowe testy logiki ──────────────────────────

describe('FONT_OPTIONS', () => {
  it('has at least 5 font choices', () => {
    expect(FONT_OPTIONS.length).toBeGreaterThanOrEqual(5);
  });
});

describe('BLOCK_LIBRARY — cross-checks', () => {
  it('every block cat exists in CATEGORIES (cross-reference)', () => {
    const catKeys = new Set(Object.keys(CATEGORIES));
    for (const b of BLOCK_LIBRARY) {
      expect(catKeys.has(b.cat), `Block ${b.code} has unknown cat: ${b.cat}`).toBe(true);
    }
  });

  it('all block sizes are S, M or L', () => {
    const valid = new Set(['S', 'M', 'L']);
    for (const b of BLOCK_LIBRARY) {
      expect(valid.has(b.size), `Block ${b.code} has invalid size: ${b.size}`).toBe(true);
    }
  });
});

describe('GRADIENT_PRESETS — color pairs', () => {
  it('all presets have distinct c1 and c2 colors', () => {
    for (const p of GRADIENT_PRESETS) {
      expect(p.c1.toLowerCase()).not.toBe(p.c2.toLowerCase());
    }
  });
});

describe('bgColorToCSS — edge cases', () => {
  it('returns fallback for empty string', () => {
    expect(bgColorToCSS('', '#AABBCC')).toBe('#AABBCC');
  });
});

describe('isDark — additional luminance checks', () => {
  it('returns true for dark gray (#777777, luminance ~119)', () => {
    // r=g=b=119 → (119*299 + 119*587 + 119*114)/1000 = 119 < 128
    expect(isDark('#777777')).toBe(true);
  });

  it('returns false for mid-bright color (#888888, luminance 136)', () => {
    // r=g=b=136 → (136*299 + 136*587 + 136*114)/1000 = 136 > 128
    expect(isDark('#888888')).toBe(false);
  });
});
