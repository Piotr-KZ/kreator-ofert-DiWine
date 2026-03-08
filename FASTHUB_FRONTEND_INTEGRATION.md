# FASTHUB FRONTEND — Design System & Integration Guide
## Extracted from WebCreator Mockup Project

---

## 1. OVERVIEW

FastHub currently has: FastAPI backend + PostgreSQL + Redis + Docker.
FastHub does NOT have: production frontend.

This document provides a complete frontend foundation based on the WebCreator design system built during mockup phase. It includes: design tokens, reusable components, layout patterns, page templates, and integration instructions.

**Stack:**
- React 18 + Vite
- Tailwind CSS (utility-first, no Ant Design)
- Google Fonts: Outfit (wght 300-800)
- No external component library — custom components below

**Why Tailwind instead of Ant Design:**
- Lighter (no 300kb bundle)
- Full control over design
- Consistent with client-facing pages (klocki stron)
- Ant Design was originally planned but mockup phase proved Tailwind is sufficient

---

## 2. DESIGN TOKENS

```css
/* fonts */
--font-primary: 'Outfit', system-ui, sans-serif;

/* colors - brand */
--color-primary: #4F46E5;       /* indigo-600 */
--color-primary-hover: #4338CA;  /* indigo-700 */
--color-primary-light: #EEF2FF; /* indigo-50 */
--color-primary-border: #C7D2FE; /* indigo-200 */

/* colors - feedback */
--color-success: #22C55E;        /* green-500 */
--color-success-light: #F0FDF4;  /* green-50 */
--color-success-border: #BBF7D0; /* green-200 */
--color-warning: #F59E0B;        /* amber-500 */
--color-warning-light: #FFFBEB;  /* amber-50 */
--color-danger: #EF4444;         /* red-500 (errors, delete) */
--color-danger-light: #FEF2F2;   /* red-50 */

/* colors - selection (green = selected state for all interactive elements) */
--color-selected: #4ADE80;       /* green-400 */
--color-selected-bg: #F0FDF4;    /* green-50 */
--color-selected-border: #4ADE80; /* green-400 */

/* colors - neutral */
--color-bg: #F9FAFB;            /* gray-50 */
--color-surface: #FFFFFF;
--color-border: #E5E7EB;        /* gray-200 */
--color-text: #111827;           /* gray-900 */
--color-text-secondary: #6B7280; /* gray-500 */
--color-text-muted: #9CA3AF;    /* gray-400 */
--color-dark: #030712;           /* gray-950 */

/* spacing */
--radius-sm: 0.5rem;   /* 8px - buttons, inputs */
--radius-md: 0.75rem;  /* 12px - cards */
--radius-lg: 1rem;     /* 16px - modals, sections */
--radius-xl: 1.5rem;   /* 24px - hero sections */

/* shadows */
--shadow-sm: 0 1px 2px rgba(0,0,0,0.05);
--shadow-md: 0 4px 6px rgba(0,0,0,0.07);
```

---

## 3. COMPONENT LIBRARY

### 3.1 Buttons

```jsx
// Primary (indigo), Ghost (white+border), Danger (red), Secondary (dark)
function Btn({ children, onClick, variant = "primary", className, disabled }) {
  const styles = {
    primary: "bg-indigo-600 text-white hover:bg-indigo-700",
    secondary: "bg-gray-900 text-white hover:bg-gray-800",
    ghost: "bg-white text-gray-700 border-2 border-gray-200 hover:border-gray-300",
    danger: "bg-red-600 text-white hover:bg-red-700",
  };
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={`px-6 py-2.5 rounded-xl font-semibold text-sm transition-all
        ${styles[variant]} ${disabled ? "opacity-50 cursor-not-allowed" : ""}
        ${className || ""}`}
    >
      {children}
    </button>
  );
}
```

### 3.2 Form Fields

