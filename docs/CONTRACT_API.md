# FastHub Core — Kontrakt API v2.0

## Dla kogo ten dokument
Dla programistów budujących aplikacje na FastHub (np. AutoFlow, FastCRM, FastHR).

## Zasady kontraktu
1. Sygnatury funkcji nie zmieniają się w ramach tej samej MAJOR wersji
2. Nowe funkcje są DODAWANE — stare nie znikają
3. Deprecated funkcje działają minimum 1 wersję po ogłoszeniu
4. Breaking changes tylko w nowej MAJOR wersji (v3.0)

## Jak używać

```python
# Instalacja
pip install -e /ścieżka/do/Fasthub

# Import kontraktu i implementacji
from fasthub_core.contracts_impl import FastHubAuth, FastHubUser, FastHubAudit

# Użycie
auth = FastHubAuth()
hashed = auth.hash_password("MojeHaslo123")
is_valid = auth.verify_password("MojeHaslo123", hashed)
```

---

## Dostępne kontrakty

### AuthContract — Logowanie i tokeny
Implementacja: `FastHubAuth`

| Metoda | Status | Opis |
|--------|--------|------|
| `hash_password(password)` | ✅ Gotowe | Hashowanie hasła bcrypt |
| `verify_password(plain, hashed)` | ✅ Gotowe | Weryfikacja hasła |
| `create_access_token(user_id, org_id)` | ✅ Gotowe | JWT access token (~30min) |
| `create_refresh_token(user_id)` | ✅ Gotowe | JWT refresh token (~7d) |
| `decode_token(token)` | ✅ Gotowe | Dekodowanie JWT |
| `blacklist_token(token, expires_at)` | ✅ Gotowe | Unieważnienie tokenu (Redis) |
| `is_token_blacklisted(token)` | ✅ Gotowe | Sprawdzenie czarnej listy |

### UserContract — Użytkownicy i organizacje
Implementacja: `FastHubUser`

| Metoda | Status | Opis |
|--------|--------|------|
| `get_current_user(token, db)` | ✅ Gotowe | Zalogowany user z tokenu |
| `get_user(user_id, db)` | ✅ Gotowe | User po ID |
| `list_organization_users(org_id, db)` | ✅ Gotowe | Wszyscy userzy w firmie |
| `get_user_role(user_id, org_id, db)` | ✅ Gotowe | Rola usera w firmie |

### PermissionContract — Uprawnienia
Implementacja: `FastHubPermission`

| Metoda | Status | Opis |
|--------|--------|------|
| `check_permission(user_id, org_id, perm, db)` | ⚠️ Basic | Tylko admin/viewer |
| `get_user_permissions(user_id, org_id, db)` | ⚠️ Basic | Rozbudowa w v2.0 |

**Obecne uprawnienia admin:** processes.view/edit/execute/delete, members.view/invite/remove, billing.view/manage, settings.view/edit, audit.view

**Obecne uprawnienia viewer:** processes.view, members.view, billing.view, settings.view

### BillingContract — Rozliczenia
Implementacja: `FastHubBilling`

| Metoda | Status | Opis |
|--------|--------|------|
| `get_subscription(org_id, db)` | ✅ Gotowe | Aktualna subskrypcja Stripe |
| `check_limit(org_id, resource, usage, db)` | 📅 v2.0 | Sprawdzenie limitów |
| `record_usage(org_id, resource, amount, db)` | 📅 v2.0 | Zapis zużycia |

### AuditContract — Historia zmian
Implementacja: `FastHubAudit`

| Metoda | Status | Opis |
|--------|--------|------|
| `log_action(user_id, org_id, action, ...)` | ✅ Gotowe | Zapis akcji |
| `get_audit_logs(org_id, ...)` | ✅ Gotowe | Pobranie logów z filtrami |

### NotificationContract — Powiadomienia
Implementacja: `FastHubNotification`

| Metoda | Status | Opis |
|--------|--------|------|
| `send_notification(user_id, type, title, msg)` | 📅 v2.0 | In-app + email |
| `send_email(to_email, template, variables)` | 📅 v2.0 | Email z szablonu |

### DatabaseContract — Baza danych
Implementacja: `FastHubDatabase`

| Metoda | Status | Opis |
|--------|--------|------|
| `get_db_session()` | ✅ Gotowe | Async DB session |
| `get_engine()` | ✅ Gotowe | SQLAlchemy engine |

---

## Podsumowanie statusu

| Kontrakt | Implementacja | Status |
|----------|--------------|--------|
| Auth | FastHubAuth | ✅ Pełna |
| User | FastHubUser | ✅ Pełna |
| Permission | FastHubPermission | ⚠️ Basic (admin/viewer) |
| Billing | FastHubBilling | ⚠️ Częściowa (brak limitów) |
| Audit | FastHubAudit | ✅ Pełna |
| Notification | FastHubNotification | 📅 Planowana v2.0 |
| Database | FastHubDatabase | ✅ Pełna |

## Wersjonowanie
- **v2.0-alpha** (obecna) — podstawowe kontrakty
- **v2.0** (planowana) — pełne RBAC, notifications, billing limits
- **v2.1** (planowana) — WebSocket, scheduler, event bus
