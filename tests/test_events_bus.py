"""
Testy modułu Event Bus (fasthub_core.events.bus).
"""

import pytest
import asyncio
from fasthub_core.events.bus import Event, EventBus


def test_event_creation():
    e = Event("user.login", {"user_id": "123"})
    assert e.event_type == "user.login"
    assert e.payload["user_id"] == "123"
    assert e.timestamp is not None
    assert e.source == "system"


def test_event_to_dict():
    e = Event("test.event", {"key": "value"}, source="api")
    d = e.to_dict()
    assert d["event_type"] == "test.event"
    assert d["source"] == "api"
    assert "timestamp" in d


def test_event_bus_singleton():
    from fasthub_core.events.bus import event_bus
    assert isinstance(event_bus, EventBus)


def test_event_bus_register_handler():
    bus = EventBus()
    handler_called = []

    def handler(event):
        handler_called.append(event)

    bus.register("test.*", handler)
    stats = bus.get_stats()
    assert stats["handlers_count"] > 0


def test_event_bus_wildcard_matching():
    bus = EventBus()
    matched = []

    bus.register("user.*", lambda e: matched.append(e))

    asyncio.get_event_loop().run_until_complete(
        bus.emit("user.login", {"user_id": "1"})
    )
    assert len(matched) == 1


def test_event_bus_no_autoflow_references():
    import inspect
    from fasthub_core.events import bus
    source = inspect.getsource(bus)
    assert "autoflow" not in source.lower()
    assert "process.started" not in source
    assert "execution." not in source


def test_event_bus_clear_handlers():
    bus = EventBus()
    bus.register("test.*", lambda e: None)
    bus.clear_handlers()
    assert bus.get_stats()["handlers_count"] == 0


@pytest.mark.asyncio
async def test_event_bus_emit_returns_count():
    bus = EventBus()
    bus.register("count.*", lambda e: None)
    bus.register("count.*", lambda e: None)
    count = await bus.emit("count.test", {})
    assert count >= 2


def test_event_bus_on_decorator():
    bus = EventBus()

    @bus.on("decorated.*")
    async def my_handler(event):
        pass

    assert bus.get_stats()["handlers_count"] >= 1


@pytest.mark.asyncio
async def test_event_bus_unregister():
    bus = EventBus()
    called = []

    def handler(event):
        called.append(event)

    bus.register("unreg.*", handler)
    await bus.emit("unreg.test", {})
    assert len(called) == 1

    bus.unregister("unreg.*", handler)
    await bus.emit("unreg.test", {})
    assert len(called) == 1  # nie powinien się zwiększyć


def test_event_bus_init_exports():
    """Events __init__ powinien eksportować kluczowe klasy"""
    from fasthub_core.events import Event, EventBus, event_bus
    assert Event is not None
    assert EventBus is not None
    assert event_bus is not None
