# AutoFlow SaaS - TODO List

## Bugs to Fix

### 1. Team Page Issues
- [x] Fix Team page endpoint to return organization members
- [x] Ensure all members (admin and viewer) can see team list
- [x] Show current user as ADMIN (owner role)

### 2. Billing Page Issues
- [x] Create mock implementation without STRIPE_SECRET_KEY
- [x] Show available plans (Free/Pro/Enterprise)
- [x] Allow Owner and Admin to change plans (mock)
- [x] Viewer can only view billing info
- [x] Handle missing subscription gracefully

### 3. Users Page Issues
- [x] Restrict Users page to SuperAdmin only (is_superuser=true)
- [x] Create SuperAdmin user for testing
- [x] Test Users page with SuperAdmin
- [x] Verify it shows ALL users from ALL organizations
- [x] Regular owners should NOT have access

## Completed
- [x] Fix onboarding flow
- [x] Fix MemberRole enum type in database
- [x] Fix SQLAlchemy enum value handling
- [x] Fix OrganizationResponse schema UUID types

## Security & Performance Fixes (2026-01-02)

### Priority 1: Critical Security
- [x] Remove hashed_password from API responses (UserResponse schema)
- [x] Add rate limiting on /auth/login endpoint (max 5 attempts/minute)
- [x] Prevent SuperAdmin from deleting themselves

### Priority 2: Performance
- [x] Add database indexes on users.email and users.full_name
- [x] Fix N+1 query problem in /users/ endpoint (not applicable - no relationships in response)

### Priority 3: Audit & Monitoring
- [x] Implement audit log for SuperAdmin actions (create audit_logs table)
- [x] Add database health check to /health endpoint (already exists in /ready)

### Priority 4: Production Readiness
- [x] Document HTTPS enforcement requirements (PRODUCTION_READINESS.md)
- [x] Document JWT_SECRET rotation strategy (PRODUCTION_READINESS.md)
- [x] Document Redis configuration for rate limiting (PRODUCTION_READINESS.md)
- [x] Document database backup strategy (PRODUCTION_READINESS.md)

## Demo Data Creation (2026-01-02)

### Phase 1: Demo Users
- [x] Create 10 demo users with realistic names and emails
- [x] Create 4 demo organizations
- [x] Assign users to organizations with different roles (admin/viewer)

### Phase 2: Demo Subscriptions
- [x] Subscriptions: Skipped (mock endpoint works without Stripe data)
- [x] Memberships: Already created in Phase 1

### Phase 3: Demo Activity
- [x] Create audit logs for SuperAdmin actions (5 entries)
- [x] Dashboard statistics: Not applicable (uses real-time data from database)

### Phase 4: Verification
- [ ] Verify all demo users can login
- [ ] Verify Team page shows members
- [ ] Verify Users page shows all users (SuperAdmin)
- [ ] Verify Billing page shows subscriptions

## Settings Form Validation & UX Improvements (2026-01-02)

### Form Validation
- [x] Add NIP (Tax ID) validation - only digits, exactly 10 characters for Poland
- [x] Add Postal Code validation - format XX-XXX for Poland
- [x] Replace Country text input with dropdown selector (list of countries)
- [x] Add phone number validation (optional field)

### UX Improvements
- [x] After successful save, redirect to read-only view with saved data
- [x] Add "Edit" button in read-only view to enable editing again
- [x] Show success message after saving changes
- [x] Add loading state during save operation


## Documentation Updates (2026-01-02)
- [ ] Update README.md with new features (multi-org, SuperAdmin, validation)
- [ ] Add link to SYSTEM_DOCUMENTATION.md in README