```jsx
// Text input / Textarea with label
function Fld({ label, placeholder, value, onChange, large, disabled, error }) {
  const base = `w-full px-4 py-3 border-2 rounded-xl text-sm outline-none transition-all
    ${error ? "border-red-300 focus:border-red-400 focus:ring-red-100" :
      "border-gray-200 focus:border-indigo-400 focus:ring-indigo-100"}
    ${disabled ? "bg-gray-50 border-gray-100 text-gray-400" : ""}
    focus:ring-2`;
  return (
    <div>
      {label && <label className="block text-sm font-medium text-gray-700 mb-1.5">{label}</label>}
      {large
        ? <textarea rows={typeof large === "number" ? large : 4}
            placeholder={placeholder} value={value || ""}
            onChange={e => onChange?.(e.target.value)}
            className={base + " resize-none"} disabled={disabled} />
        : <input type="text" placeholder={placeholder} value={value || ""}
            onChange={e => onChange?.(e.target.value)}
            className={base} disabled={disabled} />
      }
      {error && <p className="text-xs text-red-500 mt-1">{error}</p>}
    </div>
  );
}
```

### 3.3 Selection Components (Green = Selected)

```jsx
// Tile — large clickable card (single/multi select)
function Tile({ on, onClick, children, className }) {
  return (
    <button onClick={onClick}
      className={`text-left p-4 rounded-xl border-2 transition-all w-full
        ${on ? "border-green-400 bg-green-50" : "border-gray-200 bg-white hover:border-gray-300"}
        ${className || ""}`}>
      {children}
    </button>
  );
}

// Checkbox — multi-select with checkmark
function Chk({ on, onClick, children }) {
  return (
    <button onClick={onClick}
      className={`text-left p-3 rounded-lg border-2 transition-all flex items-center gap-3 w-full
        ${on ? "border-green-400 bg-green-50" : "border-gray-200 bg-white hover:border-gray-300"}`}>
      <div className={`w-5 h-5 rounded flex-shrink-0 flex items-center justify-center border-2
        ${on ? "bg-green-500 border-green-500" : "border-gray-300"}`}>
        {on && <svg className="w-3 h-3 text-white" fill="none" stroke="currentColor" strokeWidth={3} viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7"/>
        </svg>}
      </div>
      {children}
    </button>
  );
}

// Radio — single select with dot
function Rad({ on, onClick, children }) {
  return (
    <button onClick={onClick}
      className={`text-left p-3.5 rounded-xl border-2 transition-all flex items-center gap-4 w-full
        ${on ? "border-green-400 bg-green-50" : "border-gray-200 bg-white hover:border-gray-300"}`}>
      <div className={`w-4 h-4 rounded-full flex-shrink-0 border-2 flex items-center justify-center
        ${on ? "border-green-500" : "border-gray-300"}`}>
        {on && <div className="w-2 h-2 rounded-full bg-green-500" />}
      </div>
      {children}
    </button>
  );
}

// Toggle — on/off switch
function Toggle({ on, onClick, label }) {
  return (
    <div className="flex items-center gap-3">
      <div className={`w-10 h-6 rounded-full relative cursor-pointer transition-colors
        ${on ? "bg-green-500" : "bg-gray-300"}`} onClick={onClick}>
        <div className={`w-4 h-4 bg-white rounded-full absolute top-1 shadow transition-all
          ${on ? "right-1" : "left-1"}`} />
      </div>
      {label && <span className="text-sm font-medium text-gray-700">{label}</span>}
    </div>
  );
}
```

### 3.4 Layout Components

```jsx
// Section card — white box with title and description
function SectionCard({ title, desc, children }) {
  return (
    <div className="bg-white border-2 border-gray-200 rounded-xl p-6 mb-4">
      {title && <h3 className="font-semibold text-gray-900 mb-1">{title}</h3>}
      {desc && <p className="text-sm text-gray-500 mb-4">{desc}</p>}
      {children}
    </div>
  );
}

// Labeled field group with number
function Lbl({ num, title, sub }) {
  return (
    <div className="flex items-start gap-3 mb-4">
      <div className="w-7 h-7 rounded-lg bg-indigo-100 flex items-center justify-center flex-shrink-0">
        <span className="text-indigo-700 text-xs font-bold">{num}</span>
      </div>
      <div>
        <h3 className="font-semibold text-gray-900 text-sm">{title}</h3>
        {sub && <p className="text-xs text-gray-500 mt-0.5">{sub}</p>}
      </div>
    </div>
  );
}
```

---

## 4. LAYOUT PATTERNS

### 4.1 App Shell — Dark Header + Sidebar + Main

```
┌──────────────────────────────────────────┐
│  HEADER (bg-gray-950, white text)        │
│  Logo | Nav tabs | User avatar           │
├──────────┬───────────────────────────────┤
│ SIDEBAR  │  MAIN CONTENT                │
│ (white)  │  (bg-gray-50)                │
│ 220px    │  flex-1, overflow-auto        │
│          │                               │
│ Nav items│  Page content here            │
│          │                               │
└──────────┴───────────────────────────────┘
```

