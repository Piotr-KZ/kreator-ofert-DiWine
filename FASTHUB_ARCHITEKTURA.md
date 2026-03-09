# FastHub — Architektura Systemu

> Dokument biznesowy dla wlasciciela i partnerow.
> Wersja: 4.0 | Data: 2026-03-09
> Stan: Po briefach 1-28 (extended models, GUS, 2FA, dunning, frontend konto)

---

## Co to jest FastHub

FastHub to **platforma-fundament**, na ktorej buduje sie aplikacje biznesowe typu SaaS (oprogramowanie jako usluga). Zamiast budowac kazda nowa aplikacje od zera, masz gotowe "podwozie" — logowanie (2FA, sesje), organizacje, uprawnienia, powiadomienia, platnosci (5 bramek w tym polskie), windykacja (dunning), bezpieczenstwo, RODO, szablony emaili, faktury, GUS API, webhooks. Nowa aplikacja doklada tylko swoja unikalna logike biznesowa.

**Pierwsza aplikacja budowana na FastHub:** Kreator Stron WWW (WebCreator).

---

## Z czego sklada sie system

```
┌─────────────────────────────────────────────────┐
│                  UZYTKOWNIK                      │
│            (przegladarka / telefon)              │
└────────────────────┬────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────┐
│              FRONTEND (interfejs)                │
│     React + TypeScript + Tailwind CSS            │
│     Wlasne komponenty UI (Btn, Fld, Tile...)    │
│     Font: Outfit. Design system: indigo + green. │
│     Konfiguracja brandingu w jednym pliku.       │
└────────────────────┬────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────┐
│              BACKEND (serwer API)                │
│     FastAPI + fasthub_core (uniwersalny pakiet)  │
│     27+ modulow: auth (2FA, sesje), billing,     │
│     RBAC, GDPR, platnosci, dunning, webhooks,   │
│     GUS API, powiadomienia, email, social login. │
└────────────────────┬────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────┐
│         BAZA DANYCH + CACHE (pamiec)             │
│     PostgreSQL: trwale dane                      │
│     Redis: sesje, cache, task queue, eventy      │
└─────────────────────────────────────────────────┘
```

---

## Moduly systemu — co kazdy robi

### 1. Logowanie i bezpieczenstwo

Uzytkownik moze sie zalogowac na 4 sposoby: email + haslo, magiczny link (bez hasla), przez Google, przez GitHub lub Microsoft. System pamięta sesje, chroni konto, szyfruje hasla.

**2FA (Brief 26):** Opcjonalna weryfikacja dwuetapowa TOTP (Google Authenticator, Authy). Konfiguracja: QR code + klucz reczny. Kody zapasowe na wypadek utraty telefonu. Przy logowaniu z 2FA: tymczasowy token (5 min) → weryfikacja kodem → pelny dostep.

**Zarzadzanie sesjami (Brief 26):** Uzytkownik widzi wszystkie aktywne sesje (urzadzenie, IP, ostatnia aktywnosc). Moze wylogowac konkretna sesje lub wszystkie jednoczesnie.

Zabezpieczenia: haslo min 8 znakow z wielka litera i cyfra, blokada po 5 nieudanych probach, rate limiting na rejestracje i reset hasla. Tokeny JWT (30 min) z automatycznym odswiezaniem. Wylogowanie natychmiast uniewaznija token.

### 2. Social Login (Google, GitHub, Microsoft)

Uzytkownik klika "Zaloguj przez Google" — system przekierowuje do Google, uzytkownik sie loguje, wraca z tokenem. Jesli email juz istnieje w bazie — konto jest automatycznie polaczone. Jesli nie — tworzone jest nowe konto bez hasla.

### 3. Organizacje i zespoly

Firma zaklada organizacje, zaprasza pracownikow mailem, kazdy ma role. Mozna miec wiele organizacji na jednym koncie. System zaproszen: wpisz email → wyslij zaproszenie → osoba klika link → dolacza do firmy z przypisana rola.

