# BRIEF 1: FastHub Frontend — Modernizacja Fundamentu

## Dla: Opus CLI (kodowanie)
## Od: Strategia (planowanie i weryfikacja)
## Data: 2026-03-08

---

## KONTEKST

FastHub to boilerplate SaaS (FastAPI + PostgreSQL + Redis + React). Backend jest solidny. Frontend wymaga gruntownej modernizacji — jest w stanie "demo", ma pomieszany branding (AutoFlow/FastHub), używa ciężkiego Ant Design (300KB), ma hardcodowane nazwy produktu w wielu plikach, a część endpointów jest źle podłączona.

Ten brief dotyczy **Fazy 1 — budowy solidnego fundamentu frontendowego**. Faza 2 (naprawa integracji z backendem) będzie osobnym zleceniem po weryfikacji Fazy 1.

---

## CEL

Wymienić silnik frontendowy FastHub:
- Z Ant Design → na Tailwind CSS + własne komponenty UI
- Z hardcodowanego brandingu → na centralny plik konfiguracyjny
- Z obecnego zepsutego API clienta → na poprawny z obsługą tokenów
- Zachować TypeScript (konwertować nowe komponenty JSX → TSX)
- Zachować pełną funkcjonalność którą użytkownik ma dziś

---

## DOSTARCZONO (pliki wejściowe)

### 1. Nowe komponenty UI (JSX → do konwersji na TSX)
Lokalizacja: `fasthub-frontend-starter.zip` — rozpakowane do `fasthub-frontend/src/components/`

**Komponenty UI (`components/ui/`):**
- `Btn` — przycisk (warianty: primary, secondary, ghost, danger)
- `Fld` — pole formularza (input + textarea, label, error, disabled)
- `Tile` — kafelek wyboru (zielony border gdy zaznaczony)
- `Chk` — checkbox z checkmarkiem (zielony gdy zaznaczony)
- `Rad` — radio button z kropką (zielony gdy zaznaczony)
- `Toggle` — przełącznik on/off (zielony gdy włączony)
- `SectionCard` — karta sekcji (biała, border, title + desc)
- `Lbl` — etykieta z numerem (numer w indigo kółku + tytuł + opis)
- `StatusBadge` — badge statusu (success/warning/error/info/neutral)
- Barrel export w `index.js`

**Layouty (`components/layout/`):**
- `AppShell` — ciemny header + główna treść (Outlet)
- `SidebarLayout` — sidebar z tabami + treść (do stron Settings/Account)
- `WizardLayout` — header + pasek kroków + treść (do kreatora — przyszłość)

### 2. Design System (FASTHUB_FRONTEND_INTEGRATION.md)
Kompletny przewodnik: design tokens, kolory, typografia (Outfit 300-800), zaokrąglenia, cienie, zasady projektowe.

### 3. Istniejący frontend FastHub
Lokalizacja: `fasthub-frontend/` w repozytorium
Stack: React 19 + TypeScript + Vite + Ant Design 6 + Zustand + React Router 7 + Axios + Recharts

---

## ZAKRES PRACY

### KROK 1: Plik konfiguracyjny aplikacji

Utwórz `src/config/app.config.ts`:

```typescript
export const APP_CONFIG = {
  // Branding
  name: "FastHub",
  shortName: "FH",
  tagline: "SaaS Boilerplate",
  
  // Logo
  logo: {
    icon: "FH",  // tekst w ikonie gdy brak grafiki
    gradient: "from-indigo-500 to-purple-600",
  },
  
  // URLs
  api: {
    baseUrl: import.meta.env.VITE_API_URL || "http://localhost:8000/api/v1",
  },
  
  // Auth
  auth: {
    accessTokenExpireMinutes: 30,
    rememberMeKey: "remember_me",
    tokenKey: "access_token",
    refreshTokenKey: "refresh_token",
  },

  // Design tokens
  theme: {
    primaryColor: "#4F46E5",       // indigo-600
    primaryHoverColor: "#4338CA",  // indigo-700
    fontFamily: "'Outfit', system-ui, sans-serif",
  },
} as const;
```