Used in: Dashboard, Konto, Integracje, Admin panels.

### 4.2 Wizard — Steps Header + Content

```
┌──────────────────────────────────────────┐
│  HEADER (bg-gray-950)                    │
│  ← Back | Logo | Project name | Save    │
├──────────────────────────────────────────┤
│  STEPS BAR (white, border-b)            │
│  ①─②─③─④─⑤─⑥─⑦─⑧─⑨                   │
├──────────────────────────────────────────┤
│  CONTENT (bg-gray-50, p-8, scrollable)  │
│  max-w-3xl mx-auto                       │
│  Questions, forms, selections            │
│  [Dalej →] button at bottom              │
└──────────────────────────────────────────┘
```

Used in: Kreator stron (9 steps), Dunning path creator.

### 4.3 Immersive — No Header, Full Width

```
┌──────────────────────────────────────────┐
│  SLIM BAR (← Powrót do menu)            │
├──────────────────────────────────────────┤
│  TOOLBAR (sticky)                        │
│  Mode toggle | Responsive icons          │
├──────┬───────────────────────┬───────────┤
│ SIDE │  CANVAS               │           │
│ PANEL│  (full preview)       │           │
│      │                       │           │
└──────┴───────────────────────┴───────────┘
```

Used in: Step 5 (wireframe), Step 6 (preview with colors).

### 4.4 Table Page

```
┌──────────────────────────────────────────┐
│  Title                        [+ Button] │
├──────────────────────────────────────────┤
│  Col1 │ Col2 │ Col3 │ Status │ Actions  │
│──────────────────────────────────────────│
│  Row  │      │      │ Badge  │ Edit Del │
│  Row  │      │      │ Badge  │ Edit Del │
└──────────────────────────────────────────┘
```

Used in: Moje strony, Faktury, Aktywne windykacje.

---

## 5. PAGE TEMPLATES (ready to implement)

### 5.1 Pages from mockups:

| Page | Layout | Source file |
|------|--------|------------|
| Moje strony | Table Page | kreator-v15.jsx (dashTab="strony") |
| Dashboard strony | Sidebar + Main with tabs | kreator-v15.jsx (ActiveSites) |
| Integracje (marketplace) | Sidebar categories + 2-col grid | kreator-v15.jsx (IntegrationsPage) |
| Kreator stron (9 etapów) | Wizard | kreator-v15.jsx (Step1-Step9) |
| Konto — Profil | Sidebar + Form | konto-v3.jsx (TabProfile) |
| Konto — Firma | Sidebar + Form + GUS | konto-v3.jsx (TabCompany) |
| Konto — Plan | Sidebar + Cards | konto-v3.jsx (TabPlan) |
| Konto — Płatności | Sidebar + Table | konto-v3.jsx (TabPayments) |
| Konto — Faktury | Sidebar + Table | konto-v3.jsx (TabInvoices) |
| Konto — Bezpieczeństwo | Sidebar + Forms | konto-v3.jsx (TabSecurity) |
| Konto — Zespół | Sidebar + Table + Roles matrix | konto-v3.jsx (TabTeam) |
| Konto — Powiadomienia | Sidebar + Toggles | konto-v3.jsx (TabNotifications) |
| Konto — API | Sidebar + Keys + Webhook | konto-v3.jsx (TabAPI) |
| Admin — Kreator dunning | Wizard + Timeline | kreator-dunning.jsx |

### 5.2 Pages to build:

| Page | Layout | Notes |
|------|--------|-------|
| Login | Centered card | Email + hasło + "Zaloguj" + "Zarejestruj" |
| Rejestracja | Wizard 3-step | Krok 1: firma/osoba, Krok 2: NIP → GUS auto-fill, Krok 3: plan |
| Reset hasła | Centered card | Email + "Wyślij link" |
| Admin — Użytkownicy | Table Page | Lista klientów z filtrami |
| Admin — Plany | Table + Edit | CRUD planów abonamentowych |
| Admin — Statystyki | Dashboard | MRR, churn, użytkownicy, strony |
| Admin — Ustawienia | Forms | Konfiguracja globalna |
| 404 | Centered | Ilustracja + "Wróć do strony głównej" |

---

