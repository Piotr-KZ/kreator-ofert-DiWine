# BRIEF 2: FastHub Frontend — Naprawa Integracji z Backendem

## Dla: Opus CLI (kodowanie)
## Od: Strategia (planowanie i weryfikacja)
## Data: 2026-03-08
## Wymaganie: Brief 1 musi być zakończony i zweryfikowany przed rozpoczęciem

---

## KONTEKST

Brief 1 wymienił silnik frontendowy FastHub — Ant Design zastąpiony Tailwindem, branding scentralizowany, komponenty UI skonwertowane na TypeScript.

Ten brief naprawia **wszystkie znane problemy integracji między frontendem a backendem**. To są realne bugi — frontend wysyła requesty pod złe adresy, oczekuje pól których backend nie zwraca, używa warunków które nigdy nie są spełnione. Po tym briefie FastHub powinien działać end-to-end: rejestracja → logowanie → dashboard → team → settings → billing → superadmin.

---

## CEL

Naprawić wszystkie zidentyfikowane rozbieżności frontend↔backend, tak aby:
- Każdy request frontendowy trafiał na istniejący endpoint backendowy
- Typy TypeScript odzwierciedlały to co backend faktycznie zwraca
- Strony wyświetlały prawdziwe dane z API (nie mock/hardcoded)
- Panel SuperAdmin był dostępny dla użytkowników z flagą is_superuser
- Nie było błędów w konsoli przeglądarki przy normalnym użytkowaniu

---

## LISTA NAPRAW

### NAPRAWA 1: Members API — złe URL-e

**Problem:** Frontend wysyła requesty pod ścieżki które nie istnieją na backendzie.

**Plik do zmiany:** `src/api/members.ts`

**Obecne (złe) URL-e frontendu:**
```
POST   /members/organizations/{id}/members/invite    — zapraszanie
GET    /members/organizations/{id}/members            — lista
DELETE /members/organizations/{id}/members/{userId}   — usuwanie
PATCH  /members/organizations/{id}/members/{userId}/role — zmiana roli
```

**Prawdziwe endpointy backendu (z pliku fasthub-backend/app/api/v1/endpoints/members.py + api.py):**

Router members jest zarejestrowany z `prefix=""` w api.py:
```
api_router.include_router(members.router, prefix="", tags=["Members"])
```

A w members.py endpointy mają pełne ścieżki:
```
POST   /organizations/{organization_id}/members       — zapraszanie (MemberCreate: email + role)
GET    /organizations/{organization_id}/members       — lista (query params: page, per_page, search, role)
DELETE /members/{member_id}                            — usuwanie (po member_id, NIE user_id)
PATCH  /members/{member_id}                            — zmiana roli (po member_id, NIE user_id)
```

**Co zmienić w members.ts:**
- `invite`: URL na `/organizations/${organizationId}/members`, body: `{ email, role }`
- `list`: URL na `/organizations/${organizationId}/members`
- `remove`: URL na `/members/${memberId}` — UWAGA: to jest member_id (UUID wpisu w tabeli members), NIE user_id
- `changeRole`: URL na `/members/${memberId}` — j.w., member_id nie user_id

**Konsekwencja:** TeamPage.tsx musi też zostać zaktualizowana — przy usuwaniu i zmianie roli trzeba przekazywać `member.id` (ID wpisu member), nie `member.user_id`. Sprawdź jak TeamPage wywołuje te funkcje i popraw.

**Plik do zmiany:** `src/api/members.ts` + `src/pages/TeamPage.tsx`

---

### NAPRAWA 2: Typ User — brakujące/nadmiarowe pola

**Problem:** Frontend TypeScript type `User` nie zgadza się z tym co backend zwraca w `UserResponse`.

**Plik do zmiany:** `src/types/models.ts`

**Co backend FAKTYCZNIE zwraca (z app/schemas/user.py → UserResponse):**
```
id: UUID
email: string
full_name: string | null
is_active: boolean
is_verified: boolean
is_superuser: boolean
created_at: datetime
```