**ZASADA: Żaden komponent nie może mieć wpisanej nazwy produktu na sztywno. Zawsze import z APP_CONFIG.**

### KROK 2: Konwersja komponentów JSX → TSX

Skonwertuj wszystkie dostarczone komponenty z `fasthub-frontend-starter.zip` na TypeScript:
- Dodaj interfejsy propsów do każdego komponentu
- Zmień rozszerzenia .jsx → .tsx
- Zmień barrel export index.js → index.ts
- Zachowaj identyczne zachowanie wizualne i funkcjonalne

Przykład oczekiwanego wyniku dla Btn:

```typescript
interface BtnProps {
  children: React.ReactNode;
  onClick?: () => void;
  variant?: "primary" | "secondary" | "ghost" | "danger";
  className?: string;
  disabled?: boolean;
  type?: "button" | "submit" | "reset";
  loading?: boolean;
}

export default function Btn({ children, onClick, variant = "primary", className, disabled, type = "button", loading }: BtnProps) {
  // ... implementacja
}
```

Uwagi:
- Dodaj prop `type` do Btn (potrzebny w formularzach: type="submit")
- Dodaj prop `loading` do Btn (potrzebny przy operacjach async — wyświetlaj disabled + tekst "Loading..." lub spinner)
- Dodaj prop `type` do Fld (typ inputa: text/email/password)
- Fld już ma prop `type` w JSX — upewnij się że jest w interfejsie TS

### KROK 3: Zamiana Ant Design na Tailwind + nowe komponenty

**3a. Instalacja i konfiguracja Tailwind**

Zainstaluj Tailwind CSS z pluginem typography. Skonfiguruj `tailwind.config.js` z fontem Outfit. Dodaj import Google Fonts w `index.html`. Usuń import Ant Design z package.json i z całego kodu.

UWAGA: Obecny `package.json` ma Tailwind w devDependencies (v4) i Ant Design w dependencies (v6). Sprawdź czy Tailwind v4 jest skonfigurowany prawidłowo (v4 ma inną konfigurację niż v3 — sprawdź `postcss.config.js` i czy `@tailwindcss/postcss` jest użyty zamiast starego `tailwindcss`). Jeśli v4 sprawia problemy, rozważ downgrade do v3 (stabilniejszy, więcej dokumentacji).

**3b. Przepisanie layoutu — AppShell**

Zamień `components/layout/AppLayout.tsx` (Ant Design Sider + Header + Content) na nowy `AppShell.tsx` oparty na dostarczonym wzorcu, ale:
- Branding z APP_CONFIG (nie hardcodowane "WebCreator")
- Nawigacja: Dashboard, Team, Billing, Settings (te same co dziś)
- Warunkowo: Users, SuperAdmin (gdy user.is_superuser === true)
- User avatar/dropdown w headerze z logout
- Sidebar z active state (bg-indigo-50 dla aktywnego itemu)
- Responsive: sidebar chowany na mobile
- `<Outlet />` dla treści stron

**3c. Przepisanie stron auth**

Zamień `pages/auth/LoginPage.tsx`, `RegisterPage.tsx`, `ForgotPasswordPage.tsx`, `ResetPasswordPage.tsx`:
- Używaj Btn, Fld z nowej biblioteki UI
- Branding z APP_CONFIG
- Tło: gradient z design systemu
- Zachowaj logikę: walidację, obsługę błędów, loading, nawigację
- Zachowaj integrację z authStore (Zustand)

**3d. Przepisanie DashboardPage**

Zamień na nowy design z:
- Karty statystyk używające SectionCard
- StatusBadge dla stanów
- BEZ hardcodowanych mock danych na wykresach — zamiast tego pokaż prawdziwe wartości liczbowe (total users, organizations) z API, a wykresy schowaj za warunkiem `if (chartData.length > 0)` — na razie nie będzie danych historycznych do wyświetlenia, więc sekcja wykresów się nie pokaże. To jest świadoma decyzja — lepiej nic nie pokazać niż pokazać fałszywe dane.
- Warunek na onboarding: jeśli user nie ma organizacji, pokaż alert z przyciskiem "Create Organization"

