# FastHub — Architektura Systemu

> Dokument biznesowy dla wlasciciela i partnerow.
> Wersja: 2.1 | Data: 2026-03-02

---

## Co to jest FastHub

FastHub to **platforma-fundament**, na ktorej buduje sie aplikacje biznesowe typu SaaS (oprogramowanie jako usluga). Wyobraz sobie to tak: zamiast budowac kazda nowa aplikacje od zera, masz gotowe "podwozie" — logowanie, organizacje, uprawnienia, powiadomienia, platnosci, bezpieczenstwo. Nowa aplikacja doklada tylko swoja unikalna logike biznesowa.

**Analogia:** FastHub to jak plyta fundamentowa domu. Mozesz na niej postawic biurowiec, klinike albo sklep — fundament jest ten sam, ale budynek jest inny.

---

## Dla kogo jest FastHub

1. **Tworca nowych aplikacji SaaS** — oszczedza miesiace pracy, bo nie buduje podstaw od zera
2. **Partner technologiczny** — dostaje sprawdzony fundament z dokumentacja i testami
3. **Klient koncowy** — korzysta z aplikacji zbudowanej na FastHub (np. AutoFlow), nie widzi fundamentu, ale dzieki niemu wszystko dziala stabilnie i bezpiecznie

---

## Z czego sklada sie system

FastHub ma trzy glowne czesci:

```
┌─────────────────────────────────────────────────┐
│                  UZYTKOWNIK                      │
│            (przegladarka / telefon)              │
└────────────────────┬────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────┐
│              FRONTEND (interfejs)                │
│     To co uzytkownik widzi i klika.              │
│     Strony: logowanie, dashboard, ustawienia,    │
│     zespol, faktury.                             │
└────────────────────┬────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────┐
│              BACKEND (serwer API)                │
│     "Mozg" systemu. Przetwarza dane,             │
│     sprawdza uprawnienia, laczy sie z baza       │
│     danych, wysyla maile, obsluguje platnosci.   │
└────────────────────┬────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────┐
│         BAZA DANYCH + CACHE (pamiec)             │
│     PostgreSQL: trwale dane (uzytkownicy,        │
│     organizacje, faktury).                       │
│     Redis: szybka pamiec (sesje, blokady).       │
└─────────────────────────────────────────────────┘
```

Dodatkowo istnieje **FastHub Core** — pakiet z gotowymi modulami, ktory mozna "wlozyc" do dowolnej nowej aplikacji jak klocek LEGO.

---

## Moduly systemu — co kazdy robi

### 1. Logowanie i bezpieczenstwo

**Co to daje uzytkownikowi:** Moze sie zalogowac mailem i haslem, zresetowac haslo, zweryfikowac email. System pamięta sesje i chroni konto.

**Jak to dziala:**
- Uzytkownik loguje sie → dostaje "przepustke" (token) wazna 30 minut
- Po 30 minutach system automatycznie ja odświeża (uzytkownik tego nie widzi)
- Po wylogowaniu przepustka jest uniewazniona — nikt nie moze jej uzyc
- Hasla sa szyfrowane — nawet administratorzy nie widza ich w bazie
- Mozna zalogowac sie "magicznym linkiem" wystanym na mail (bez hasla)

**Zabezpieczenia:**
- Haslo musi miec minimum 8 znakow, wielka litere, mala litere i cyfre
- Po 5 nieudanych probach logowania — blokada na minute
- Rejestracja ograniczona do 3 na godzine (ochrona przed botami)

---

### 2. Organizacje i zespoly

**Co to daje:** Firma zaklada organizacje, zaprasza pracownikow, kazdy ma swoja role.

**Jak to dziala:**
- Kazdy uzytkownik moze stworzyc organizacje (firma, zespol, projekt)
- Zapraszanie czlonkow po adresie email
- Kazdy czlonek ma role: **Wlasciciel** (pelna kontrola), **Admin** (zarzadzanie), **Czlonek** (podstawowy dostep)
- Mozna miec wiele organizacji na jednym koncie
- Organizacja przechowuje dane firmowe: NIP, adres rozliczeniowy

