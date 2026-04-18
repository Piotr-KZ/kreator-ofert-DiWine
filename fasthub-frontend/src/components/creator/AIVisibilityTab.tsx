/**
 * AIVisibilityTab — Brief 41: AI Visibility tab for Step 7 Config.
 * Allows users to add structured data for AI search engines (ChatGPT, Gemini, Perplexity).
 */

import { useState } from "react";
import type {
  AIVisibilityData,
  AIVisibilityLink,
  AIVisibilityCategoryItem,
  AIVisibilityPerson,
} from "@/types/creator";

// ─── Constants ───

const COMPANY_CATEGORIES = [
  { key: "produkty", label: "Produkty" },
  { key: "uslugi", label: "Usługi" },
  { key: "projekty", label: "Projekty / realizacje" },
  { key: "metodyki", label: "Metodyki / podejścia" },
  { key: "certyfikaty", label: "Certyfikaty i uprawnienia" },
  { key: "opinie", label: "Opinie i rekomendacje" },
  { key: "artykuly", label: "Artykuły / publikacje" },
  { key: "oddzialy", label: "Oddziały" },
  { key: "sukcesy", label: "Sukcesy firmy" },
] as const;

const PERSON_CATEGORIES = [
  { key: "kompetencje", label: "Kompetencje" },
  { key: "doswiadczenie", label: "Doświadczenie zawodowe" },
  { key: "wyksztalcenie", label: "Wykształcenie" },
  { key: "sukcesy", label: "Sukcesy / osiągnięcia" },
  { key: "certyfikaty", label: "Certyfikaty" },
  { key: "uslugi", label: "Usługi" },
  { key: "metodyki", label: "Metodyki" },
  { key: "projekty", label: "Projekty" },
  { key: "artykuly", label: "Artykuły / publikacje" },
  { key: "opinie", label: "Opinie i rekomendacje" },
] as const;

const CATEGORY_LABELS: Record<string, string> = {};
for (const c of COMPANY_CATEGORIES) CATEGORY_LABELS[c.key] = c.label;
for (const c of PERSON_CATEGORIES) CATEGORY_LABELS[c.key] = c.label;

const SOCIAL_SUGGESTIONS = ["Facebook", "LinkedIn", "Instagram", "YouTube", "X/Twitter", "TikTok", "Pinterest"];

interface Props {
  data: AIVisibilityData;
  onChange: (data: AIVisibilityData) => void;
}

const inputClass = "w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500";
const labelClass = "block text-sm font-medium text-gray-700 mb-1";
const btnSecondary = "px-3 py-1.5 text-sm border border-gray-200 rounded-lg hover:bg-gray-50 text-gray-700";
const btnDanger = "p-1 text-gray-400 hover:text-red-500 transition-colors";

// ─── Sub-components ───

