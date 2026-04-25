/**
 * ElementToolbar — floating toolbar do formatowania tekstu w contentEditable slotach.
 *
 * Pojawia sie nad zaznaczonym tekstem i umozliwia:
 * - Bold (B), Italic (I), Underline (U)
 * - Zmiane koloru tekstu (8 predefiniowanych kolorow)
 * - Wyrownanie tekstu (lewo, srodek, prawo)
 *
 * Uzywa natywnego Selection API + document.execCommand.
 */

import { useState, useEffect, useRef, useCallback } from "react";

// ── Paleta kolorow dla color pickera ─────────────────────────────────────────

const COLOR_PALETTE = [
  "#0F172A", // slate-900
  "#DC2626", // red-600
  "#EA580C", // orange-600
  "#CA8A04", // yellow-600
  "#16A34A", // green-600
  "#2563EB", // blue-600
  "#7C3AED", // violet-600
  "#FFFFFF", // white
];

// ── Typy ─────────────────────────────────────────────────────────────────────

interface ToolbarPosition {
  top: number;
  left: number;
  visible: boolean;
}

// ── Komponent przycisk toolbara ──────────────────────────────────────────────

function TBtn({
  active,
  title,
  onClick,
  children,
  style: extraStyle,
}: {
  active?: boolean;
  title: string;
  onClick: (e: React.MouseEvent) => void;
  children: React.ReactNode;
  style?: React.CSSProperties;
}) {
  return (
    <button
      title={title}
      onMouseDown={(e) => {
        // preventDefault aby nie stracic zaznaczenia w contentEditable
        e.preventDefault();
        onClick(e);
      }}
      style={{
        width: 30,
        height: 28,
        border: "none",
        borderRadius: 5,
        background: active ? "#EEF2FF" : "transparent",
        color: active ? "#4F46E5" : "#475569",
        cursor: "pointer",
        display: "grid",
        placeItems: "center",
        fontSize: 13,
        fontWeight: active ? 700 : 600,
        fontFamily: "Inter, system-ui, sans-serif",
        transition: "background .1s, color .1s",
        ...extraStyle,
      }}
    >
      {children}
    </button>
  );
}

// ── Separator ────────────────────────────────────────────────────────────────

function Sep() {
  return (
    <div
      style={{
        width: 1,
        height: 18,
        background: "#E2E8F0",
        margin: "0 2px",
        flexShrink: 0,
      }}
    />
  );
}

// ── Color Picker mini popup ──────────────────────────────────────────────────

function ColorPickerPopup({
  onSelect,
  onClose,
}: {
  onSelect: (color: string) => void;
  onClose: () => void;
}) {
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handler = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) {
        onClose();
      }
    };
    // Delay dodajemy zeby nie zamknac od razu po kliknieciu przycisku
    const t = setTimeout(() => document.addEventListener("mousedown", handler), 0);
    return () => {
      clearTimeout(t);
      document.removeEventListener("mousedown", handler);
    };
  }, [onClose]);

  return (
    <div
      ref={ref}
      style={{
        position: "absolute",
        top: "calc(100% + 6px)",
        left: "50%",
        transform: "translateX(-50%)",
        background: "#fff",
        border: "1px solid #E2E8F0",
        borderRadius: 10,
        padding: 8,
        boxShadow: "0 8px 24px rgba(15,23,42,.15)",
        display: "grid",
        gridTemplateColumns: "repeat(4, 1fr)",
        gap: 4,
        zIndex: 1000,
      }}
    >
      {COLOR_PALETTE.map((color) => (
        <button
          key={color}
          title={color}
          onMouseDown={(e) => {
            e.preventDefault();
            onSelect(color);
          }}
          style={{
            width: 24,
            height: 24,
            borderRadius: 6,
            background: color,
            border: `2px solid ${color === "#FFFFFF" ? "#CBD5E1" : color}`,
            cursor: "pointer",
            padding: 0,
            transition: "transform .1s",
          }}
          onMouseEnter={(e) =>
            ((e.currentTarget as HTMLButtonElement).style.transform = "scale(1.2)")
          }
          onMouseLeave={(e) =>
            ((e.currentTarget as HTMLButtonElement).style.transform = "scale(1)")
          }
        />
      ))}
    </div>
  );
}

