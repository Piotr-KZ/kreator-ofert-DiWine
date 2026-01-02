-- Demo Data for AutoFlow SaaS
-- Creates organizations, users, and memberships
-- Password for all demo users: DemoPass123
-- Hashed password: $2b$12$LKzO8Z8vQ8Z8vQ8Z8vQ8vOe8Z8vQ8Z8vQ8Z8vQ8Z8vQ8Z8vQ8Z8vQ

-- Step 1: Create organizations
INSERT INTO organizations (id, name, slug, is_complete, created_at, updated_at)
VALUES
  ('a1111111-1111-1111-1111-111111111111', 'TechCorp Solutions', 'techcorp-solutions', true, NOW() - INTERVAL '30 days', NOW() - INTERVAL '30 days'),
  ('a2222222-2222-2222-2222-222222222222', 'Digital Innovations Ltd', 'digital-innovations', true, NOW() - INTERVAL '30 days', NOW() - INTERVAL '30 days'),
  ('a3333333-3333-3333-3333-333333333333', 'CloudStart Inc', 'cloudstart', true, NOW() - INTERVAL '30 days', NOW() - INTERVAL '30 days'),
  ('a4444444-4444-4444-4444-444444444444', 'DataFlow Systems', 'dataflow-systems', true, NOW() - INTERVAL '30 days', NOW() - INTERVAL '30 days');

-- Step 2: Create users
-- Password hash for "DemoPass123"
INSERT INTO users (id, email, full_name, hashed_password, is_active, is_verified, is_superuser, created_at, updated_at)
VALUES
  ('b1111111-1111-1111-1111-111111111111', 'alice.johnson@techcorp.com', 'Alice Johnson', '$2b$12$JOKDl4tOKpt9L/pYKl/dSu9fC4jshFsI9qDJhRU9czaPt0Ve9va9.', true, true, false, NOW() - INTERVAL '25 days', NOW() - INTERVAL '25 days'),
  ('b2222222-2222-2222-2222-222222222222', 'bob.smith@techcorp.com', 'Bob Smith', '$2b$12$JOKDl4tOKpt9L/pYKl/dSu9fC4jshFsI9qDJhRU9czaPt0Ve9va9.', true, true, false, NOW() - INTERVAL '25 days', NOW() - INTERVAL '25 days'),
  ('b3333333-3333-3333-3333-333333333333', 'carol.williams@digitalinnovations.com', 'Carol Williams', '$2b$12$JOKDl4tOKpt9L/pYKl/dSu9fC4jshFsI9qDJhRU9czaPt0Ve9va9.', true, true, false, NOW() - INTERVAL '25 days', NOW() - INTERVAL '25 days'),
  ('b4444444-4444-4444-4444-444444444444', 'david.brown@digitalinnovations.com', 'David Brown', '$2b$12$JOKDl4tOKpt9L/pYKl/dSu9fC4jshFsI9qDJhRU9czaPt0Ve9va9.', true, true, false, NOW() - INTERVAL '25 days', NOW() - INTERVAL '25 days'),
  ('b5555555-5555-5555-5555-555555555555', 'emma.davis@digitalinnovations.com', 'Emma Davis', '$2b$12$JOKDl4tOKpt9L/pYKl/dSu9fC4jshFsI9qDJhRU9czaPt0Ve9va9.', true, true, false, NOW() - INTERVAL '25 days', NOW() - INTERVAL '25 days'),
  ('b6666666-6666-6666-6666-666666666666', 'frank.miller@cloudstart.io', 'Frank Miller', '$2b$12$JOKDl4tOKpt9L/pYKl/dSu9fC4jshFsI9qDJhRU9czaPt0Ve9va9.', true, true, false, NOW() - INTERVAL '25 days', NOW() - INTERVAL '25 days'),
  ('b7777777-7777-7777-7777-777777777777', 'grace.wilson@cloudstart.io', 'Grace Wilson', '$2b$12$JOKDl4tOKpt9L/pYKl/dSu9fC4jshFsI9qDJhRU9czaPt0Ve9va9.', true, true, false, NOW() - INTERVAL '25 days', NOW() - INTERVAL '25 days'),
  ('b8888888-8888-8888-8888-888888888888', 'henry.moore@dataflow.systems', 'Henry Moore', '$2b$12$JOKDl4tOKpt9L/pYKl/dSu9fC4jshFsI9qDJhRU9czaPt0Ve9va9.', true, true, false, NOW() - INTERVAL '25 days', NOW() - INTERVAL '25 days'),
  ('b9999999-9999-9999-9999-999999999999', 'iris.taylor@dataflow.systems', 'Iris Taylor', '$2b$12$JOKDl4tOKpt9L/pYKl/dSu9fC4jshFsI9qDJhRU9czaPt0Ve9va9.', true, true, false, NOW() - INTERVAL '25 days', NOW() - INTERVAL '25 days'),
  ('baaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', 'jack.anderson@dataflow.systems', 'Jack Anderson', '$2b$12$JOKDl4tOKpt9L/pYKl/dSu9fC4jshFsI9qDJhRU9czaPt0Ve9va9.', true, true, false, NOW() - INTERVAL '25 days', NOW() - INTERVAL '25 days');