**Przyklad:**
```
Organizacja "Budimex Sp. z o.o."
  ├── Jan Kowalski — Wlasciciel (pelna kontrola)
  ├── Anna Nowak — Admin (zaprasza ludzi, zmienia ustawienia)
  └── Piotr Wisniewski — Czlonek (widzi dane, nie zmienia ustawien)
```

---

### 3. Uprawnienia (kto co moze robic)

**Co to daje:** Precyzyjna kontrola — kto widzi faktury, kto zaprasza ludzi, kto zmienia ustawienia.

**Jak to dziala:**
- 12 podstawowych uprawnien w 4 kategoriach:
  - **Zespol:** wyswietlanie czlonkow, zapraszanie, usuwanie, zmiana rol
  - **Faktury:** przegladanie planow, zmiana planu, przegladanie faktur
  - **Ustawienia:** przegladanie, edycja, integracje
  - **Dziennik zmian:** przegladanie, eksport

- 3 gotowe role z przypisanymi uprawnieniami:
  - **Wlasciciel** — wszystkie uprawnienia
  - **Admin** — zespol + ustawienia + faktury (14 uprawnien)
  - **Czlonek** — tylko podglad (3 uprawnienia)

- Mozna tworzyc **wlasne role** — np. "Ksiegowy" z dostepem tylko do faktur

**Super Admin** (administrator systemu) — widzi i moze wszystko we wszystkich organizacjach.

---

### 4. Powiadomienia

**Co to daje:** Uzytkownik wie co sie dzieje — zaproszenia, zmiany rol, alerty bezpieczenstwa. Jak na Facebooku — dzwonek z liczba nieprzeczytanych.

**3 kanaly dostarczania:**
1. **W aplikacji** — ikona dzwonka, lista powiadomien, oznaczanie jako przeczytane
2. **Email** — wazne powiadomienia wysylane mailem
3. **Preferencje** — uzytkownik sam decyduje co chce dostawac

**8 typow powiadomien:**
| Typ | Przyklad | Email domyslnie |
|-----|----------|-----------------|
| Zaproszenie | "Jan zaprosil Cie do organizacji Budimex" | Tak |
| Zmiana roli | "Twoja rola zmieniona z Czlonek na Admin" | Tak |
| Alert bezpieczenstwa | "Nowe logowanie z nowego urzadzenia" | Tak (wymuszony) |
| Billing | "Faktura #123 wystawiona" | Tak |
| Systemowe | "Zaplanowana przerwa techniczna" | Nie |
| Impersonacja | "Administrator przejal Twoje konto" | Tak (wymuszony) |

**Wazne:** Alertow bezpieczenstwa i impersonacji NIE MOZNA wylaczyc — to ochrona uzytkownika.

---

### 5. Platnosci i faktury

**Co to daje:** Organizacja moze wybrać plan (darmowy, pro, enterprise), oplacac subskrypcje, przegladac faktury. System automatycznie kontroluje limity i ostrzega przed ich przekroczeniem.

**Integracje:**
- **Stripe** — obsluga platnosci karta, subskrypcje, webhooks, checkout session, customer portal
- **Fakturownia** — generowanie polskich faktur VAT

**Plany i limity (Brief 10):**
- Kazdy plan definiuje: max procesow, max wykonan/miesiac, max integracji, max operacji AI, max czlonkow, max storage
- Waluta domyslna: PLN (polski rynek)
- Add-ony: paczki dodatkowych zasobow (np. +100 wykonan)
- Usage tracking: automatyczne liczenie zuzycia per miesiac
- Middleware: enforce_limit() blokuje z HTTP 402 gdy limit przekroczony

**Statusy subskrypcji:**
- Aktywna — wszystko dziala
- Probna (trial) — darmowy okres testowy
- Zalegla — platnosc nie przeszla, grace period
- Anulowana — subskrypcja zakonczona

---

### 6. Dziennik zmian (Audit Trail)

**Co to daje:** Pelna historia — kto co zmienil, kiedy, skad. Niezbedne dla compliance i rozwiazywania problemow.

**Co jest rejestrowane:**
- Kto — uzytkownik (email, ID)
- Co — jaka akcja (tworzenie, edycja, usuwanie)
- Na czym — jaki zasob (uzytkownik, organizacja, subskrypcja)
- Kiedy — dokladna data i godzina
- Skad — adres IP, przegladarka
- Co sie zmienilo — stan PRZED i PO zmianie (np. "plan: pro → enterprise")