function LinkList({
  items,
  onChange,
  addLabel,
  namePlaceholder,
  suggestions,
}: {
  items: AIVisibilityLink[];
  onChange: (items: AIVisibilityLink[]) => void;
  addLabel: string;
  namePlaceholder: string;
  suggestions?: string[];
}) {
  const [showSuggestions, setShowSuggestions] = useState(false);

  const update = (idx: number, field: keyof AIVisibilityLink, value: string) => {
    const next = [...items];
    next[idx] = { ...next[idx], [field]: value };
    onChange(next);
  };

  const remove = (idx: number) => onChange(items.filter((_, i) => i !== idx));

  const add = (name = "") => {
    onChange([...items, { name, url: "" }]);
    setShowSuggestions(false);
  };

  return (
    <div className="space-y-2">
      {items.map((item, idx) => (
        <div key={idx} className="flex gap-2 items-start">
          <input
            type="text"
            className={inputClass}
            placeholder={namePlaceholder}
            value={item.name}
            onChange={(e) => update(idx, "name", e.target.value)}
            style={{ maxWidth: "180px" }}
          />
          <input
            type="url"
            className={`${inputClass} flex-1`}
            placeholder="https://..."
            value={item.url}
            onChange={(e) => update(idx, "url", e.target.value)}
          />
          <button type="button" onClick={() => remove(idx)} className={btnDanger} title="Usuń">
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      ))}
      <div className="relative">
        {suggestions ? (
          <>
            <button type="button" className={btnSecondary} onClick={() => setShowSuggestions(!showSuggestions)}>
              + {addLabel}
            </button>
            {showSuggestions && (
              <div className="absolute z-10 mt-1 bg-white border border-gray-200 rounded-lg shadow-lg py-1 min-w-[200px]">
                {suggestions
                  .filter((s) => !items.some((i) => i.name === s))
                  .map((s) => (
                    <button
                      key={s}
                      type="button"
                      className="block w-full text-left px-3 py-1.5 text-sm hover:bg-gray-50"
                      onClick={() => add(s)}
                    >
                      {s}
                    </button>
                  ))}
                <button
                  type="button"
                  className="block w-full text-left px-3 py-1.5 text-sm hover:bg-gray-50 border-t border-gray-100"
                  onClick={() => add("")}
                >
                  Inne...
                </button>
              </div>
            )}
          </>
        ) : (
          <button type="button" className={btnSecondary} onClick={() => add("")}>
            + {addLabel}
          </button>
        )}
      </div>
    </div>
  );
}

function CategoryItemsList({
  catKey,
  items,
  onChange,
  onRemoveCategory,
}: {
  catKey: string;
  items: AIVisibilityCategoryItem[];
  onChange: (items: AIVisibilityCategoryItem[]) => void;
  onRemoveCategory: () => void;
}) {
  const isExperience = catKey === "doswiadczenie";
  const isEducation = catKey === "wyksztalcenie";

  const update = (idx: number, field: string, value: string) => {
    const next = [...items];
    next[idx] = { ...next[idx], [field]: value };
    onChange(next);
  };

  const remove = (idx: number) => onChange(items.filter((_, i) => i !== idx));

  const add = () => {
    const empty: AIVisibilityCategoryItem = { name: "", description: "" };
    if (isExperience) empty.period = "";
    if (isEducation) {
      empty.school = "";
      empty.title = "";
    }
    onChange([...items, empty]);
  };

  const addLabel = CATEGORY_LABELS[catKey]
    ? `Dodaj ${CATEGORY_LABELS[catKey].toLowerCase().replace(/\s*\/.*/, "").replace(/\s*i\s.*/, "")}`
    : "Dodaj";

  return (
    <div className="border border-gray-200 rounded-lg p-4 space-y-3">
      <div className="flex items-center justify-between">
        <h4 className="text-sm font-semibold text-gray-800">{CATEGORY_LABELS[catKey] || catKey}</h4>
        <button type="button" onClick={onRemoveCategory} className={btnDanger} title="Usuń kategorię">
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      {items.map((item, idx) => (
        <div key={idx} className="flex gap-2 items-start">
          {isEducation ? (
            <>
              <input
                type="text"
                className={inputClass}
                placeholder="Szkoła / uczelnia"
                value={item.school || ""}
                onChange={(e) => update(idx, "school", e.target.value)}
                style={{ maxWidth: "180px" }}
              />
              <input
                type="text"
                className={inputClass}
                placeholder="Tytuł / kierunek"
                value={item.title || ""}
                onChange={(e) => update(idx, "title", e.target.value)}
                style={{ maxWidth: "180px" }}
              />
            </>
          ) : (
            <input
              type="text"
              className={inputClass}
              placeholder={isExperience ? "Nazwa firmy" : "Nazwa"}
              value={item.name}
              onChange={(e) => update(idx, "name", e.target.value)}
              style={{ maxWidth: "180px" }}
            />
          )}
          {isExperience && (
            <input
              type="text"
              className={inputClass}
              placeholder="np. 2010-2020"
              value={item.period || ""}
              onChange={(e) => update(idx, "period", e.target.value)}
              style={{ maxWidth: "120px" }}
            />
          )}
          <textarea
            className={`${inputClass} flex-1`}
            placeholder="Opis"
            rows={1}
            value={item.description || ""}
            onChange={(e) => update(idx, "description", e.target.value)}
          />
          <button type="button" onClick={() => remove(idx)} className={btnDanger} title="Usuń">
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      ))}

      <button type="button" className={btnSecondary} onClick={add}>
        + {addLabel}
      </button>
    </div>
  );
}

