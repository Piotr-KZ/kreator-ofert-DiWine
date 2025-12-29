# Claude's Sections - Extracted Requirements

**Analyzed 10 sections**

---

## Section 1: SECURITY (Best Practices, OWASP)

**File:** `section_10.txt`

**Key Requirements:**
- SQL Injection
- XSS (Cross-Site Scripting)
- Command Injection
- Path Traversal
- NoSQL Injection
- SQL injection via email field
- XSS via email field
- 8-128 characters
- At least 1 uppercase letter
- At least 1 lowercase letter
- At least 1 digit
- At least 1 special character
- Weak passwords
- Dictionary attacks
- Common passwords
- ../../../etc/passwd
- /etc/passwd
- C:\Windows\System32
- Path traversal characters (../)
- Special characters

**Code Examples:** 0

---

## Section 2: MIGRACJA FIREBASE → POSTGRESQL

**File:** `section_10_final.txt`

**Key Requirements:**
- Incremental migration
- Data validation
- Error handling
- Progress tracking
- Rollback support
- Record counts match
- Foreign key integrity
- Data consistency
- No orphaned records
---
**CRITICAL: Always backup before migration!**
- Check record counts
- Look for errors
- Verify data transformations
- Record counts match
- Foreign key integrity
- No orphaned records
- Data consistency
---
- Check error logs

**Code Examples:** 12

---

## Section 3: KONWERSJA FIRESTORE → POSTGRESQL

**File:** `section_2_firestore_to_postgresql.txt`

**Database Tables:** organizations, process_executions, processes, integrations, invoices, subscriptions, api_tokens, users

**Key Requirements:**
✅ Flexible schema (dodaj pole kiedy chcesz)
✅ Nested objects (embedded documents)
✅ Denormalizacja (duplikacja danych OK)
❌ Brak JOINs (trzeba robić N queries)
❌ Brak transakcji między kolekcjami
❌ Trudne complex queries
✅ Fixed schema (migracje dla zmian)
✅ JOINs (pobierz dane z wielu tabel)
✅ ACID transactions
✅ Complex queries (GROUP BY, agregacje)
✅ Foreign keys (referential integrity)
⚠️ Normalizacja wymagana (no duplication)
-- Index dla szybkiego lookup
-- Brak subscription fields!
-- Osobna tabela dla subscriptions
-- Jeden user = jedna aktywna subskrypcja
-- PostgreSQL: 1 query (JOIN)
-- Index dla lookup
-- Insert
-- Query JSONB (PostgreSQL supports it!)

**Code Examples:** 0

---

## Section 4: AUTENTYKACJA I AUTORYZACJA

**File:** `section_3_auth_security.txt`

**Key Requirements:**
✅ ZALETY:
❌ WADY:
✅ ZALETY:
⚠️ WYMAGA:
- At least 8 characters
- Contains uppercase letter
- Contains lowercase letter
- Contains number
- Contains special character
⚠️ Token is only shown ONCE - save it!
- app.current_org_id (for organization isolation)
- app.current_user_id (for user-specific policies)
❌ ŹLE:
✅ DOBRZE:
⚠️ POTENCJALNE PROBLEMY
❌ ŹLE:
✅ DOBRZE:
❌ ŹLE:
✅ DOBRZE:
❌ ŹLE:

**Code Examples:** 0

---

## Section 5: INTEGRACJE (Stripe, Outlook, Fakturownia, Google)

**File:** `section_4.txt`

**Key Requirements:**
- test_connection()
- connect()
- disconnect()
- Create customers
- Create subscriptions
- Create checkout sessions
- Handle webhooks
- List invoices
- customer.subscription.created
- customer.subscription.updated
- customer.subscription.deleted
- invoice.payment_succeeded
- invoice.payment_failed
- Connect via IMAP (no OAuth)
- Read emails
- Search emails
- Download attachments
- Mark as read/unread
- Create invoices
- Get invoices

**Code Examples:** 0

---

## Section 6: section_5

**File:** `section_5.txt`

**Key Requirements:**
**Terminal 1 - Main Worker:**
**Terminal 2 - Beat (Scheduler):**
**Terminal 3 - Flower (Monitoring):**
---
---
**Features:**
- Real-time task monitoring
- Worker status
- Task history
- Task retry/revoke
- Task rate charts
---
---
---
---
---
**File: `/etc/systemd/system/celery-worker.service`**
--loglevel=info \
--concurrency=4 \
--logfile=/var/log/celery/worker.log

**Code Examples:** 26

---

## Section 7: section_6

**File:** `section_6.txt`

**Code Examples:** 0

---

## Section 8: TESTING (pytest)

**File:** `section_7.txt`

**Key Requirements:**
--verbose
--strict-markers
--tb=short
--cov=app
--cov-report=term-missing
--cov-report=html
--cov-fail-under=80
*/tests/*
*/migrations/*
*/__pycache__/*
*/venv/*
*/site-packages/*
✅ BEST PRACTICES
⚠️ COMMON ISSUES
---
✅ CHECKLIST DLA MANUSA

**Code Examples:** 0

---

## Section 9: DEPLOYMENT (Docker, CI/CD, Production)

**File:** `section_8.txt`

**Key Requirements:**
---
**Exclude z Docker image**
*.py[cod]
*$py.class
*.so
*.egg-info/
*.egg
*.swp
*.swo
*~
*.md
*.log
*.db
*.sqlite
-h HOST | --host=HOST       Host or IP under test
-p PORT | --port=PORT       TCP port under test
-s | --strict               Only execute subcommand if the test succeeds
-q | --quiet                Don't output any status messages
-t TIMEOUT | --timeout=TIMEOUT
-- COMMAND ARGS             Execute command with args after the test finishes

**Code Examples:** 0

---

## Section 10: PERFORMANCE OPTIMIZATION

**File:** `section_9.txt`

**Key Requirements:**
-- Performance indexes for AutoFlow
-- ============================================
-- USERS TABLE INDEXES
-- ============================================
-- Email lookup (login)
-- Organization + email (multi-tenant queries)
-- Active users lookup
-- Email verification lookup
-- Password reset lookup
-- ============================================
-- ORGANIZATIONS TABLE INDEXES
-- ============================================
-- Slug lookup (URL routing)
-- Stripe customer lookup
-- ============================================
-- SUBSCRIPTIONS TABLE INDEXES
-- ============================================
-- Organization lookup
-- Stripe subscription lookup
-- Active subscriptions

**Code Examples:** 0

---