**Automatyczne podsumowanie:** System sam generuje czytelny opis zmian, np.:
> "Zmieniono plan z 'pro' na 'enterprise', zmieniono billing_country z 'PL' na 'DE'"

**Retencja:** Logi starsze niz 90 dni sa automatycznie usuwane (konfigurowalny okres).

---

### 7. Komunikacja w czasie rzeczywistym (WebSocket)

**Co to daje:** Powiadomienia pojawiaja sie natychmiast — bez odswiezania strony. Jak na Slacku — wiadomosc przychodzi w sekundzie.

**Mozliwosci:**
- Wyslanie wiadomosci do konkretnego uzytkownika
- Broadcast do calej organizacji (np. "proces zakonczony")
- Broadcast do wszystkich (np. "przerwa techniczna za 15 minut")
- Sprawdzanie kto jest online

**Ograniczenie:** Obecnie dziala na jednym serwerze. Przy skalowaniu do wielu serwerow potrzebny bedzie dodatkowy mechanizm (Redis pub/sub) — zaplanowane w przyszlej wersji.

---

### 8. Szyfrowanie danych (Brief 10)

**Co to daje:** Klucze API, tokeny OAuth i inne wrazliwe dane sa szyfrowane w bazie. Nawet jesli ktos uzyska dostep do bazy — nie odczyta sekretow.

**Jak to dziala:**
- Dane szyfrowane algorytmem Fernet (AES-128-CBC)
- Zaszyfrowane wartosci zaczynaja sie od "ENC:" — latwo je odroznic
- Admin moze zrotowac klucz szyfrowania — stare dane automatycznie przenoszone na nowy klucz
- W logach wrazliwe pola sa maskowane: "sk-very-***"
- Jesli klucz nie jest skonfigurowany — dane zapisywane jako plain JSON (nie crash, ale bez szyfrowania)

---

### 9. Magistrala zdarzen (Event Bus — Brief 10)

**Co to daje:** Rozne czesci systemu moga reagowac na zdarzenia — np. kiedy proces sie zakonczy, system automatycznie wysyla powiadomienie i aktualizuje statystyki.

**Jak to dziala:**
- Modul emituje zdarzenie: "execution.completed" z danymi
- Inne moduly sluchaja na wzorce: "execution.*" lapie wszystkie zdarzenia wykonania
- Kazdy handler reaguje niezaleznie — jeden wysyla email, drugi zapisuje statystyki
- Zdarzenia sa broadcastowane przez Redis (jesli dostepny) — dzialaja miedzy serwerami

**Przyklad:**
```
Proces zakonczony → Event: "execution.completed"
  ├── Handler 1: Aktualizuj statystyki zuzycia
  ├── Handler 2: Wyslij powiadomienie do uzytkownika
  └── Handler 3: Sprawdz czy nie przekroczono limitu
```

---

### 10. Integracje zewnetrzne (OAuth + Webhooks — Brief 10)

**Co to daje:** Gotowy mechanizm podlaczania zewnetrznych uslug (Google, Microsoft, Stripe) — autoryzacja OAuth i obsluga webhookow.

**OAuth:**
- Wsparcie PKCE (bezpieczniejszy flow autoryzacji)
- Automatyczne odswiezanie tokenow gdy wygasna
- Multi-provider: mozna podlaczyc Google, Microsoft, itp. niezaleznie
- Tokeny szyfrowane przed zapisem do bazy

**Webhooks:**
- Weryfikacja podpisow HMAC (SHA256, SHA1, MD5)
- Ochrona przed zmodyfikowanym payloadem
- Deduplication — ten sam event nie jest przetworzony dwa razy

---

### 11. Bramki platnosci (Payment Gateway — Brief 16)

**Co to daje:** System moze obslugiwac platnosci przez WIELE bramek jednoczesnie — np. Stripe, PayU, Tpay. Klient widzi wszystkie dostepne metody platnosci z wszystkich aktywnych bramek.