**Rejestracja rozszerzona (Brief 25):** Przy rejestracji firmy mozna podac NIP — system automatycznie pobiera dane z GUS/REGON (nazwa, adres, REGON, forma prawna). Pola organizacji: forma prawna, REGON, KRS, strona WWW, logo, inspektor RODO.

4 poziomy ról: Wlasciciel (pelna kontrola), Admin (zarzadzanie), Edytor (tworzenie/edycja), Podglad (tylko czytanie). Mozna tworzyc wlasne role z dowolna kombinacja uprawnien.

### 4. Uprawnienia (RBAC)

12 podstawowych uprawnien w 4 kategoriach: zespol, faktury, ustawienia, dziennik zmian. Kazda organizacja moze tworzyc wlasne role — np. "Ksiegowy" z dostepem tylko do faktur. Super Admin widzi i moze wszystko we wszystkich organizacjach.

### 5. Platnosci — 5 bramek jednoczesnie

System obsluguje platnosci przez WIELE bramek jednoczesnie. Klient widzi wszystkie dostepne metody platnosci:

| Bramka | Metody platnosci | Status |
|--------|-----------------|--------|
| Stripe | Karta, BLIK, Google Pay, Apple Pay | Gotowe |
| PayU | BLIK, karta, przelew, Google Pay, Apple Pay | Gotowe |
| Tpay | BLIK, karta, przelew, Google Pay, Apple Pay | Gotowe |
| Przelewy24 | BLIK, karta, przelew, Google Pay, Apple Pay | Gotowe |
| PayPal | PayPal | Gotowe |

Wlasciciel aplikacji wlacza bramki podajac klucze API. System automatycznie pomija nieskonfigurowane. Metody platnosci sa deduplikowane — jesli PayU i Tpay obsluguja BLIK, pokazuje sie raz.

**Subskrypcje:** Stripe i PayPal maja wbudowane subskrypcje. Polskie bramki (PayU, Tpay, P24) nie maja — system sam zarzadza cyklem: co miesiac generuje platnosc, sprawdza czy zaplacono, jesli nie — uruchamia sciezke windykacji (dunning).

**Windykacja / Dunning (Brief 27):** Konfigurowalne sciezki odzyskiwania platnosci. Domyslna sciezka: 16 krokow od dnia 0 do 45 (przypomnienie email → ostrzezenie → proba ponownej platnosci → ograniczenie dostepu → blokada → degradacja planu → anulowanie subskrypcji). Admin moze tworzyc wlasne sciezki z 11 typami akcji. Pelna historia eventow windykacji.

**Historia platnosci (Brief 27):** Kazda platnosc rejestrowana w tabeli payments (kwota, bramka, metoda, status). Uzytkownik widzi pelna historie w panelu konta.

**Webhooks per organizacja (Brief 27):** Organizacja moze skonfigurowac URL do otrzymywania webhookow o 13 typach eventow (platnosc, subskrypcja, faktura, zespol, plan). Podpis HMAC-SHA256, rotacja klucza, auto-disable po 10 kolejnych bledach, historia dostaw.

### 6. Faktury i KSeF

Automatyczne generowanie faktur PDF po kazdej platnosci. Integracja z Fakturownia (polskie faktury VAT). Przygotowanie pod KSeF (Krajowy System e-Faktur) — polski system obowiazkowego fakturowania elektronicznego.

### 7. Plany i limity

4 domyslne plany: Free, Starter (49 PLN/mies), Pro (149 PLN/mies), Enterprise (499 PLN/mies). Kazdy plan definiuje limity: max procesow, wykonan, integracji, operacji AI, czlonkow zespolu, przestrzeni dyskowej. System automatycznie blokuje z komunikatem "Zmien plan" gdy limit przekroczony. Add-ony: dokupywalne pakiety zasobow.

### 8. Powiadomienia i szablony emaili

Powiadomienia w aplikacji (ikona dzwonka), emailem i z preferencjami per uzytkownik. 8 szablonow emaili HTML: powitanie, reset hasla, zaproszenie, weryfikacja email, platnosc udana, platnosc nieudana, usunięcie konta, bazowy layout. Szablony sa nadpisywalne — aplikacja (np. kreator) moze podmienic je na swoje z wlasnym brandingiem.