**3e. Przepisanie TeamPage**

Zamień tabelę Ant Design na czystą tabelę HTML/Tailwind:
- Nagłówki: bg-gray-50, tekst text-xs uppercase text-gray-500
- Wiersze: hover:bg-gray-50, border-b
- StatusBadge dla ról (admin = indigo, viewer = green)
- Przycisk "Invite Member" → modal z Fld + Rad (wybór roli)
- Zachowaj logikę: fetch members, invite, remove, change role

**3f. Przepisanie SettingsPage**

Zamień na SidebarLayout z tabami:
- Tab Profile: Fld (full name, email disabled, position), Btn "Save Changes"
- Tab Organization: SectionCard z danymi firmy, Fld dla edycji, walidacja NIP/phone/postal
- Tab Security: zmiana hasła (Fld current + new + confirm), Btn "Change Password"
- Tab Danger Zone: SectionCard z czerwonym border, Btn danger "Delete Organization"

**3g. Przepisanie BillingPage**

Zamień na nowy design z:
- Karty planów używające Tile (zielony border = aktualny plan)
- StatusBadge dla statusu subskrypcji
- Informacja: "Stripe integration coming soon" jeśli billing nie jest podłączony (bo Stripe jest wykomentowany na backendzie)

**3h. Przepisanie OnboardingPage**

Zamień na centralną kartę (nie wizard — to jest prosty formularz jednego kroku):
- Fld "Organization Name"
- Btn "Complete Setup"
- Link "Skip for now"
- Branding z APP_CONFIG

**3i. Przepisanie stron SuperAdmin (OrganizationsPage, MetricsPage)**

Zamień na nowy design z czystymi tabelami Tailwind. Te strony są widoczne TYLKO gdy `user.is_superuser === true`.

**3j. Usunięcie Ant Design**

Po przepisaniu wszystkich stron:
- Usuń `antd` i `@ant-design/icons` z package.json
- Usuń wszystkie importy Ant Design z kodu
- Uruchom `npm install` i sprawdź czy build przechodzi

### KROK 4: Nowy API Client

Zamień `src/api/client.ts` — zachowaj obecną logikę (jest dobra), ale popraw:

1. **Czytaj baseURL z APP_CONFIG** zamiast bezpośrednio z env
2. **Sprawdzaj token w obu storage'ach** (localStorage + sessionStorage) — to jest w obecnym kodzie i działa dobrze, zachowaj
3. **Zachowaj interceptor token refresh** z queued requests — obecna implementacja jest poprawna i obsługuje edge case gdy wiele requestów jednocześnie dostaje 401
4. **Upewnij się że refreshToken trafia do tego samego storage** z którego był pobrany (localStorage jeśli remember_me, sessionStorage jeśli nie) — to jest w obecnym kodzie

### KROK 5: Fix App.tsx — token na starcie

W `App.tsx` zmień inicjalizację:

Obecny kod sprawdza TYLKO localStorage:
```
const token = localStorage.getItem('access_token');
```

Musi sprawdzać OBA storage:
```
const token = localStorage.getItem('access_token') || sessionStorage.getItem('access_token');
```

Dzięki temu użytkownicy bez "Remember me" nie wypadną po odświeżeniu przeglądarki.

### KROK 6: Error Boundary

Obecnie aplikacja nie ma React Error Boundary. Oznacza to że jeden błąd w dowolnym komponencie (np. crash na stronie Billing) zabija CAŁĄ aplikację — użytkownik widzi biały ekran i musi odświeżyć.

Utwórz `src/components/shared/ErrorBoundary.tsx`:
- Klasowy komponent React (Error Boundaries wymagają class component)
- Łapie błędy w drzewie komponentów-dzieci
- Wyświetla czytelny komunikat błędu z przyciskiem "Spróbuj ponownie" (reset state)
- Stylowany w Tailwind: biała karta, ikona ostrzeżenia, tekst "Coś poszło nie tak", przycisk Btn variant="primary"
- Opcjonalnie: logowanie błędu do konsoli (w przyszłości do Sentry)

