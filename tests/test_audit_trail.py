"""Testy rozbudowanego Audit Trail"""


def test_audit_model_has_before_after():
    """AuditLog musi mieć pola changes_before i changes_after"""
    from fasthub_core.audit.models import AuditLog
    assert hasattr(AuditLog, 'changes_before')
    assert hasattr(AuditLog, 'changes_after')
    assert hasattr(AuditLog, 'summary')


def test_audit_model_has_ip_useragent():
    """AuditLog musi mieć pola ip_address i user_agent"""
    from fasthub_core.audit.models import AuditLog
    assert hasattr(AuditLog, 'ip_address')
    assert hasattr(AuditLog, 'user_agent')


def test_audit_model_has_impersonation():
    """AuditLog musi śledzić impersonation"""
    from fasthub_core.audit.models import AuditLog
    assert hasattr(AuditLog, 'impersonated_by')


def test_audit_model_has_extra_data():
    """AuditLog musi mieć pole extra_data (dodatkowe dane)"""
    from fasthub_core.audit.models import AuditLog
    assert hasattr(AuditLog, 'extra_data')


def test_audit_model_has_organization_id():
    """AuditLog musi mieć pole organization_id"""
    from fasthub_core.audit.models import AuditLog
    assert hasattr(AuditLog, 'organization_id')


def test_audit_model_has_user_email():
    """AuditLog musi mieć pole user_email (denormalizacja)"""
    from fasthub_core.audit.models import AuditLog
    assert hasattr(AuditLog, 'user_email')


def test_audit_service_methods():
    """AuditService musi mieć wszystkie wymagane metody"""
    from fasthub_core.audit.service import AuditService
    assert hasattr(AuditService, 'log_action')
    assert hasattr(AuditService, 'get_logs')
    assert hasattr(AuditService, 'get_resource_history')
    assert hasattr(AuditService, 'cleanup_old_logs')
    assert hasattr(AuditService, 'get_stats')
    assert hasattr(AuditService, 'snapshot')
    assert hasattr(AuditService, 'log_model_change')


def test_audit_generate_summary():
    """_generate_summary musi generować czytelne opisy zmian"""
    from fasthub_core.audit.service import AuditService
    service = AuditService.__new__(AuditService)

    summary = service._generate_summary(
        {"plan": "pro", "seats": 10},
        {"plan": "enterprise", "seats": 50},
    )
    assert "plan" in summary
    assert "pro" in summary
    assert "enterprise" in summary
    assert "seats" in summary


def test_audit_generate_summary_added():
    """_generate_summary obsługuje dodanie nowego pola"""
    from fasthub_core.audit.service import AuditService
    service = AuditService.__new__(AuditService)

    summary = service._generate_summary(
        {},
        {"plan": "enterprise"},
    )
    assert "Dodano" in summary
    assert "plan" in summary


def test_audit_generate_summary_removed():
    """_generate_summary obsługuje usunięcie pola"""
    from fasthub_core.audit.service import AuditService
    service = AuditService.__new__(AuditService)

    summary = service._generate_summary(
        {"plan": "pro"},
        {},
    )
    assert "Usunięto" in summary or "Usuni" in summary


def test_audit_generate_summary_no_changes():
    """_generate_summary przy braku zmian"""
    from fasthub_core.audit.service import AuditService
    service = AuditService.__new__(AuditService)

    summary = service._generate_summary(
        {"plan": "pro"},
        {"plan": "pro"},
    )
    assert summary == "Brak zmian"


def test_audit_snapshot_is_static():
    """snapshot jest staticmethod — można wywołać bez instancji"""
    from fasthub_core.audit.service import AuditService
    assert callable(AuditService.snapshot)


def test_audit_sensitive_fields_filter():
    """Pola wrażliwe nie powinny być logowane"""
    from fasthub_core.audit.service import SENSITIVE_FIELDS
    assert "hashed_password" in SENSITIVE_FIELDS
    assert "password" in SENSITIVE_FIELDS
    assert "token" in SENSITIVE_FIELDS
    assert "magic_link_token" in SENSITIVE_FIELDS


def test_audit_router():
    """Router audit musi mieć prefix /api/audit i minimum 4 endpointy"""
    from fasthub_core.audit.routes import router
    assert router.prefix == "/api/audit"
    routes = [r for r in router.routes]
    assert len(routes) >= 4  # logs, resource history, stats, cleanup


def test_audit_schemas():
    """Schemas audit muszą być importowalne i poprawne"""
    from fasthub_core.audit.schemas import (
        AuditLogResponse, AuditLogList, AuditStatsResponse, RetentionResult,
    )
    result = RetentionResult(deleted_count=150, retention_days=90)
    assert result.deleted_count == 150
    assert result.retention_days == 90

    stats = AuditStatsResponse(total_entries=100, entries_last_24h=5)
    assert stats.total_entries == 100


def test_request_context():
    """get_request_context musi być callable"""
    from fasthub_core.audit.request_context import get_request_context
    assert callable(get_request_context)


def test_audit_importable_from_init():
    """audit_router, AuditService, get_request_context muszą być dostępne z fasthub_core"""
    from fasthub_core import audit_router, AuditService, get_request_context
    assert audit_router is not None
    assert AuditService is not None
    assert callable(get_request_context)


def test_audit_contract_uses_new_service():
    """FastHubAudit musi delegować do rozbudowanego AuditService"""
    from fasthub_core.contracts_impl import FastHubAudit
    import inspect
    source = inspect.getsource(FastHubAudit.log_action)
    assert "AuditService" in source