**Co frontend OCZEKUJE (z types/models.ts → User):**
```
id: string
email: string
full_name: string
is_active: boolean
is_verified: boolean
is_superuser: boolean
position?: string          ← NIE ISTNIEJE w backend response
last_login_at?: string     ← NIE ISTNIEJE w backend response
created_at: string
updated_at: string         ← NIE ISTNIEJE w backend response
```

**Co zmienić:**
- Usuń `position` z typu User (backend go nie zwraca; jeśli chcemy go w przyszłości, trzeba najpierw dodać do backendu — to nie jest w zakresie tego briefu)
- Usuń `last_login_at` z typu User (j.w.)
- Usuń `updated_at` z typu User (backend UserResponse go nie zwraca)
- Upewnij się że `full_name` jest `string | null` (backend może zwrócić null)

**UWAGA:** Typ `TeamMember` i `MemberWithUser` też mogą mieć te pola. Sprawdź i popraw wszędzie.

---

### NAPRAWA 3: Typ Organization — brakujące/nadmiarowe pola

**Problem:** Frontend typ `Organization` ma pola których nie ma w backendzie i brakuje pól które backend zwraca.

**Plik do zmiany:** `src/types/models.ts`

**Co backend FAKTYCZNIE zwraca (z app/schemas/organization.py → OrganizationResponse i OrganizationWithStats):**

OrganizationResponse:
```
id: UUID
name: string
slug: string | null
owner_id: UUID
stripe_customer_id: string | null
type: string | null
email: string | null
nip: string | null
phone: string | null
billing_street: string | null
billing_city: string | null
billing_postal_code: string | null
billing_country: string | null
is_complete: boolean
created_at: datetime
updated_at: datetime
```

OrganizationWithStats (endpoint /organizations/me):
```
...wszystko z OrganizationResponse plus:
user_count: integer (default 0)
subscription_status: string | null
```

**Co frontend MA (z types/models.ts → Organization):**
```
regon?: string        ← NIE ISTNIEJE w backend
krs?: string          ← NIE ISTNIEJE w backend
first_name?: string   ← NIE ISTNIEJE w backend
last_name?: string    ← NIE ISTNIEJE w backend
logo_url?: string     ← NIE ISTNIEJE w backend
```

**Brakuje w frontend:**
```
owner_id: string
is_complete: boolean
stripe_customer_id?: string
slug: string
```

**Co zmienić:**
- Usuń pola: regon, krs, first_name, last_name, logo_url
- Dodaj pola: owner_id, is_complete, slug
- Dodaj typ `OrganizationWithStats` który rozszerza Organization o: user_count (number), subscription_status (string | null)
- Upewnij się że DashboardPage używa `user_count` (nie `member_count` który nie istnieje)

---

### NAPRAWA 4: Warunek SuperAdmin — user.role nie istnieje

**Problem:** DashboardPage i AppLayout sprawdzają `user?.role === 'superadmin'` ale typ User nie ma pola `role`. Backend nie zwraca takiego pola. Warunek NIGDY nie jest true — panel SuperAdmin jest niewidoczny nawet dla superadminów.

**Pliki do zmiany:** `src/pages/DashboardPage.tsx` + layout (AppShell po Brief 1)

**Co zmienić:**
- Zamień wszystkie `user?.role === 'superadmin'` na `user?.is_superuser === true`
- Sprawdź w AppShell (po Brief 1) — jeśli tam też jest warunek na role, popraw
- Sprawdź router.tsx — `requireSuperuser` prop w ProtectedRoute już sprawdza `user.is_superuser`, więc routing jest OK

---

### NAPRAWA 5: Profile Update — martwy przycisk

**Problem:** SettingsPage → Profile → "Save Changes" wyświetla `message.info('Profile update feature coming soon')`. Ale backend endpoint `PATCH /users/me` istnieje i działa (plik: fasthub-backend/app/api/v1/endpoints/users.py linia 53-73).

**Plik do zmiany:** `src/pages/SettingsPage.tsx` (po przepisaniu w Brief 1)

