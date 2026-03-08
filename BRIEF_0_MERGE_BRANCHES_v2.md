# BRIEF 0: FastHub — Mergowanie niezintegrowanych branchy do main (v2)

## Dla: Opus CLI (kodowanie)
## Od: Strategia (planowanie i weryfikacja)
## Data: 2026-03-08
## Priorytet: KRYTYCZNY — wykonaj PRZED jakąkolwiek inną pracą
## Wersja: 2.0 — zaktualizowane po odkryciu że feature/social-login zawiera briefy 15-21

---

## KONTEKST

FastHub ma gotowy kod briefów 15-21 (payment gateway, task queue, multi-tenancy, social login, GDPR, email templates, polskie bramki, KSeF). Ten kod NIGDY nie został zmergowany do main. Main kończy się na Brief 14.

Kod jest rozłożony na dwóch kluczowych branchach:
- `feature/payment-gateway` — Brief 16 (payment gateway abstraction + Stripe) — PUSHED do GitHub
- `feature/social-login` — mega-branch zawierający Briefy 15+17, 18, 18-19, 20-21 — 3 commity NIE PUSHNIĘTE (istnieją tylko lokalnie)

Są też osobne branche dla Brief 15 (`feature/background-tasks`) i Brief 17 (`feature/tenant-middleware-cli`), ale ich kod jest ZDUPLIKOWANY na `feature/social-login` w nowszej wersji. Nie mergujemy ich osobno — użyjemy wersji z social-login.

Dodatkowo są 3 mniejsze branche: `feature/remaining-tests`, `feature/workflow-dispatch`, `feature/universal-modules-transfer`.

---

## ZASADY