## 6. INTEGRATION STEPS FOR FASTHUB

### 6.1 Setup (one-time)

```bash
# In FastHub repo root
cd frontend  # or create if doesn't exist

# Init Vite + React
npm create vite@latest . -- --template react
npm install

# Tailwind CSS
npm install -D tailwindcss @tailwindcss/typography postcss autoprefixer
npx tailwindcss init -p

# Router
npm install react-router-dom

# HTTP client
npm install axios

# Date formatting
npm install date-fns
```

### 6.2 Tailwind config

```js
// tailwind.config.js
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      fontFamily: {
        sans: ["'Outfit'", "system-ui", "sans-serif"],
      },
    },
  },
  plugins: [require("@tailwindcss/typography")],
};
```

### 6.3 Project structure

```
frontend/
├── public/
├── src/
│   ├── components/
│   │   ├── ui/              # Design system primitives
│   │   │   ├── Btn.jsx
│   │   │   ├── Fld.jsx
│   │   │   ├── Tile.jsx
│   │   │   ├── Chk.jsx
│   │   │   ├── Rad.jsx
│   │   │   ├── Toggle.jsx
│   │   │   ├── SectionCard.jsx
│   │   │   ├── Lbl.jsx
│   │   │   └── index.js     # barrel export
│   │   ├── layout/
│   │   │   ├── AppShell.jsx  # Header + Sidebar + Main
│   │   │   ├── Wizard.jsx    # Steps header + content
│   │   │   └── Immersive.jsx # Full-width canvas
│   │   └── shared/
│   │       ├── DataTable.jsx
│   │       ├── Modal.jsx
│   │       ├── StatusBadge.jsx
│   │       └── EmptyState.jsx
│   ├── pages/
│   │   ├── auth/
│   │   │   ├── Login.jsx
│   │   │   ├── Register.jsx
│   │   │   └── ResetPassword.jsx
│   │   ├── dashboard/
│   │   │   ├── MySites.jsx
│   │   │   ├── SiteDashboard.jsx
│   │   │   └── Integrations.jsx
│   │   ├── kreator/
│   │   │   ├── KreatorShell.jsx
│   │   │   ├── Step1Brief.jsx
│   │   │   ├── Step2Materials.jsx
│   │   │   ├── Step3Style.jsx
│   │   │   ├── Step4Validation.jsx
│   │   │   ├── Step5Structure.jsx
│   │   │   ├── Step6Preview.jsx
│   │   │   ├── Step7Config.jsx
│   │   │   ├── Step8Check.jsx
│   │   │   └── Step9Publish.jsx
│   │   ├── account/
│   │   │   ├── Profile.jsx
│   │   │   ├── Company.jsx
│   │   │   ├── Plan.jsx
│   │   │   ├── Payments.jsx
│   │   │   ├── Invoices.jsx
│   │   │   ├── Security.jsx
│   │   │   ├── Team.jsx
│   │   │   ├── Notifications.jsx
│   │   │   └── ApiKeys.jsx
│   │   └── admin/
│   │       ├── DunningCreator.jsx
│   │       ├── Users.jsx
│   │       └── Stats.jsx
│   ├── hooks/
│   │   ├── useAuth.js
│   │   ├── useApi.js
│   │   └── useProject.js
│   ├── api/
│   │   ├── client.js         # Axios instance with auth
│   │   ├── auth.js
│   │   ├── projects.js
│   │   ├── subscriptions.js
│   │   └── integrations.js
│   ├── store/
│   │   └── useStore.js       # Zustand or Context
│   ├── App.jsx               # Router
│   ├── main.jsx
│   └── index.css             # Tailwind directives + Outfit font
├── index.html
├── package.json
├── tailwind.config.js
├── postcss.config.js
└── vite.config.js
```

### 6.4 API Client

```jsx
// src/api/client.js
import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "/api",
  headers: { "Content-Type": "application/json" },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

api.interceptors.response.use(
  (res) => res,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem("token");
      window.location.href = "/login";
    }
    return Promise.reject(err);
  }
);

export default api;
```

### 6.5 Router