**Co zmienić:**
- Podłącz formularz profilu do `usersApi.update('me', { full_name: values.full_name })`
- Albo stwórz dedykowaną funkcję w `src/api/users.ts`: `updateMe: (data) => apiClient.patch('/users/me', data)`
- Po sukcesie: odśwież dane użytkownika przez `fetchCurrentUser()` z authStore
- Obsłuż błędy: wyświetl komunikat z API

**UWAGA:** Backend UserUpdate przyjmuje: full_name, email (opcjonalne), is_active (opcjonalne). Zwykły user może zmienić full_name. Email jest disabled w formularzu (słusznie — zmiana email wymagałaby weryfikacji). is_active to pole adminowe — nie wystawiaj go w formularzu profilu.

---

### NAPRAWA 6: Magic Link — GET vs POST

**Problem:** Frontend wysyła `GET /auth/magic-link/verify?token=...` ale backend oczekuje `POST /auth/magic-link/verify` z tokenem w body.

**Plik do zmiany:** `src/api/auth.ts`

**Co zmienić:**
- Zamień: `verifyMagicLink: (token: string) => apiClient.get('/auth/magic-link/verify?token=${token}')`
- Na: `verifyMagicLink: (token: string) => apiClient.post('/auth/magic-link/verify', { token })`

**UWAGA:** Sprawdź backend dokładnie — endpoint w auth.py linia 269-279 to:
```python
@router.post("/magic-link/verify", response_model=TokenResponse)
async def verify_magic_link(token: str, db: AsyncSession = Depends(get_db)):
```
Token jest przekazywany jako query parameter (FastAPI automatycznie bierze `token: str` z query jeśli nie ma Body). Więc technicznie może działać zarówno jako query param w POST jak i w body. Najbezpieczniej: `apiClient.post('/auth/magic-link/verify?token=${token}')`. Ale sprawdź na żywo i wybierz wariant który działa.

---

### NAPRAWA 7: Dashboard — prawdziwe dane zamiast mocków

**Problem:** Po Brief 1 dashboard nie powinien mieć hardcodowanych wykresów. Ale statystyki (karty licznikowe) powinny pokazywać prawdziwe dane.

**Plik do zmiany:** `src/pages/DashboardPage.tsx`

**Dla zwykłego usera (nie superadmin):**

Dashboard wywołuje `organizationsApi.getCurrent()` który trafia na `GET /organizations/me` → zwraca `OrganizationWithStats`.

Popraw mapowanie:
- "Total Users" → `data.user_count` (NIE `data.member_count` — to pole nie istnieje)
- "Organizations" → `1` (user widzi swoją organizację)
- "Active Subscriptions" → sprawdź `data.subscription_status === 'active'` → 1 lub 0
- "Revenue" → nie pokazuj tej karty dla zwykłego usera (nie ma dostępu do danych revenue)

Usuń hardcodowane procenty "+12% from last month", "+5% from last month" itd. Jeśli nie mamy danych porównawczych, nie pokazuj procentów. Lepiej nic niż kłamstwo.

**Dla superadmina:**

Dashboard wywołuje `superadminApi.getMetrics()` → `GET /admin/stats`. Sprawdź co backend zwraca (plik: fasthub-backend/app/schemas/admin.py → SystemStatsResponse) i dopasuj frontend.

---

### NAPRAWA 8: Backend — usunięcie martwego endpointu invite

**Problem:** W pliku `fasthub-backend/app/api/v1/endpoints/organizations.py` linia 221-323 jest endpoint `POST /organizations/invite` który używa `current_user.organization` i `existing_user.organization_id`. Te pola NIE ISTNIEJĄ w modelu User po migracji na multi-org (tabela Members). Ten endpoint rzuci `AttributeError` przy każdym wywołaniu.

**Plik do zmiany:** `fasthub-backend/app/api/v1/endpoints/organizations.py`

**Co zmienić:**
- Usuń cały blok od `class InviteMemberRequest` (linia 221) do końca pliku (linia 323)
- Ten endpoint jest duplikatem — prawidłowy invite jest w `members.py` (`POST /organizations/{id}/members`)
- Frontend po Naprawie 1 będzie już korzystał z prawidłowego endpointu