Zastosowanie w routerze:
- Owrapuj `<Outlet />` w AppShell Error Boundary — dzięki temu crash strony nie zabija nawigacji
- Owrapuj cały `<RouterProvider />` w App.tsx w globalny Error Boundary — ostatnia linia obrony

### KROK 7: billingStore

Utwórz `src/store/billingStore.ts` — store Zustand dla danych billingowych:

```typescript
interface BillingState {
  subscription: Subscription | null;
  isLoading: boolean;
  error: string | null;
  
  fetchSubscription: () => Promise<void>;
  clearError: () => void;
}
```

Obecnie każde wejście na stronę Billing pobiera dane od nowa. Store cachuje dane subskrypcji żeby nie robić niepotrzebnych requestów. Wzór identyczny jak istniejący orgStore — fetch, cache, error handling.

BillingPage i DashboardPage (karta "Active Subscriptions") powinny czytać z tego store'a zamiast robić własne requesty.

---

## CZEGO NIE ROBIMY W TYM BRIEFIE

- NIE naprawiamy URL-i Members API (Brief 2)
- NIE naprawiamy brakujących pól w typach (Brief 2)
- NIE podłączamy prawdziwych danych do dashboardu (Brief 2)
- NIE naprawiamy magic link GET/POST (Brief 2)  
- NIE usuwamy martwego kodu z backendu (Brief 2)
- NIE budujemy stron kreatora (przyszłe briefy)
- NIE zmieniamy niczego w backendzie FastHub

---

## DESIGN TOKENS (referencja dla stylowania)

```
Font: 'Outfit', wagi 300-800
Primary: indigo-600 (#4F46E5), hover: indigo-700
Selected state: green-400 border + green-50 bg (Tile, Chk, Rad, Toggle)
Success: green-500/green-50, Warning: amber-500/amber-50, Danger: red-500/red-50
Background: gray-50, Surface: white, Border: gray-200
Text: gray-900, Secondary: gray-500, Muted: gray-400
Header: gray-950 (ciemny, prawie czarny)
Radius: rounded-xl (karty, inputy, przyciski), rounded-2xl (modale, hero)
Shadow: shadow-sm (karty), shadow-md (dropdown, modals)
```

---

## STRUKTURA PLIKÓW PO ZAKOŃCZENIU