**Jak to dziala:**
- Kazda bramka implementuje ten sam kontrakt (interfejs) — dodanie nowej to jeden plik
- Rejestr bramek automatycznie pomija nieskonfigurowane — zero bledow
- Metody platnosci sa deduplikowane — jesli Stripe i PayU obsluguja BLIK, pokazuje sie raz
- Stripe obsluguje: karta, BLIK, Google Pay, Apple Pay

**Architektura pluggable:**
```
PaymentGateway (kontrakt)
  ├── StripeGateway   ← gotowe (Brief 16)
  ├── PayUGateway     ← planowane (Brief 20)
  └── TpayGateway     ← planowane (Brief 20)
```

**Stripe Webhooks:**
- 6 typow zdarzen: checkout, subskrypcja (created/updated/deleted), platnosc (failed/succeeded)
- 4 hook points: on_checkout_completed, on_subscription_canceled, on_payment_failed, on_payment_succeeded
- Deduplication — ten sam event nie jest przetworzony dwa razy

---

### 12. Klienci HTTP (Shared Clients — Brief 16)

**Co to daje:** Gotowe wrappery na zewnetrzne API — Stripe, Fakturownia — z retry, timeout, spojnym error handling.

**Jak to dziala:**
- BaseHTTPClient — bazowy klient z retry i timeout (httpx)
- FakturowniaClient — faktury VAT (dwa tryby: token klienta lub token firmowy)
- StripeClient — checkout, portal, webhooks, klienci

**Przyklad: Fakturownia w dwoch kontekstach:**
```
Kontekst 1 (Provider): FakturowniaClient(account="klient", api_token="token_klienta")
Kontekst 2 (Billing):  FakturowniaClient.from_config()  ← token firmowy z .env
```

---

### 13. Warstwa bezpieczenstwa

**Co to daje:** Ochrona przed typowymi atakami internetowymi — automatycznie, bez konfiguracji.

**Zabezpieczenia:**
| Ochrona | Co robi |
|---------|---------|
| Anti-clickjacking | Strona nie moze byc osadzona w ramce na obcej stronie |
| Anti-XSS | Przegladarka blokuje wstrzykniecie zlowrogiego kodu |
| Anti-MIME sniffing | Przegladarka nie zgaduje typu pliku (zapobiega atakom) |
| Content Security Policy | Kontrola skad moga byc ladowane skrypty i zasoby |
| HTTPS wymuszenie | W produkcji cala komunikacja jest szyfrowana |
| Request ID | Kazde zadanie dostaje unikalny numer — ulatwia diagnostyke |

**Request ID w praktyce:**
1. Uzytkownik zglasza "cos nie dziala"
2. Support mowi "podaj numer z naglowka X-Request-ID"
3. W logach natychmiast znajdujemy dokladny przebieg tego zadania

---

## Jak to wyglada dla uzytkownika

### Ekrany aplikacji

```
Logowanie / Rejestracja
         │
         ▼
    Dashboard
    (statystyki, wykresy, aktywnosc)
         │
    ┌────┼────────────┬──────────────┐
    │    │             │              │
    ▼    ▼             ▼              ▼
  Zespol  Ustawienia   Faktury     Super Admin
  (lista   (profil,     (plany,     (wszystkie
  czlonkow, organizacja, faktury,   organizacje,
  zapraszanie, haslo)    PDF)       metryki,
  role)                              impersonacja)
```

---

## Bezpieczenstwo danych

| Aspekt | Rozwiazanie |
|--------|-------------|
| Hasla | Szyfrowane bcrypt — nie da sie odczytac nawet z bazy |
| Sesje | JWT tokeny z krotkim czasem zycia (30 min) |
| Wylogowanie | Token natychmiast uniewazniony (blacklist) |
| Transmisja | HTTPS — szyfrowana komunikacja |
| Rate limiting | Ochrona przed atakami brute-force |
| Audit trail | Pelna historia zmian — kto, co, kiedy, skad |
| Uprawnienia | Kazda akcja sprawdzana — user widzi tylko to, do czego ma dostep |
| Dane wrazliwe | Hasla, tokeny, sekrety automatycznie filtrowane z logow |

---

## Skalowalnosc — jak system rosnie