**WYJĄTEK: To jest jedyna zmiana backendowa w tym briefie.** Robimy ją bo ten martwy kod może powodować import errors i jest aktywnie niebezpieczny (zwraca 500 na produkcji).

---

### NAPRAWA 9: Backend admin — logo_url nie istnieje

**Problem:** W pliku `fasthub-backend/app/api/v1/endpoints/admin.py` linia 162 jest `"logo_url": org.logo_url` — ale model Organization nie ma pola `logo_url`. Rzuci `AttributeError`.

**Plik do zmiany:** `fasthub-backend/app/api/v1/endpoints/admin.py`

**Co zmienić:**
- Usuń linię `"logo_url": org.logo_url,` z dict comprehension w list_organizations endpoint
- Albo zamień na `"logo_url": None,` jeśli frontend oczekuje tego pola (po Naprawie 3 nie powinien)

**WYJĄTEK nr 2: Druga zmiana backendowa — naprawienie crash-a.**

---

### NAPRAWA 10: Member ID typ — int vs UUID

**Problem:** Backend endpointy `DELETE /members/{member_id}` i `PATCH /members/{member_id}` deklarują `member_id: int` ale model Member ma UUID jako primary key (dziedziczy z BaseModel). FastAPI nie skonwertuje UUID na int — request z UUID zwróci 422 Unprocessable Entity.

**Plik do zmiany:** `fasthub-backend/app/api/v1/endpoints/members.py`

**Co zmienić:**
- `async def remove_member(member_id: int, ...)` → `async def remove_member(member_id: UUID, ...)`
- `async def update_member_role(member_id: int, ...)` → `async def update_member_role(member_id: UUID, ...)`
- Dodaj import `from uuid import UUID` na górze pliku (jeśli jeszcze nie ma)

**WYJĄTEK nr 3: Trzecia zmiana backendowa — bez niej members management nie działa.**

---

### NAPRAWA 11: Register schema — frontend type vs backend

**Problem:** Frontend `src/api/auth.ts` definiuje `RegisterRequest` z zagnieżdżonym obiektem `organization` (name, type, nip, street, city itd.). Backend `UserRegister` schema przyjmuje płasko: email, password, full_name, organization_name.

**Plik do zmiany:** `src/api/auth.ts`

**Co zmienić:**
- Popraw interfejs `RegisterRequest` żeby odpowiadał temu co backend faktycznie przyjmuje:
```typescript
export interface RegisterRequest {
  email: string;
  password: string;
  full_name?: string;
  organization_name?: string;
}
```
- Sprawdź czy RegisterPage wysyła dane w tym formacie (po Brief 1 powinien)

---

### NAPRAWA 12: Token storage przy rejestracji — niespójność z loginem

**Problem:** AuthStore → `register()` ZAWSZE zapisuje tokeny do localStorage. Natomiast `login()` respektuje wybór "Remember Me" — jeśli user nie zaznaczył "Remember Me", token idzie do sessionStorage. Po rejestracji użytkownik jest traktowany jakby zawsze zaznaczył "Remember Me", nawet jeśli tego nie chce.

**Plik do zmiany:** `src/store/authStore.ts`

**Co zmienić:**
- W funkcji `register` zmień zapis tokenów z bezwarunkowego `localStorage.setItem` na logikę identyczną jak w `login` — domyślnie `localStorage` (bo przy rejestracji nie ma checkboxa "Remember Me", więc domyślne zachowanie to zapamiętanie — user dopiero się zarejestrował, chce zostać zalogowany)
- Alternatywnie: dodaj parametr `rememberMe` do `register()` z domyślną wartością `true`
- Kluczowe: zachowaj spójność — jeśli login używa sessionStorage gdy rememberMe=false, to register powinien mieć tę samą logikę

To nie jest krytyczny bug (default localStorage = zapamiętaj sesję = dobre UX przy rejestracji), ale niespójność w kodzie powinna być świadoma i udokumentowana, nie przypadkowa.

---

### NAPRAWA 13: Konsolidacja typów — inline types do models.ts