```
fasthub-frontend/src/
├── config/
│   └── app.config.ts          ← NOWE: centralna konfiguracja
├── components/
│   ├── ui/                    ← NOWE: design system (z konwersji JSX→TSX)
│   │   ├── Btn.tsx
│   │   ├── Fld.tsx
│   │   ├── Tile.tsx
│   │   ├── Chk.tsx
│   │   ├── Rad.tsx
│   │   ├── Toggle.tsx
│   │   ├── SectionCard.tsx
│   │   ├── Lbl.tsx
│   │   ├── StatusBadge.tsx
│   │   └── index.ts
│   ├── layout/                ← PRZEPISANE: nowe layouty Tailwind
│   │   ├── AppShell.tsx
│   │   ├── SidebarLayout.tsx
│   │   └── WizardLayout.tsx
│   ├── shared/                ← NOWE: wspólne komponenty
│   │   ├── ErrorBoundary.tsx  ← NOWE: łapie crashe komponentów
│   │   ├── Modal.tsx
│   │   ├── DataTable.tsx      (opcjonalne — jeśli tabele są powtarzalne)
│   │   └── EmptyState.tsx
│   └── auth/
│       └── ProtectedRoute.tsx ← ZACHOWANE (ewentualnie przepisane bez Ant Spin)
├── pages/
│   ├── auth/
│   │   ├── LoginPage.tsx      ← PRZEPISANE
│   │   ├── RegisterPage.tsx   ← PRZEPISANE
│   │   ├── ForgotPasswordPage.tsx ← PRZEPISANE
│   │   └── ResetPasswordPage.tsx  ← PRZEPISANE
│   ├── DashboardPage.tsx      ← PRZEPISANE
│   ├── TeamPage.tsx           ← PRZEPISANE
│   ├── BillingPage.tsx        ← PRZEPISANE
│   ├── SettingsPage.tsx       ← PRZEPISANE (z SidebarLayout)
│   ├── OnboardingPage.tsx     ← PRZEPISANE
│   ├── UsersPage.tsx          ← PRZEPISANE
│   └── superadmin/
│       ├── OrganizationsPage.tsx ← PRZEPISANE
│       └── MetricsPage.tsx       ← PRZEPISANE
├── api/                       ← ZACHOWANE (poprawki w client.ts)
│   ├── client.ts              ← POPRAWIONE
│   ├── auth.ts                ← ZACHOWANE
│   ├── members.ts             ← ZACHOWANE (poprawki URL w Brief 2)
│   ├── organizations.ts       ← ZACHOWANE
│   ├── billing.ts             ← ZACHOWANE
│   ├── superadmin.ts          ← ZACHOWANE
│   └── users.ts               ← ZACHOWANE
├── store/
│   ├── authStore.ts           ← ZACHOWANE
│   ├── orgStore.ts            ← ZACHOWANE
│   └── billingStore.ts        ← NOWE: cache danych subskrypcji
├── types/
│   └── models.ts              ← ZACHOWANE (poprawki typów w Brief 2)
├── hooks/                     ← NOWE (opcjonalne)
│   └── useAuth.ts             (opcjonalne — jeśli uprości kod)
├── router.tsx                 ← PRZEPISANE (te same ścieżki, nowe importy)
├── App.tsx                    ← POPRAWIONE (sprawdzanie obu storage'ów)
├── main.tsx                   ← ZACHOWANE
└── index.css                  ← PRZEPISANE (Tailwind directives + Outfit)
```

---

## CHECKLIST WERYFIKACYJNA

Po zakończeniu pracy, upewnij się że:

### Build i konfiguracja
- [ ] `npm run build` przechodzi bez błędów
- [ ] `npm run dev` uruchamia serwer deweloperski
- [ ] Brak importów Ant Design w całym kodzie (grep -r "antd" src/ zwraca 0 wyników)
- [ ] Brak importów @ant-design/icons w całym kodzie
- [ ] antd i @ant-design/icons usunięte z package.json
- [ ] Tailwind CSS działa (klasy utility renderują się poprawnie)
- [ ] Font Outfit ładuje się i jest widoczny

### Konfiguracja centralna
- [ ] `src/config/app.config.ts` istnieje i eksportuje APP_CONFIG
- [ ] Grep -r "AutoFlow" src/ zwraca 0 wyników (brak hardcoded branding)
- [ ] Grep -r "WebCreator" src/ zwraca 0 wyników
- [ ] Nazwa produktu we wszystkich komponentach pochodzi z APP_CONFIG
- [ ] Zmiana APP_CONFIG.name na "TestApp" powoduje zmianę nazwy wszędzie w UI

### Komponenty UI (TypeScript)
- [ ] Wszystkie 9 komponentów ui/ są w .tsx z interfejsami propsów
- [ ] Barrel export w index.ts działa (import { Btn, Fld } from '@/components/ui')
- [ ] Btn obsługuje variant, disabled, loading, type="submit"
- [ ] Fld obsługuje label, error, disabled, type (text/email/password), large (textarea)
- [ ] Tile/Chk/Rad/Toggle mają zieloną selekcję (green-400/green-50)
- [ ] StatusBadge renderuje warianty: success, warning, error, info, neutral