function AddCategoryDropdown({
  existingKeys,
  categories,
  onAdd,
}: {
  existingKeys: string[];
  categories: readonly { key: string; label: string }[];
  onAdd: (key: string) => void;
}) {
  const [open, setOpen] = useState(false);
  const available = categories.filter((c) => !existingKeys.includes(c.key));

  if (available.length === 0) return null;

  return (
    <div className="relative inline-block">
      <button type="button" className={btnSecondary} onClick={() => setOpen(!open)}>
        + Dodaj kategorię ▾
      </button>
      {open && (
        <div className="absolute z-10 mt-1 bg-white border border-gray-200 rounded-lg shadow-lg py-1 min-w-[240px]">
          {available.map((cat) => (
            <button
              key={cat.key}
              type="button"
              className="block w-full text-left px-3 py-2 text-sm hover:bg-gray-50"
              onClick={() => {
                onAdd(cat.key);
                setOpen(false);
              }}
            >
              {cat.label}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

function PersonCard({
  person,
  index,
  onChange,
  onRemove,
}: {
  person: AIVisibilityPerson;
  index: number;
  onChange: (person: AIVisibilityPerson) => void;
  onRemove: () => void;
}) {
  const categories = person.categories || {};
  const existingKeys = Object.keys(categories);

  const updateField = (field: keyof AIVisibilityPerson, value: string) => {
    onChange({ ...person, [field]: value });
  };

  const updateCategory = (catKey: string, items: AIVisibilityCategoryItem[]) => {
    onChange({ ...person, categories: { ...categories, [catKey]: items } });
  };

  const addCategory = (catKey: string) => {
    onChange({ ...person, categories: { ...categories, [catKey]: [] } });
  };

  const removeCategory = (catKey: string) => {
    const next = { ...categories };
    delete next[catKey];
    onChange({ ...person, categories: next });
  };

  return (
    <div className="border border-indigo-200 rounded-lg p-4 space-y-4 bg-indigo-50/30">
      <div className="flex items-center justify-between">
        <h4 className="text-sm font-semibold text-indigo-800">
          {person.name || `Osoba ${index + 1}`}
          {person.title ? ` — ${person.title}` : ""}
        </h4>
        <button type="button" onClick={onRemove} className={btnDanger} title="Usuń osobę">
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      <div className="grid grid-cols-2 gap-3">
        <div>
          <label className={labelClass}>Imię i nazwisko *</label>
          <input
            type="text"
            className={inputClass}
            placeholder="Jan Kowalski"
            value={person.name}
            onChange={(e) => updateField("name", e.target.value)}
          />
        </div>
        <div>
          <label className={labelClass}>Funkcja / stanowisko</label>
          <input
            type="text"
            className={inputClass}
            placeholder="CEO / Trener sprzedaży"
            value={person.title || ""}
            onChange={(e) => updateField("title", e.target.value)}
          />
        </div>
      </div>

      {Object.entries(categories).map(([catKey, items]) => (
        <CategoryItemsList
          key={catKey}
          catKey={catKey}
          items={items}
          onChange={(newItems) => updateCategory(catKey, newItems)}
          onRemoveCategory={() => removeCategory(catKey)}
        />
      ))}

      <AddCategoryDropdown
        existingKeys={existingKeys}
        categories={PERSON_CATEGORIES}
        onAdd={addCategory}
      />
    </div>
  );
}

// ─── Main Component ───

export default function AIVisibilityTab({ data, onChange }: Props) {
  const socialProfiles = data.social_profiles || [];
  const websites = data.websites || [];
  const categories = data.categories || {};
  const people = data.people || [];
  const existingCatKeys = Object.keys(categories);

  const updateField = (field: keyof AIVisibilityData, value: unknown) => {
    onChange({ ...data, [field]: value });
  };

  const updateCategory = (catKey: string, items: AIVisibilityCategoryItem[]) => {
    updateField("categories", { ...categories, [catKey]: items });
  };

  const addCompanyCategory = (catKey: string) => {
    updateField("categories", { ...categories, [catKey]: [] });
  };

  const removeCompanyCategory = (catKey: string) => {
    const next = { ...categories };
    delete next[catKey];
    updateField("categories", next);
  };

  const updatePerson = (idx: number, person: AIVisibilityPerson) => {
    const next = [...people];
    next[idx] = person;
    updateField("people", next);
  };

  const addPerson = () => {
    updateField("people", [...people, { name: "", title: "", categories: {} }]);
  };

  const removePerson = (idx: number) => {
    updateField("people", people.filter((_, i) => i !== idx));
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-lg font-semibold mb-1">Widoczność AI</h2>
        <p className="text-sm text-gray-500 mb-4">
          Wyszukiwarki AI (ChatGPT, Gemini, Perplexity) nie czytają strony jak ludzie.
          Czytają dane strukturalne — konkretne fakty, liczby, powiązania.
          Im więcej precyzyjnych danych podasz, tym częściej AI poleci Twoją firmę.
        </p>
        <p className="text-xs text-gray-400 mb-4">
          Te dane NIE pojawią się na stronie — trafią do kodu który widzą tylko roboty AI.
        </p>
      </div>

      {/* Company description */}
      <div>
        <label className={labelClass}>Opis firmy</label>
        <textarea
          className={inputClass}
          rows={4}
          placeholder="Czym się zajmujesz, od kiedy, dla kogo, co Cię wyróżnia..."
          value={data.description || ""}
          onChange={(e) => updateField("description", e.target.value)}
        />
      </div>

      {/* Two columns: Social profiles + Websites */}
      <div className="grid grid-cols-2 gap-6">
        <div>
          <label className={labelClass}>Profile społecznościowe</label>
          <LinkList
            items={socialProfiles}
            onChange={(items) => updateField("social_profiles", items)}
            addLabel="Dodaj profil"
            namePlaceholder="np. Facebook"
            suggestions={SOCIAL_SUGGESTIONS}
          />
        </div>
        <div>
          <label className={labelClass}>Strony www i serwisy</label>
          <LinkList
            items={websites}
            onChange={(items) => updateField("websites", items)}
            addLabel="Dodaj stronę"
            namePlaceholder="np. Strona główna"
          />
        </div>
      </div>

      {/* Company categories */}
      {Object.entries(categories).map(([catKey, items]) => (
        <CategoryItemsList
          key={catKey}
          catKey={catKey}
          items={items}
          onChange={(newItems) => updateCategory(catKey, newItems)}
          onRemoveCategory={() => removeCompanyCategory(catKey)}
        />
      ))}

      <AddCategoryDropdown
        existingKeys={existingCatKeys}
        categories={COMPANY_CATEGORIES}
        onAdd={addCompanyCategory}
      />

      {/* Separator */}
      <hr className="border-gray-200" />

      {/* Key people */}
      <div>
        <h3 className="text-md font-semibold mb-3">Kluczowe osoby</h3>

        <div className="space-y-4">
          {people.map((person, idx) => (
            <PersonCard
              key={idx}
              person={person}
              index={idx}
              onChange={(p) => updatePerson(idx, p)}
              onRemove={() => removePerson(idx)}
            />
          ))}
        </div>

        <button type="button" className={`${btnSecondary} mt-3`} onClick={addPerson}>
          + Dodaj osobę
        </button>
      </div>
    </div>
  );
}
