-- Demo Audit Logs for AutoFlow SaaS
-- Creates sample audit log entries for SuperAdmin actions

-- Get SuperAdmin ID
DO $$
DECLARE
    superadmin_id UUID;
    test_user_id UUID;
BEGIN
    -- Find SuperAdmin
    SELECT id INTO superadmin_id FROM users WHERE is_superuser = true LIMIT 1;
    
    -- Find a test user to use in logs
    SELECT id INTO test_user_id FROM users WHERE email = 'bob.smith@techcorp.com';
    
    IF superadmin_id IS NOT NULL AND test_user_id IS NOT NULL THEN
        -- Create sample audit logs
        INSERT INTO audit_logs (id, user_id, action, resource_type, resource_id, details, ip_address, user_agent, created_at)
        VALUES
          -- User update action (3 days ago)
          (gen_random_uuid(), superadmin_id, 'user.update', 'user', test_user_id, 
           '{"email": "bob.smith@techcorp.com", "changes": {"full_name": {"old": "Bob Smith", "new": "Bob Smith Jr."}}}',
           '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
           NOW() - INTERVAL '3 days'),
          
          -- User view action (2 days ago)
          (gen_random_uuid(), superadmin_id, 'user.view', 'user', test_user_id,
           '{"email": "bob.smith@techcorp.com", "full_name": "Bob Smith Jr."}',
           '127.0.0.1', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
           NOW() - INTERVAL '2 days'),
          
          -- Organization view action (1 day ago)
          (gen_random_uuid(), superadmin_id, 'organization.view', 'organization', 
           (SELECT id FROM organizations WHERE name = 'TechCorp Solutions'),
           '{"name": "TechCorp Solutions", "slug": "techcorp-solutions"}',
           '127.0.0.1', 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
           NOW() - INTERVAL '1 day'),
          
          -- System health check (today)
          (gen_random_uuid(), superadmin_id, 'system.health_check', 'system', superadmin_id,
           '{"status": "healthy", "database": "connected", "redis": "connected"}',
           '127.0.0.1', 'curl/7.68.0',
           NOW() - INTERVAL '2 hours');
        
        RAISE NOTICE '✅ Created 4 demo audit log entries for SuperAdmin';
    ELSE
        RAISE NOTICE '⚠️  SuperAdmin or test user not found - skipping audit logs';
    END IF;
END $$;

-- Summary
SELECT '✅ Demo audit logs created!' AS status;
SELECT COUNT(*) AS audit_log_count FROM audit_logs;