### Layouty
- [ ] AppShell: ciemny header (gray-950), sidebar z nawigacją, Outlet
- [ ] AppShell: branding z APP_CONFIG (nazwa + ikona)
- [ ] AppShell: user dropdown z logout w headerze
- [ ] AppShell: warunkowo Users/SuperAdmin menu gdy user.is_superuser
- [ ] SidebarLayout: sidebar z tabami, aktywny tab podświetlony (indigo-50)
- [ ] WizardLayout: header + pasek kroków (konwertowany do TSX, gotowy na przyszłość)
- [ ] ProtectedRoute: działa bez Ant Design Spin (użyj Tailwind spinner)

### Strony auth
- [ ] Login: email + hasło + remember me + forgot password + link do register
- [ ] Login: po zalogowaniu redirect do /dashboard
- [ ] Register: full name + email + hasło + link do login
- [ ] Register: po rejestracji redirect do /onboarding
- [ ] ForgotPassword: email + submit → komunikat sukcesu
- [ ] ResetPassword: nowe hasło + potwierdzenie → submit

### Strony główne
- [ ] Dashboard: karty statystyk (bez fałszywych danych na wykresach)
- [ ] Dashboard: alert "Create Organization" gdy user bez organizacji
- [ ] Team: tabela członków, przycisk Invite, dropdown akcji (change role, remove)
- [ ] Settings: taby Profile/Organization/Security/Danger Zone
- [ ] Settings → Profile: formularz z Fld, Btn Save
- [ ] Settings → Organization: formularz z walidacją NIP/phone/postal
- [ ] Settings → Security: zmiana hasła
- [ ] Settings → Danger Zone: usunięcie organizacji z potwierdzeniem
- [ ] Billing: karty planów, informacja o statusie
- [ ] Onboarding: formularz tworzenia organizacji
- [ ] Users (superadmin): tabela użytkowników z paginacją

### API i autentykacja
- [ ] API client czyta baseURL z APP_CONFIG
- [ ] Token refresh interceptor działa (zachowany z obecnego kodu)
- [ ] App.tsx sprawdza token w localStorage ORAZ sessionStorage na starcie
- [ ] Logout czyści oba storage'e
- [ ] authStore (Zustand) nie został zmieniony funkcjonalnie

### Jakość
- [ ] Zero ostrzeżeń TypeScript (no any types w nowych komponentach)
- [ ] Konsola przeglądarki czysta na starcie (brak console.error)
- [ ] Responsywność: strony wyglądają poprawnie na >= 768px

### Error Boundary
- [ ] ErrorBoundary.tsx istnieje w components/shared/
- [ ] ErrorBoundary wyświetla czytelny komunikat i przycisk "Spróbuj ponownie"
- [ ] AppShell owrapowany Error Boundary wokół Outlet (crash strony nie zabija menu)
- [ ] App.tsx owrapowany globalnym Error Boundary (ostatnia linia obrony)
- [ ] Test: celowo wrzuć throw Error w DashboardPage → powinien wyświetlić się komunikat, nie biały ekran

### billingStore
- [ ] billingStore.ts istnieje w store/
- [ ] Eksportuje fetchSubscription, subscription, isLoading, error
- [ ] BillingPage czyta z billingStore (nie fetchuje samodzielnie)
- [ ] Dashboard karta "Active Subscriptions" czyta z billingStore

---

## WAŻNE UWAGI

1. **NIE zmieniaj backendu** — żadnych zmian w fasthub-backend/ ani fasthub_core/
2. **NIE zmieniaj istniejących store'ów** (authStore, orgStore) — zachowaj obecną logikę, zmień tylko UI. Dodaj NOWY billingStore.
3. **NIE zmieniaj plików API** (auth.ts, members.ts itd.) — poprawki URL będą w Brief 2
4. **NIE zmieniaj types/models.ts** — poprawki typów będą w Brief 2
5. **NIE usuwaj Recharts** z dependencies — może być potrzebny w przyszłości, ale nie używaj go na Dashboard jeśli nie ma prawdziwych danych
6. **Zachowaj react-hook-form i zod** w dependencies — mogą być użyte w przyszłych formularzach
7. **Commit message**: "feat: modernize frontend - Tailwind + design system + app config"