### 9. RODO / GDPR

Pelna zgodnosc z RODO:
- **Eksport danych:** Uzytkownik klika "Pobierz moje dane" → system pakuje wszystko w ZIP (profil, organizacja, subskrypcje, faktury, historia zmian, powiadomienia)
- **Usuniecie konta:** Uzytkownik klika "Usun konto" → 14 dni na anulowanie → automatyczny eksport danych → anonimizacja (dane osobowe zamieniane na hash, faktury zachowane 5 lat zgodnie z prawem)
- **Prawo do przenoszenia:** Dane w formacie JSON

### 10. Dziennik zmian (Audit Trail)

Pelna historia: kto co zmienil, kiedy, skad (IP, przegladarka). Stan PRZED i PO zmianie. Automatyczne podsumowanie zmian. Retencja konfigurowalna (domyslnie 90 dni).

### 11. Komunikacja w czasie rzeczywistym (WebSocket)

Powiadomienia pojawiaja sie natychmiast bez odswiezania strony. Mozliwosc wyslania wiadomosci do konkretnego uzytkownika, calej organizacji lub wszystkich.

### 12. Zadania w tle (Task Queue)

Emaile wysylane w tle (nie spowalniaja strony). Cron jobs: czyszczenie starych danych, reset licznikow, odnowienia subskrypcji. Dwa backendy: ARQ (produkcja z Redis) i Sync (development bez Redis).

### 13. Multi-tenancy (izolacja danych)

Automatyczna izolacja danych miedzy organizacjami. Middleware automatycznie wyciaga organizacje z tokenu — programista nie musi pamietac o filtrowaniu. Niemozliwe jest "przypadkowe" pokazanie danych innej firmy.

### 14. CLI (narzedzia administracyjne)

Komendy: `fasthub seed` (zaladuj domyslne plany/role), `fasthub create-admin` (stworz administratora), `fasthub check` (sprawdz czy baza/Redis dziala), `fasthub shell` (interaktywna konsola).

### 15. Przechowywanie plikow

Upload plikow z walidacja (rozmiar, typ). Dwa backendy storage: Local (development) i S3 (produkcja). Automatyczne sledzenie zuzycia przestrzeni per organizacja.

### 16. Warstwa bezpieczenstwa

Szyfrowanie danych wrazliwych (Fernet AES), ochrona przed atakami (XSS, clickjacking, MIME sniffing), HTTPS, rate limiting, Request ID do diagnostyki, filtrowanie danych wrazliwych z logow.

---

## Jak to wyglada dla uzytkownika

```
Logowanie / Rejestracja (+ GUS) / Social Login / 2FA
         │
         ▼
    Dashboard
    (statystyki, aktywnosc)
         │
    ┌────┼──────────────┬──────────────────────┐
    │    │               │                      │
    ▼    ▼               ▼                      ▼
  Zespol  Konto (9 tab)  Billing            Super Admin
  (czlon- (profil, firma, (plany, bramki,   (organizacje,
  kowie,  plan, platnosci, checkout, status) metryki,
  zapra-  faktury, 2FA,                      uzytkownicy,
  szanie, sesje, zespol,                     dunning paths)
  role)   powiadomienia,
          API/webhooks)
```

---

## Co jest gotowe — pelna lista