1. **NIE ruszaj fasthub-frontend/** — frontend jest już zmodernizowany po Brief 1. Ten brief dotyczy TYLKO backendu.
2. Po każdym mergu: sprawdź konflikty, uruchom testy.
3. NIE rób squash merge — zachowaj historię commitów.
4. Jeśli testy failują — napraw zanim przejdziesz dalej.

---

## PRZED ROZPOCZĘCIEM

```bash
cd "C:\Projekty internetowe\Fasthub"
git checkout main
git pull origin main
git status  # musi być czysto

# Backup
git checkout -b backup/main-before-merge
git checkout main

# KROK KRYTYCZNY: Push 3 lokalnych commitów z feature/social-login
git checkout feature/social-login
git log --oneline -10  # powinieneś widzieć commity 55693c0, a3aaaee, 23ca49a
git push origin feature/social-login
git checkout main
```

**WAŻNE:** Jeśli `git push` dla social-login nie działa (np. branch nie istnieje na remote), użyj:
```bash
git push -u origin feature/social-login
```

---

## KOLEJNOŚĆ MERGOWANIA

### MERGE 1: feature/remaining-tests
**Co to jest:** Analiza test coverage, dokumentacja testów
**Ryzyko:** Minimalne — głównie pliki .md

```bash
git merge origin/feature/remaining-tests --no-ff -m "Merge: remaining-tests (test coverage analysis)"
```

Sprawdź konflikty → rozwiąż → uruchom testy:
```bash
python -m pytest tests/ -v --tb=short -q 2>&1 | tail -15
```

---

### MERGE 2: feature/workflow-dispatch
**Co to jest:** Fix testów
**Ryzyko:** Minimalne

```bash
git merge origin/feature/workflow-dispatch --no-ff -m "Merge: workflow-dispatch (test fixes)"
```

Sprawdź konflikty → testy.

---

### MERGE 3: feature/universal-modules-transfer
**Co to jest:** Migracja Alembic billing v2 tables
**Ryzyko:** Średnie — migracje bazy danych

```bash
git merge origin/feature/universal-modules-transfer --no-ff -m "Merge: universal-modules-transfer (billing v2 migrations)"
```

Sprawdź konflikty, szczególnie w `fasthub-backend/alembic/versions/`. Jeśli konflikty w migracjach: zachowaj OBE migracje, popraw depends_on jeśli trzeba.

---

### MERGE 4: feature/payment-gateway (Brief 16)
**Co to jest:** PaymentGateway(ABC), PaymentGatewayRegistry, StripeGateway, StripeWebhookHandler, Shared HTTP Clients (BaseHTTPClient, FakturowniaClient, StripeClient)
**Ryzyko:** Średnie-wysokie — modyfikuje billing/service.py, billing/__init__.py, config.py
**Dlaczego osobno:** Ten branch NIE jest na feature/social-login. Musi być zmergowany osobno.

```bash
git merge origin/feature/payment-gateway --no-ff -m "Merge: Brief 16 - payment gateway (multi-bramka + Stripe + shared clients)"
```

Sprawdź konflikty w:
- `fasthub_core/billing/__init__.py` — zachowaj WSZYSTKIE eksporty z obu stron
- `fasthub_core/billing/service.py` — nowe metody + istniejące
- `fasthub_core/config.py` — zachowaj WSZYSTKIE pola Settings z obu stron
- `fasthub_core/__init__.py` — zachowaj WSZYSTKIE importy
- `setup.py` — zachowaj WSZYSTKIE dependencies

Testy:
```bash
python -m pytest tests/ -v --tb=short -q 2>&1 | tail -15
python -c "from fasthub_core.billing.payment_gateway import PaymentGateway; print('OK')"
python -c "from fasthub_core.billing.payment_registry import PaymentGatewayRegistry; print('OK')"
python -c "from fasthub_core.billing.gateways.stripe_gateway import StripeGateway; print('OK')"
python -c "from fasthub_core.clients.base_client import BaseHTTPClient; print('OK')"
```

---

### MERGE 5: feature/social-login (Briefy 15+17, 18, 18-19, 20-21 — MEGA MERGE)
**Co to jest:** Wszystko co zostało:
- Brief 15: Background Tasks (ARQ + Sync task queue)
- Brief 17: Multi-tenancy Middleware + CLI Commands
- Brief 18: Social Login (Google, GitHub, Microsoft)
- Brief 18-19: GDPR/RODO Export + Email Templates + Invitations
- Brief 20-21: Polskie bramki (PayU, Tpay, P24, PayPal) + KSeF

**Ryzyko:** WYSOKIE — to jest największy merge, zawiera zmiany w wielu plikach core

```bash
git merge origin/feature/social-login --no-ff -m "Merge: Briefs 15+17+18+18-19+20-21 (tasks, tenancy, social login, GDPR, email templates, polish gateways, KSeF)"
```

**UWAGA O DUPLIKACJI:** Ten branch zawiera Brief 15 i 17 w połączonej wersji. NIE mergowaliśmy wcześniej `feature/background-tasks` ani `feature/tenant-middleware-cli` osobno — bo social-login ma nowszą, zintegrowaną wersję tego kodu. Jeśli zobaczysz konflikty z plikami task queue lub tenancy — to jest OK, użyj wersji z social-login.

Sprawdź konflikty w:
- `fasthub_core/__init__.py` — zachowaj WSZYSTKIE importy (będzie ich dużo)
- `fasthub_core/config.py` — zachowaj WSZYSTKIE pola (PayU, Tpay, P24, PayPal, GDPR, SMTP, itd.)
- `fasthub_core/billing/__init__.py` — zachowaj eksporty z OBIE merge'ów (Brief 16 + Brief 20-21)
- `fasthub_core/billing/service.py` — może kolidować z Brief 16, zachowaj OBA zestawy zmian
- `fasthub_core/auth/` — nowe pliki social login
- `fasthub_core/users/models.py` — nowe kolumny (google_id, github_id, microsoft_id)
- `fasthub-backend/alembic/versions/` — nowe migracje
- `setup.py` — nowe dependencies

**Szczególna uwaga na billing:** Brief 16 (Merge 4) dodał payment_gateway.py, payment_registry.py, gateways/stripe_gateway.py. Brief 20-21 (w tym mergu) dodaje gateways/payu_gateway.py, tpay_gateway.py, p24_gateway.py, paypal_gateway.py + recurring_manager.py. Te pliki powinny współistnieć bez konfliktu (nowe pliki). Ale `gateways/__init__.py` i `billing/__init__.py` mogą mieć konflikty w eksportach — zachowaj WSZYSTKIE.

Testy:
```bash
python -m pytest tests/ -v --tb=short -q 2>&1 | tail -30

# Sprawdź kluczowe importy
python -c "from fasthub_core.billing.gateways.stripe_gateway import StripeGateway; print('Stripe OK')"
python -c "from fasthub_core.auth.social_login import SocialLoginService; print('Social OK')"
python -c "from fasthub_core.gdpr import ExportService; print('GDPR OK')"
python -c "from fasthub_core.email import TemplateEngine; print('Email OK')"
```

---

## BRANCHE KTÓRYCH NIE MERGUJEMY

- `feature/background-tasks` — duplikat, kod jest w nowszej wersji na social-login
- `feature/tenant-middleware-cli` — duplikat, kod jest w nowszej wersji na social-login

Te branche można potem usunąć (ale nie teraz — zostawiamy jako referencję).

---

## PO WSZYSTKICH MERGACH — WERYFIKACJA KOŃCOWA

```bash
# 1. Pełny test suite
python -m pytest tests/ -v --tb=short 2>&1 | tail -30

# 2. Kluczowe importy — wszystko co powinno istnieć po mergach
python -c "
modules = [
    'fasthub_core.billing.payment_gateway',
    'fasthub_core.billing.payment_registry',
    'fasthub_core.billing.gateways.stripe_gateway',
    'fasthub_core.clients.base_client',
    'fasthub_core.clients.fakturownia_client',
]
for m in modules:
    try:
        __import__(m)
        print(f'OK: {m}')
    except ImportError as e:
        print(f'FAIL: {m} — {e}')
"

# 3. Sprawdź strukturę katalogów
dir fasthub_core\billing\gateways\
dir fasthub_core\clients\
dir fasthub_core\tasks\ 2>nul || echo "tasks: sprawdź czy istnieje pod inną nazwą"
dir fasthub_core\tenancy\ 2>nul || echo "tenancy: sprawdź czy istnieje pod inną nazwą"
dir fasthub_core\gdpr\ 2>nul || echo "gdpr: sprawdź czy istnieje pod inną nazwą"
dir fasthub_core\email\ 2>nul || echo "email: sprawdź czy istnieje pod inną nazwą"

# 4. Frontend — nadal builduje (Brief 1 nie powinien być dotknięty)
cd fasthub-frontend
npm run build 2>&1 | tail -5
cd ..

# 5. Git log
git log --oneline -15
```

### Push

```bash
git push origin main
```

---

## RAPORT PO ZAKOŃCZENIU

Wypisz tabelę:

| # | Branch/Brief | Konflikty | Rozwiązanie | Testy |
|---|---|---|---|---|
| 1 | remaining-tests | ? | ? | PASS/FAIL |
| 2 | workflow-dispatch | ? | ? | PASS/FAIL |
| 3 | universal-modules-transfer | ? | ? | PASS/FAIL |
| 4 | payment-gateway (Brief 16) | ? | ? | PASS/FAIL |
| 5 | social-login (Briefy 15-21) | ? | ? | PASS/FAIL |

Plus:
- Łączna liczba nowych plików na main
- Wynik końcowy testów
- Lista modułów które się importują / nie importują
- Ewentualne problemy do rozwiązania

---

## CZEGO NIE ROBIĆ

- NIE ruszaj fasthub-frontend/ — jest zmodernizowany po Brief 1
- NIE modyfikuj kodu poza rozwiązywaniem konfliktów
- NIE merguj feature/background-tasks osobno (duplikat — jest na social-login)
- NIE merguj feature/tenant-middleware-cli osobno (duplikat — jest na social-login)
- NIE usuwaj żadnych branchy
- NIE rób rebase — tylko merge
- NIE pushuj po każdym mergu — pushuj raz na końcu po pełnej weryfikacji

---

## JEŚLI COŚ PÓJDZIE NIE TAK

```bash
git checkout main
git reset --hard backup/main-before-merge
git push origin main --force
```

---

## PO TYM BRIEFIE — main zawiera:

| Brief | Moduł | Status |
|---|---|---|
| 1-14 | Auth, RBAC, Audit, Notifications, WebSocket, Redis, Events, OAuth, Billing (basic), Logging, Monitoring, Rate Limiting, Health, File Storage, Feature Flags | Było na main |
| 15 | Background Tasks (ARQ + Sync) | NOWE z merge |
| 16 | Payment Gateway (ABC + Registry + Stripe) | NOWE z merge |
| 17 | Multi-tenancy Middleware + CLI | NOWE z merge |
| 18 social | Social Login (Google, GitHub, Microsoft) | NOWE z merge |
| 18-19 | GDPR Export + Email Templates + Invitations | NOWE z merge |
| 20-21 | Polskie bramki (PayU, Tpay, P24, PayPal) + KSeF | NOWE z merge |

FastHub main = **kompletny backend SaaS z polskimi płatnościami i RODO.**

Gotowe do:
- Brief 2 nasz (naprawa integracji frontend↔backend)
- Budowanie kreatora stron

*Brief #0 v2, przygotowany przez Strategię, 2026-03-08*