**Problem:** Część typów jest zdefiniowana centralnie w `src/types/models.ts`, ale część jest zdefiniowana inline w plikach API (`src/api/auth.ts` → RegisterRequest, LoginRequest, LoginResponse; `src/api/members.ts` → InviteMemberRequest, ChangeMemberRoleRequest, MemberListResponse; `src/api/users.ts` → UsersListResponse).

To powoduje że typy są rozproszone — programista nie wie gdzie szukać definicji. Typy response'ów API powinny być w jednym miejscu.

**Pliki do zmiany:** `src/types/models.ts` + wszystkie pliki w `src/api/`

**Co zmienić:**
- Przenieś WSZYSTKIE interfejsy request/response z plików api/*.ts do `src/types/models.ts` (albo stwórz osobny `src/types/api.ts` jeśli models.ts staje się za duży)
- W plikach api/*.ts importuj typy z types/ zamiast definiować lokalnie
- Utrzymaj jeden plik jako "source of truth" dla wszystkich typów danych

Struktura po zmianie:
```
src/types/
├── models.ts     ← modele danych (User, Organization, Member, Subscription, Invoice...)
└── api.ts        ← NOWE: request/response types (LoginRequest, LoginResponse, RegisterRequest, MemberListResponse...)
```

---

### NAPRAWA 14: Backend — usunięcie pustego katalogu use_cases/

**Problem:** `fasthub-backend/app/use_cases/` zawiera tylko pusty `__init__.py`. Żaden kod go nie używa, żaden import do niego nie prowadzi. To martwy placeholder który wprowadza w błąd (sugeruje że jest wzorzec use cases, którego nie ma).

**Plik do zmiany:** `fasthub-backend/app/use_cases/`

**Co zmienić:**
- Usuń cały katalog `use_cases/` z `fasthub-backend/app/`
- Sprawdź czy żaden plik nie importuje z `app.use_cases` (grep -r "use_cases" fasthub-backend/)

**WYJĄTEK nr 4: Czwarta zmiana backendowa — czyszczenie martwego kodu.**

---

## CZEGO NIE ROBIMY W TYM BRIEFIE

- NIE budujemy nowych endpointów backendowych (poza 4 naprawami: martwy invite, logo_url, UUID typy, pusty use_cases)
- NIE budujemy stron kreatora
- NIE dodajemy nowych funkcji
- NIE zmieniamy design systemu (to zostało ustalone w Brief 1)
- NIE ruszamy fasthub_core/

---

## CHECKLIST WERYFIKACYJNA

### Members API
- [ ] Frontend wysyła POST na `/organizations/{id}/members` (invite)
- [ ] Frontend wysyła GET na `/organizations/{id}/members` (lista)
- [ ] Frontend wysyła DELETE na `/members/{memberId}` z UUID membera (nie usera)
- [ ] Frontend wysyła PATCH na `/members/{memberId}` z UUID membera (nie usera)
- [ ] TeamPage prawidłowo przekazuje member.id (nie member.user_id) do remove i changeRole
- [ ] Backend members.py: remove_member i update_member_role przyjmują UUID nie int
- [ ] Zaproszenie nowego członka działa end-to-end (wpisz email → submit → pojawia się w tabeli)
- [ ] Usunięcie członka działa end-to-end
- [ ] Zmiana roli działa end-to-end

### Typy TypeScript
- [ ] User type nie ma: position, last_login_at, updated_at
- [ ] User type ma full_name jako string | null
- [ ] Organization type nie ma: regon, krs, first_name, last_name, logo_url
- [ ] Organization type ma: owner_id, is_complete, slug
- [ ] OrganizationWithStats type istnieje z: user_count, subscription_status
- [ ] Brak błędów TypeScript po zmianach typów (npm run build czyste)

### SuperAdmin
- [ ] Warunek superadmin: `user.is_superuser === true` (nie user.role)
- [ ] Menu SuperAdmin widoczne w AppShell gdy user jest superuserem
- [ ] Dashboard SuperAdmin pobiera dane z /admin/stats
- [ ] Strona Organizations (superadmin) pobiera dane z /admin/organizations
- [ ] Strona Users (superadmin) pobiera dane z /users/

### Profile Update
- [ ] Settings → Profile → Save Changes wywołuje PATCH /users/me
- [ ] Po zapisie dane użytkownika się odświeżają (fetchCurrentUser)
- [ ] Błąd API wyświetla komunikat dla użytkownika

### Magic Link
- [ ] verifyMagicLink wysyła POST (nie GET) na /auth/magic-link/verify

### Dashboard dane
- [ ] Zwykły user: statystyki z organizationsApi.getCurrent() → user_count (nie member_count)
- [ ] Brak hardcodowanych procentów (+12%, +5% itd.)
- [ ] Brak fałszywych danych na wykresach
- [ ] SuperAdmin: statystyki z /admin/stats

### Register
- [ ] RegisterRequest type zgadza się z backend UserRegister schema
- [ ] Rejestracja działa end-to-end: wypełnij formularz → submit → redirect do onboarding

### Token storage (rejestracja)
- [ ] authStore.register() ma świadomą decyzję o storage (domyślnie localStorage z komentarzem dlaczego)
- [ ] Zachowanie jest spójne z login() — ten sam wzorzec, te same klucze

### Konsolidacja typów
- [ ] Wszystkie request/response interfejsy z api/*.ts przeniesione do types/
- [ ] Plik src/types/api.ts istnieje (lub typy dodane do models.ts)
- [ ] Pliki api/*.ts importują typy z types/ (żadnych lokalnych definicji interfejsów)
- [ ] grep -r "export interface" src/api/ zwraca 0 wyników

### Backend naprawy
- [ ] Usunięty martwy endpoint POST /organizations/invite z organizations.py
- [ ] Usunięte/naprawione org.logo_url w admin.py list_organizations
- [ ] members.py: member_id typowane jako UUID (nie int)
- [ ] Usunięty pusty katalog fasthub-backend/app/use_cases/
- [ ] grep -r "use_cases" fasthub-backend/ zwraca 0 wyników

### Ogólna weryfikacja end-to-end
- [ ] Flow: Register → Onboarding (create org) → Dashboard → Team (see yourself) → Settings (edit profile) → Logout
- [ ] Flow: Login → Dashboard → Team → Invite member → See new member → Change role → Remove member
- [ ] Flow: Login as superadmin → Dashboard (admin stats) → Users list → Organizations list
- [ ] Konsola przeglądarki: ZERO błędów przy normalnym użytkowaniu (żadnych 404, 422, 500)
- [ ] Network tab: żadnych failed requests przy normalnym użytkowaniu
- [ ] `npm run build` — zero błędów TypeScript
- [ ] Backend: `pytest` — istniejące testy nadal przechodzą (nie zepsuliśmy nic usuwając martwy kod)

---

## KOLEJNOŚĆ WYKONYWANIA

Rekomendowana kolejność (od najważniejszego):

1. **Naprawy backendowe (8, 9, 10, 14)** — bo bez nich frontend nie ma do czego strzelać
2. **Naprawa Members API (1)** — najczęściej używana funkcja
3. **Naprawa typów (2, 3) + konsolidacja typów (13)** — TypeScript zacznie krzyczeć o błędach, co pomoże znaleźć resztę
4. **Naprawa SuperAdmin (4)** — odblokuje panel admina
5. **Naprawa Profile (5)** — podłączenie martwego przycisku
6. **Naprawa Dashboard (7)** — prawdziwe dane
7. **Naprawa Magic Link (6)** — edge case, mniej krytyczny
8. **Naprawa Register (11) + token storage (12)** — typy i spójność

---

## WAŻNE UWAGI

1. **Ten brief ma 4 zmiany backendowe** — usunięcie martwego endpointu, naprawa logo_url, poprawka typów UUID, usunięcie pustego use_cases/. Reszta to wyłącznie frontend.
2. **Po tym briefie FastHub powinien być w stanie "production-ready" dla flow podstawowego** — rejestracja, logowanie, zarządzanie zespołem, ustawienia, panel admina.
3. **Testuj na żywym backendzie** — uruchom `docker-compose up` i sprawdź flow end-to-end. Samo przejście builda TypeScript nie wystarczy — trzeba kliknąć.
4. **Commit message**: "fix: repair all frontend-backend integration issues"