-- Step 3: Create memberships
INSERT INTO members (id, user_id, organization_id, role, joined_at, created_at, updated_at)
VALUES
  -- TechCorp Solutions
  ('c1111111-1111-1111-1111-111111111111', 'b1111111-1111-1111-1111-111111111111', 'a1111111-1111-1111-1111-111111111111', 'admin', NOW() - INTERVAL '20 days', NOW() - INTERVAL '20 days', NOW() - INTERVAL '20 days'),
  ('c2222222-2222-2222-2222-222222222222', 'b2222222-2222-2222-2222-222222222222', 'a1111111-1111-1111-1111-111111111111', 'viewer', NOW() - INTERVAL '20 days', NOW() - INTERVAL '20 days', NOW() - INTERVAL '20 days'),
  -- Digital Innovations Ltd
  ('c3333333-3333-3333-3333-333333333333', 'b3333333-3333-3333-3333-333333333333', 'a2222222-2222-2222-2222-222222222222', 'admin', NOW() - INTERVAL '20 days', NOW() - INTERVAL '20 days', NOW() - INTERVAL '20 days'),
  ('c4444444-4444-4444-4444-444444444444', 'b4444444-4444-4444-4444-444444444444', 'a2222222-2222-2222-2222-222222222222', 'viewer', NOW() - INTERVAL '20 days', NOW() - INTERVAL '20 days', NOW() - INTERVAL '20 days'),
  ('c5555555-5555-5555-5555-555555555555', 'b5555555-5555-5555-5555-555555555555', 'a2222222-2222-2222-2222-222222222222', 'viewer', NOW() - INTERVAL '20 days', NOW() - INTERVAL '20 days', NOW() - INTERVAL '20 days'),
  -- CloudStart Inc
  ('c6666666-6666-6666-6666-666666666666', 'b6666666-6666-6666-6666-666666666666', 'a3333333-3333-3333-3333-333333333333', 'admin', NOW() - INTERVAL '20 days', NOW() - INTERVAL '20 days', NOW() - INTERVAL '20 days'),
  ('c7777777-7777-7777-7777-777777777777', 'b7777777-7777-7777-7777-777777777777', 'a3333333-3333-3333-3333-333333333333', 'viewer', NOW() - INTERVAL '20 days', NOW() - INTERVAL '20 days', NOW() - INTERVAL '20 days'),
  -- DataFlow Systems
  ('c8888888-8888-8888-8888-888888888888', 'b8888888-8888-8888-8888-888888888888', 'a4444444-4444-4444-4444-444444444444', 'admin', NOW() - INTERVAL '20 days', NOW() - INTERVAL '20 days', NOW() - INTERVAL '20 days'),
  ('c9999999-9999-9999-9999-999999999999', 'b9999999-9999-9999-9999-999999999999', 'a4444444-4444-4444-4444-444444444444', 'viewer', NOW() - INTERVAL '20 days', NOW() - INTERVAL '20 days', NOW() - INTERVAL '20 days'),
  ('caaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', 'baaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', 'a4444444-4444-4444-4444-444444444444', 'viewer', NOW() - INTERVAL '20 days', NOW() - INTERVAL '20 days', NOW() - INTERVAL '20 days');

-- Summary
SELECT '✅ Demo data created successfully!' AS status;
SELECT 
  (SELECT COUNT(*) FROM organizations WHERE name LIKE 'TechCorp%' OR name LIKE 'Digital%' OR name LIKE 'CloudStart%' OR name LIKE 'DataFlow%') AS organizations,
  (SELECT COUNT(*) FROM users WHERE email LIKE '%techcorp.com' OR email LIKE '%digitalinnovations.com' OR email LIKE '%cloudstart.io' OR email LIKE '%dataflow.systems') AS users,
  (SELECT COUNT(*) FROM members WHERE id::text LIKE 'c%') AS memberships;

-- Demo credentials
SELECT '🔑 Demo Credentials:' AS info;
SELECT 'Email: alice.johnson@techcorp.com' AS example_1, 'Password: DemoPass123' AS password_1
UNION ALL
SELECT 'Email: carol.williams@digitalinnovations.com', 'Password: DemoPass123'
UNION ALL
SELECT 'Email: frank.miller@cloudstart.io', 'Password: DemoPass123';