// ── Glowny komponent ElementToolbar ──────────────────────────────────────────

export default function ElementToolbar() {
  const [pos, setPos] = useState<ToolbarPosition>({ top: 0, left: 0, visible: false });
  const [activeStates, setActiveStates] = useState({
    bold: false,
    italic: false,
    underline: false,
  });
  const [showColorPicker, setShowColorPicker] = useState(false);
  const toolbarRef = useRef<HTMLDivElement>(null);
  const hideTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  // ── Sprawdz stan formatowania ──────────────────────────────────────────────

  const checkActiveStates = useCallback(() => {
    try {
      setActiveStates({
        bold: document.queryCommandState("bold"),
        italic: document.queryCommandState("italic"),
        underline: document.queryCommandState("underline"),
      });
    } catch {
      // queryCommandState moze rzucic w niektorych przeglądarkach
    }
  }, []);

  // ── Sprawdz czy zaznaczenie jest wewnatrz contentEditable ─────────────────

  const isInsideContentEditable = useCallback((node: Node | null): boolean => {
    let current = node;
    while (current) {
      if (current instanceof HTMLElement) {
        if (current.contentEditable === "true") return true;
        // Jesli doszlismy do body, koniec
        if (current === document.body) return false;
      }
      current = current.parentNode;
    }
    return false;
  }, []);

  // ── Obsluga zaznaczenia tekstu ─────────────────────────────────────────────

  const handleSelectionChange = useCallback(() => {
    // Nie aktualizuj jesli color picker jest otwarty
    if (showColorPicker) return;

    const selection = window.getSelection();
    if (!selection || selection.isCollapsed || !selection.rangeCount) {
      // Opoznij ukrywanie zeby uzytkownik mogl kliknac przycisk toolbara
      if (hideTimeoutRef.current) clearTimeout(hideTimeoutRef.current);
      hideTimeoutRef.current = setTimeout(() => {
        setPos((prev) => ({ ...prev, visible: false }));
        setShowColorPicker(false);
      }, 150);
      return;
    }

    // Sprawdz czy zaznaczenie jest w contentEditable
    const anchorNode = selection.anchorNode;
    if (!isInsideContentEditable(anchorNode)) {
      setPos((prev) => ({ ...prev, visible: false }));
      setShowColorPicker(false);
      return;
    }

    // Zaznaczenie jest prawidlowe — anuluj ukrywanie
    if (hideTimeoutRef.current) {
      clearTimeout(hideTimeoutRef.current);
      hideTimeoutRef.current = null;
    }

    const range = selection.getRangeAt(0);
    const rect = range.getBoundingClientRect();

    // Oblicz pozycje — toolbar nad zaznaczeniem (fixed positioning, viewport-relative)
    const toolbarHeight = 40;
    const gap = 8;
    let top = rect.top - toolbarHeight - gap;
    const left = rect.left + rect.width / 2;

    // Jesli toolbar wychodzilby ponad viewport, pokaz pod zaznaczeniem
    if (top < 4) {
      top = rect.bottom + gap;
    }

    setPos({ top, left, visible: true });
    checkActiveStates();
  }, [isInsideContentEditable, checkActiveStates, showColorPicker]);

  // ── Sluchanie na selectionchange ───────────────────────────────────────────

  useEffect(() => {
    document.addEventListener("selectionchange", handleSelectionChange);
    return () => {
      document.removeEventListener("selectionchange", handleSelectionChange);
      if (hideTimeoutRef.current) clearTimeout(hideTimeoutRef.current);
    };
  }, [handleSelectionChange]);

  // ── Zamknij toolbar po kliknieciu poza nim ─────────────────────────────────

  useEffect(() => {
    const handleMouseDown = (e: MouseEvent) => {
      if (
        toolbarRef.current &&
        !toolbarRef.current.contains(e.target as Node) &&
        !isInsideContentEditable(e.target as Node)
      ) {
        setPos((prev) => ({ ...prev, visible: false }));
        setShowColorPicker(false);
      }
    };
    document.addEventListener("mousedown", handleMouseDown);
    return () => document.removeEventListener("mousedown", handleMouseDown);
  }, [isInsideContentEditable]);

  // ── Komendy formatowania ───────────────────────────────────────────────────

  const exec = useCallback(
    (command: string, value?: string) => {
      document.execCommand(command, false, value);
      checkActiveStates();
    },
    [checkActiveStates]
  );

  const handleColorSelect = useCallback(
    (color: string) => {
      exec("foreColor", color);
      setShowColorPicker(false);
    },
    [exec]
  );

  // ── Render ─────────────────────────────────────────────────────────────────

  if (!pos.visible) return null;

  return (
    <div
      ref={toolbarRef}
      style={{
        position: "fixed",
        top: pos.top,
        left: pos.left,
        transform: "translateX(-50%)",
        zIndex: 9999,
        pointerEvents: pos.visible ? "auto" : "none",
      }}
    >
      <div
        style={{
          display: "inline-flex",
          alignItems: "center",
          gap: 1,
          padding: "4px 6px",
          background: "#fff",
          border: "1px solid #E2E8F0",
          borderRadius: 10,
          boxShadow:
            "0 8px 24px rgba(15,23,42,.12), 0 2px 6px rgba(15,23,42,.06)",
          fontFamily: "Inter, system-ui, sans-serif",
        }}
        onMouseDown={(e) => {
          // Zapobiegnij utracie zaznaczenia przy kliknieciu w toolbar
          e.preventDefault();
        }}
      >
        {/* Bold */}
        <TBtn
          active={activeStates.bold}
          title="Pogrubienie (Ctrl+B)"
          onClick={() => exec("bold")}
        >
          <strong>B</strong>
        </TBtn>

        {/* Italic */}
        <TBtn
          active={activeStates.italic}
          title="Kursywa (Ctrl+I)"
          onClick={() => exec("italic")}
        >
          <em style={{ fontStyle: "italic" }}>I</em>
        </TBtn>

        {/* Underline */}
        <TBtn
          active={activeStates.underline}
          title="Podkreslenie (Ctrl+U)"
          onClick={() => exec("underline")}
        >
          <span style={{ textDecoration: "underline" }}>U</span>
        </TBtn>

        <Sep />

        {/* Color Picker */}
        <div style={{ position: "relative" }}>
          <TBtn
            title="Kolor tekstu"
            onClick={() => setShowColorPicker((prev) => !prev)}
          >
            <svg
              width="14"
              height="14"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2z" />
              <path d="M12 2a4 4 0 014 4c0 2-2 3-2 6h-4c0-3-2-4-2-6a4 4 0 014-4z" />
            </svg>
          </TBtn>
          {showColorPicker && (
            <ColorPickerPopup
              onSelect={handleColorSelect}
              onClose={() => setShowColorPicker(false)}
            />
          )}
        </div>

        <Sep />

        {/* Align Left */}
        <TBtn title="Wyrownaj do lewej" onClick={() => exec("justifyLeft")}>
          <svg
            width="14"
            height="14"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
          >
            <line x1="3" y1="6" x2="21" y2="6" />
            <line x1="3" y1="12" x2="15" y2="12" />
            <line x1="3" y1="18" x2="18" y2="18" />
          </svg>
        </TBtn>

        {/* Align Center */}
        <TBtn title="Wycentruj" onClick={() => exec("justifyCenter")}>
          <svg
            width="14"
            height="14"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
          >
            <line x1="3" y1="6" x2="21" y2="6" />
            <line x1="6" y1="12" x2="18" y2="12" />
            <line x1="4" y1="18" x2="20" y2="18" />
          </svg>
        </TBtn>

        {/* Align Right */}
        <TBtn title="Wyrownaj do prawej" onClick={() => exec("justifyRight")}>
          <svg
            width="14"
            height="14"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
          >
            <line x1="3" y1="6" x2="21" y2="6" />
            <line x1="9" y1="12" x2="21" y2="12" />
            <line x1="6" y1="18" x2="21" y2="18" />
          </svg>
        </TBtn>
      </div>
    </div>
  );
}
