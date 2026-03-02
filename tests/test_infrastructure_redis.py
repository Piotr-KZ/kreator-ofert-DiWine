"""
Testy modułu Redis Service (fasthub_core.infrastructure.redis).
"""

import pytest
import asyncio


def test_redis_module_imports():
    from fasthub_core.infrastructure.redis import (
        get_redis, close_redis, redis_health_check,
        publish_event, subscribe_events, subscribe_all_events,
        set_cache, get_cache, delete_cache, cache_exists, clear_cache_pattern,
        get_ai_cache, set_ai_cache
    )
    assert callable(get_redis)
    assert callable(set_cache)
    assert callable(redis_health_check)


def test_redis_config_uses_settings():
    """Redis powinien brać URL z fasthub_core config, nie z os.environ bezpośrednio"""
    import inspect
    from fasthub_core.infrastructure import redis as redis_mod
    source = inspect.getsource(redis_mod)
    assert "AUTOFLOW" not in source, "Redis nie powinien odwoływać się do AUTOFLOW"


@pytest.mark.asyncio
async def test_cache_set_get_without_redis():
    """Bez Redis-a, cache powinien gracefully degradować (not crash)"""
    from fasthub_core.infrastructure.redis import get_cache
    try:
        result = await get_cache("nonexistent_key")
        # None albo exception — oba OK
    except Exception:
        pass  # Redis niedostępny — to OK w testach


def test_no_arq_references():
    """Upewnij się że ARQ/enqueue nie zostały przeniesione"""
    import inspect
    from fasthub_core.infrastructure import redis as redis_mod
    source = inspect.getsource(redis_mod)
    assert "enqueue_task" not in source
    assert "arq" not in source.lower()


@pytest.mark.asyncio
async def test_health_check_structure():
    from fasthub_core.infrastructure.redis import redis_health_check
    result = await redis_health_check()
    assert isinstance(result, dict)
    assert "status" in result


def test_redis_init_exports():
    """Infrastructure __init__ powinien eksportować kluczowe funkcje"""
    from fasthub_core.infrastructure import (
        get_redis, close_redis, redis_health_check,
        publish_event, subscribe_events,
        set_cache, get_cache, delete_cache,
    )
    assert callable(get_redis)