| Faza | Uzytkownicy | Infrastruktura |
|------|-------------|----------------|
| Start | 1-100 | Jeden serwer, PostgreSQL, Redis |
| Wzrost | 100-1000 | Oddzielny serwer bazy, cache, load balancer |
| Skala | 1000-10000 | Wiele serwerow API, Redis cluster, WebSocket pub/sub |
| Enterprise | 10000+ | Kubernetes, mikroserwisy, dedykowane bazy per modul |

**Obecny stan:** System jest przygotowany na faze Start i Wzrost. Faza Skala wymaga dodania Redis pub/sub dla WebSocket (zaplanowane).

---

## Co jest gotowe, a co w planach

### Gotowe (Faza 1 — Briefs 1-9)
- Logowanie, rejestracja, weryfikacja email, reset hasla
- Organizacje i zespoly z rolami
- Zaawansowane uprawnienia (RBAC)
- Super Admin dashboard z impersonacja
- Pelny dziennik zmian (audit trail)
- Powiadomienia in-app + email
- WebSocket (komunikacja w czasie rzeczywistym)
- Middleware bezpieczenstwa (headers, request ID)

### Gotowe (Faza 2 — Brief 10)
- **Redis Service** — shared connection pool, cache, pub/sub, health check
- **Event Bus** — wildcard matching, multi-handler, Redis broadcast
- **Encryption** — Fernet AES, key rotation, credential masking
- **OAuth Base** — PKCE, multi-provider, token storage
- **Webhook Base** — HMAC signatures (SHA256/SHA1/MD5), deduplication
- **Billing System** — plany, addony, usage tracking, Stripe checkout/portal, limity
- 184 testow fasthub_core + 43 testy e2e AutoFlow (Brief 12)

### Gotowe (Faza 3 — Brief 12)
- **Testy e2e AutoFlow + fasthub_core** — 43 testy integracyjne
- Pokrycie: encryption, event bus, OAuth, webhooks, billing, manifest, cross-module

### Gotowe (Faza 4 — Briefs 13-16)
- **Structured Logging** — JSON w produkcji, kolorowy w dev (structlog)
- **Monitoring** — Sentry z filtrami PII (opcjonalny)
- **Rate Limiting** — per-endpoint, Redis/memory backend (slowapi)
- **Subscription Check** — middleware, dekorator, HTTP 402 enforcement
- **Health Checks** — /health, /ready, custom checks z timeoutem
- **File Storage** — S3 + Local backend, pluggable (Brief 14)
- **Feature Flags** — check_feature, require_feature per plan (Brief 14)
- **Background Tasks** — ARQ (Redis), pluggable backend, cron jobs (Brief 15)
- **Payment Gateway** — multi-bramka, pluggable, StripeGateway (Brief 16)
- **Stripe Webhooks** — 6 eventow, 4 hook points, deduplication (Brief 16)
- **Shared HTTP Clients** — BaseHTTPClient + Fakturownia + Stripe wrapper (Brief 16)
- 284 testow fasthub_core (zero regresji)

### Planowane
- Brief 11: Thin wrappery w AutoFlow (zamiana lokalnych kopii na import z fasthub_core)
- Brief 20: Kolejne bramki platnosci (PayU, Tpay, Przelewy24)
- Szablony HTML emaili (zamiast plain text)
- WebSocket skalowanie (Redis pub/sub dla multi-server)
- Dashboard metryki biznesowe

---

## Wartosc biznesowa FastHub

1. **Oszczednosc czasu:** Nowa aplikacja SaaS startuje w dni, nie miesiace
2. **Sprawdzone rozwiazania:** Kazdy modul jest przetestowany (327+ testow: 284 fasthub_core + 43 e2e AutoFlow)
3. **Bezpieczenstwo z automatu:** Bez dodatkowej pracy — szyfrowanie, uprawnienia, audit
4. **Elastycznosc:** Kazdy modul mozna wymienic lub rozszerzyc niezaleznie
5. **Skalowalnosc:** System gotowy na wzrost — od startupu do enterprise
6. **Dokumentacja:** Techniczne i biznesowa dokumentacja — latwiejsze wdrazanie partnerow

---

*Dokument przygotowany 2026-03-01*
*FastHub v2.0-alpha*