```jsx
// src/App.jsx
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AppShell } from "./components/layout/AppShell";
import Login from "./pages/auth/Login";
import MySites from "./pages/dashboard/MySites";
import SiteDashboard from "./pages/dashboard/SiteDashboard";
import Integrations from "./pages/dashboard/Integrations";
import KreatorShell from "./pages/kreator/KreatorShell";
// ... account, admin pages

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Public */}
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />

        {/* Authenticated — AppShell layout */}
        <Route element={<AppShell />}>
          <Route path="/" element={<Navigate to="/sites" />} />
          <Route path="/sites" element={<MySites />} />
          <Route path="/dashboard/:siteId" element={<SiteDashboard />} />
          <Route path="/integrations" element={<Integrations />} />
          <Route path="/account/*" element={<AccountRoutes />} />
        </Route>

        {/* Kreator — own layout (wizard) */}
        <Route path="/kreator/:projectId" element={<KreatorShell />} />

        {/* Admin */}
        <Route path="/admin/*" element={<AdminRoutes />} />
      </Routes>
    </BrowserRouter>
  );
}
```

---

## 7. MAPPING FASTHUB API → FRONTEND

| Frontend page | FastHub API endpoint | Notes |
|---|---|---|
| Login | POST /api/auth/login | JWT token |
| Register | POST /api/auth/register | + GUS lookup |
| MySites | GET /api/projects | List all user projects |
| Create site | POST /api/projects | New project |
| Kreator Step 1 | PUT /api/projects/{id}/brief | Save brief data |
| Kreator Step 2 | POST /api/projects/{id}/materials | Upload files |
| Kreator Step 3 | PUT /api/projects/{id}/style | Save style config |
| Kreator Step 4 | POST /api/projects/{id}/validate | AI validation |
| Kreator Step 5 | PUT /api/projects/{id}/structure | Save sections |
| Kreator Step 6 | GET /api/projects/{id}/preview | Render preview |
| Kreator Step 7 | PUT /api/projects/{id}/config | Tech config |
| Kreator Step 9 | POST /api/projects/{id}/publish | Publish site |
| Dashboard | GET /api/projects/{id}/stats | Site statistics |
| Integrations | GET /api/integrations | List available |
| Connect integration | POST /api/integrations/{id}/connect | Provider config |
| Account | GET/PUT /api/users/me | Profile data |
| Company | GET/PUT /api/organizations/{id} | Org data + GUS |
| Plan | GET /api/subscriptions/current | Current plan |
| Payments | GET /api/payments | Payment history |
| Invoices | GET /api/invoices | Invoice list |
| Team | GET /api/organizations/{id}/members | Team members |
| Admin Dunning | GET/POST /api/admin/dunning-paths | Path CRUD |

---

## 8. DESIGN RULES (enforced across all pages)

1. **Selection = green** — every Tile, Chk, Rad, Toggle uses green-400/green-50 when selected
2. **No emoji icons** — use text, badges, or minimal SVG only
3. **Font: Outfit** — everywhere, weights 300-800
4. **Border radius: xl (1rem)** — for cards, inputs, buttons. Consistent.
5. **Spacing: p-4/p-6/p-8** — consistent padding in cards and sections
6. **Dark header** — bg-gray-950, always visible, logo + nav + user
7. **White sidebar** — 220px, border-r, nav items with active state bg-indigo-50
8. **Gray-50 background** — main content area, always
9. **Tables** — rounded-xl border, bg-gray-50 header, hover:bg-gray-50 rows
10. **Modals** — bg-black/50 overlay, rounded-2xl, max-w-3xl, scrollable body
11. **Status badges** — green-100/green-700 (success), amber-100/amber-700 (warning), red-100/red-700 (error), gray-100/gray-500 (inactive)
12. **Details/summary** — for expandable sections (SEO per page, integrations, legal)
13. **Communication first** — every section starts with clear explanation of what and why
14. **Progressive disclosure** — show only what's needed, expand on click

---

## 9. MIGRATION CHECKLIST

- [ ] Create frontend/ directory in FastHub repo
- [ ] Init Vite + React + Tailwind
- [ ] Copy component library (Section 3) to src/components/ui/
- [ ] Copy layout patterns (Section 4) to src/components/layout/
- [ ] Setup router (Section 6.5)
- [ ] Setup API client (Section 6.4)
- [ ] Build Login + Register pages
- [ ] Build MySites page (table)
- [ ] Build KreatorShell + Step 1 (proof of concept)
- [ ] Build Account pages
- [ ] Connect to FastHub API endpoints
- [ ] Build Admin — Dunning creator
- [ ] Test full flow: register → create site → kreator → publish → dashboard
