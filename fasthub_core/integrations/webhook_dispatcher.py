"""
Wysylanie webhookow do skonfigurowanych endpointow organizacji.

Uzycie:
    from fasthub_core.integrations.webhook_dispatcher import dispatch_webhook

    await dispatch_webhook(
        db=db,
        organization_id=org_id,
        event_type="form_submission",
        payload={"form_id": "abc", "data": {"name": "Jan"}},
    )
"""

import hashlib
import hmac
import json
import logging
from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from fasthub_core.integrations.webhook_config import WebhookDelivery, WebhookEndpoint

logger = logging.getLogger(__name__)

MAX_CONSECUTIVE_FAILURES = 10


class WebhookDispatcher:
    """Dispatches webhooks to configured organization endpoints."""

    async def dispatch(
        self,
        db: AsyncSession,
        organization_id: UUID,
        event_type: str,
        payload: dict,
    ):
        """Wyslij webhook do wszystkich aktywnych endpointow organizacji."""
        endpoints = await self._get_matching_endpoints(db, organization_id, event_type)

        for endpoint in endpoints:
            webhook_payload = {
                "event": event_type,
                "timestamp": datetime.utcnow().isoformat(),
                "organization_id": str(organization_id),
                "data": payload,
            }

            payload_str = json.dumps(webhook_payload, default=str)
            signature = self._sign_payload(payload_str, endpoint.secret)

            await self._send(endpoint, webhook_payload, signature, db)

    async def _get_matching_endpoints(
        self,
        db: AsyncSession,
        organization_id: UUID,
        event_type: str,
    ) -> List[WebhookEndpoint]:
        """Get active endpoints matching the event type."""
        result = await db.execute(
            select(WebhookEndpoint).where(
                WebhookEndpoint.organization_id == organization_id,
                WebhookEndpoint.is_active == True,
            )
        )
        endpoints = list(result.scalars().all())
        return [e for e in endpoints if event_type in (e.events or [])]

    @staticmethod
    def _sign_payload(payload: str, secret: str) -> str:
        """HMAC-SHA256 signature."""
        return hmac.new(
            secret.encode(), payload.encode(), hashlib.sha256
        ).hexdigest()

    async def _send(
        self,
        endpoint: WebhookEndpoint,
        payload: dict,
        signature: str,
        db: AsyncSession,
    ):
        """POST na endpoint.url z payload. Timeout 10s."""
        import time

        start = time.monotonic()
        status_code = None
        response_body = None
        success = False
        error = None

        try:
            import httpx

            headers = {
                "Content-Type": "application/json",
                "X-Webhook-Signature": f"sha256={signature}",
                "X-Webhook-Event": payload.get("event", ""),
            }

            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(
                    endpoint.url,
                    json=payload,
                    headers=headers,
                )
                status_code = resp.status_code
                response_body = resp.text[:1000] if resp.text else None
                success = 200 <= resp.status_code < 300

        except Exception as e:
            error = str(e)
            logger.error(f"Webhook delivery failed for {endpoint.url}: {e}")

        elapsed_ms = int((time.monotonic() - start) * 1000)

        # Log delivery
        delivery = WebhookDelivery(
            endpoint_id=endpoint.id,
            event_type=payload.get("event", ""),
            payload=payload,
            status_code=status_code,
            response_body=response_body,
            response_time_ms=elapsed_ms,
            success=success,
            error=error,
        )
        db.add(delivery)

        # Update endpoint status
        endpoint.last_triggered_at = datetime.utcnow()
        endpoint.last_status_code = status_code

        if success:
            endpoint.consecutive_failures = 0
        else:
            endpoint.consecutive_failures = (endpoint.consecutive_failures or 0) + 1
            if endpoint.consecutive_failures >= MAX_CONSECUTIVE_FAILURES:
                endpoint.is_active = False
                logger.warning(
                    f"Webhook {endpoint.id} auto-disabled after "
                    f"{MAX_CONSECUTIVE_FAILURES} consecutive failures"
                )

        await db.flush()

    async def send_test(
        self,
        endpoint: WebhookEndpoint,
        db: AsyncSession,
    ) -> dict:
        """Send test webhook and return result."""
        test_payload = {
            "event": "test",
            "timestamp": datetime.utcnow().isoformat(),
            "organization_id": str(endpoint.organization_id),
            "data": {"test": True},
        }
        payload_str = json.dumps(test_payload, default=str)
        signature = self._sign_payload(payload_str, endpoint.secret)

        import time
        start = time.monotonic()

        try:
            import httpx

            headers = {
                "Content-Type": "application/json",
                "X-Webhook-Signature": f"sha256={signature}",
                "X-Webhook-Event": "test",
            }

            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(
                    endpoint.url, json=test_payload, headers=headers
                )
                elapsed_ms = int((time.monotonic() - start) * 1000)
                success = 200 <= resp.status_code < 300
                return {
                    "success": success,
                    "status_code": resp.status_code,
                    "response_time_ms": elapsed_ms,
                }

        except Exception as e:
            elapsed_ms = int((time.monotonic() - start) * 1000)
            return {
                "success": False,
                "status_code": None,
                "response_time_ms": elapsed_ms,
                "error": str(e),
            }


async def dispatch_webhook(
    db: AsyncSession,
    organization_id: UUID,
    event_type: str,
    payload: dict,
):
    """Convenience function for dispatching webhooks."""
    dispatcher = WebhookDispatcher()
    await dispatcher.dispatch(db, organization_id, event_type, payload)