### Backend (fasthub_core) — 27+ modulow
| Modul | Opis | Brief |
|-------|------|-------|
| Auth | JWT, bcrypt, blacklist, magic link, weryfikacja email | 1-9 |
| 2FA / TOTP | Weryfikacja dwuetapowa, QR code, kody zapasowe | 26 |
| Session Management | Sledzenie sesji (device, IP), wylogowanie zdalne | 26 |
| Social Login | Google, GitHub, Microsoft OAuth | 18 |
| Users & Organizations | Multi-org, zaproszenia, role, rozszerzone pola | 1-9, 19, 24 |
| RBAC | 4 role systemowe (Wlasciciel/Admin/Edytor/Podglad), custom roles | 1-9, 24 |
| Audit Trail | Historia zmian, before/after, IP tracking | 1-9 |
| Notifications | In-app + email, preferencje, 8 typow | 1-9 |
| WebSocket | Real-time, per user/org/broadcast | 1-9 |
| Redis | Cache, pub/sub, health check | 10 |
| Event Bus | Pub/sub z wildcard matching | 10 |
| Encryption | Fernet AES, key rotation, masking | 10 |
| OAuth | PKCE, multi-provider, token storage | 10 |
| Webhooks (system) | HMAC signatures, deduplication | 10 |
| Webhooks (per org) | Konfigurowalne endpointy per organizacja, 13 typow eventow | 27 |
| Billing | Plany, addony, usage tracking, limity | 10 |
| Dunning | Konfigurowalne sciezki windykacji, 11 typow akcji, historia | 27 |
| Payment History | Rejestracja i historia platnosci per organizacja | 27 |
| GUS API | Pobieranie danych firm z GUS/REGON po NIP | 25 |
| Monitoring | Sentry, structured logging | 13 |
| Rate Limiting | Per-endpoint, Redis/memory | 13 |
| Health Checks | /health, /ready, custom checks | 13 |
| File Storage | S3 + Local, upload walidacja | 14 |
| Feature Flags | Per plan, check_feature, require_feature | 14 |
| Background Tasks | ARQ + Sync, email queue, cron | 15 |
| Payment Gateway | 5 bramek (Stripe, PayU, Tpay, P24, PayPal) | 16, 20 |
| Multi-tenancy | Auto-izolacja danych, TenantMiddleware | 17 |
| CLI | seed, create-admin, check, shell | 17 |
| Email Templates | 8 szablonow HTML, Jinja2, nadpisywalne | 19 |
| Invitations | System zaproszen email → link → dolaczenie | 19 |
| GDPR | Eksport danych, anonimizacja, deletion workflow | 18 |
| KSeF | Krajowy System e-Faktur (przygotowanie) | 21 |
| Shared Clients | HTTP clients: Stripe, Fakturownia, PayU, Tpay, P24, PayPal | 16, 20 |
| RecurringManager | Cykliczne platnosci, delegacja do DunningService | 20, 27 |

### Frontend
| Element | Opis |
|---------|------|
| Design system | Tailwind CSS + Outfit font + wlasne komponenty (Btn, Fld, Tile, Chk, Rad, Toggle, SectionCard, StatusBadge, Lbl) |
| Layouty | AppShell (ciemny header + sidebar), SidebarLayout (taby), WizardLayout (kreator krokowy) |
| Konfiguracja | app.config.ts — nazwa, logo, kolory, URL-e w jednym pliku |
| Strony | Login, Register, Dashboard, Team, Billing, Onboarding, Users, **AccountPage (9 zakladek)**, SuperAdmin |
| Panel Konto (Brief 28) | 9 zakladek: Profil, Firma (+ GUS lookup), Plan, Platnosci, Faktury, Bezpieczenstwo (2FA, sesje), Zespol, Powiadomienia, API/Webhooks |
| Rejestracja (Brief 25) | Rozszerzona rejestracja z NIP → auto-uzupelnianie danych z GUS |
| Stan | Zustand stores (auth, org, billing) |
| API client | Axios z auto-refresh tokenow + account.ts (2FA, sesje, GUS, webhooks, payments) |

### Testy
~780 testow, CI: GitHub Actions (backend + frontend).

---

## Wartosc biznesowa

1. **Oszczednosc czasu:** 6-12 miesiecy pracy gotowe "z pudełka"
2. **Polskie platnosci:** BLIK, przelewy, PayU, Tpay, P24 — nie tylko Stripe
3. **Zgodnosc z prawem:** RODO, KSeF ready, polskie faktury VAT
4. **Elastycznosc:** Kazdy modul wymienny (storage: local→S3, task queue: sync→ARQ, bramka: Stripe→PayU)
5. **Skalowalnosc:** Od startupu do enterprise
6. **Przetestowane:** 780+ testow, CI/CD ready

---

*FastHub v4.0 | Zaktualizowane 2026-03-09 | Po briefach 1-28*
