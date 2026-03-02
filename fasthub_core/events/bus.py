"""
FastHub Core — Event Bus.

Pub/Sub z wildcard handlers + opcjonalny Redis broadcast.

Użycie:
    from fasthub_core.events.bus import event_bus

    @event_bus.on("user.*")
    async def handle_user_events(event):
        print(f"User event: {event['event_type']}")

    await event_bus.emit("user.login", {"user_id": "123"})
"""

import asyncio
import fnmatch
import inspect
import logging
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Tuple

logger = logging.getLogger("fasthub.events")


class Event:
    """Represents an event in the system."""

    def __init__(
        self,
        event_type: str,
        payload: Optional[Dict[str, Any]] = None,
        source: str = "system",
    ):
        self.event_type = event_type
        self.payload = payload or {}
        self.timestamp = datetime.utcnow().isoformat()
        self.source = source

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_type": self.event_type,
            "payload": self.payload,
            "timestamp": self.timestamp,
            "source": self.source,
        }

    def __repr__(self):
        return f"<Event {self.event_type} from {self.source}>"


class EventBus:
    """
    Event Bus singleton — local handlers + Redis pub/sub broadcast.

    Wildcard matching via fnmatch:
      - "user.*" matches "user.login", "user.created"
      - "*.error" matches "process.error", "billing.error"
      - "*" matches everything
    """

    def __init__(self):
        self._handlers: List[Tuple[str, Callable]] = []

    def on(self, event_pattern: str):
        """
        Decorator to register event handler.

        @event_bus.on("user.*")
        async def handle(event):
            ...
        """
        def decorator(handler: Callable):
            self.register(event_pattern, handler)
            return handler
        return decorator

    def register(self, pattern: str, handler: Callable):
        """Register a handler for an event pattern."""
        self._handlers.append((pattern, handler))
        logger.debug(f"Handler registered for pattern: {pattern}")

    def unregister(self, pattern: str, handler: Callable):
        """Remove a specific handler."""
        self._handlers = [
            (p, h) for p, h in self._handlers
            if not (p == pattern and h is handler)
        ]

    async def emit(
        self,
        event_type: str,
        payload: Optional[Dict[str, Any]] = None,
        source: str = "system",
    ) -> int:
        """
        Emit an event. Calls all matching local handlers + publishes to Redis.
        Returns number of handlers called.
        """
        event = Event(event_type, payload, source)
        event_dict = event.to_dict()

        # Call matching local handlers
        called = 0
        for pattern, handler in self._handlers:
            if fnmatch.fnmatch(event_type, pattern):
                try:
                    if inspect.iscoroutinefunction(handler):
                        await handler(event_dict)
                    else:
                        handler(event_dict)
                    called += 1
                except Exception as e:
                    logger.error(
                        f"Handler error for {event_type} (pattern={pattern}): {e}"
                    )

        # Broadcast to Redis (non-blocking, best-effort)
        try:
            from fasthub_core.infrastructure.redis import publish_event
            await publish_event(event_type, event_dict)
        except Exception:
            pass  # Redis unavailable — local-only mode

        logger.debug(f"Event {event_type}: {called} handlers called")
        return called

    async def emit_many(self, events: List[Tuple[str, Dict]]) -> int:
        """
        Emit multiple events. Returns total handlers called.
        events: list of (event_type, payload) tuples.
        """
        total = 0
        for event_type, payload in events:
            total += await self.emit(event_type, payload)
        return total

    def get_stats(self) -> Dict[str, Any]:
        """Get stats about registered handlers."""
        patterns = {}
        for pattern, _ in self._handlers:
            patterns[pattern] = patterns.get(pattern, 0) + 1
        return {
            "handlers_count": len(self._handlers),
            "patterns": patterns,
        }

    def clear_handlers(self):
        """Remove all handlers."""
        self._handlers.clear()


# === DEFAULT HANDLERS ===

async def _default_log_handler(event: Dict[str, Any]):
    """Log all system events at INFO level."""
    logger.info(f"Event: {event.get('event_type')} from {event.get('source')}")


# === SINGLETON ===

event_bus = EventBus()
event_bus.register("system.*", _default_log_handler)
