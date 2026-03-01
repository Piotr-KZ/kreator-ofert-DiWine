"""
Request ID Middleware — kazdy request dostaje UUID.

Jak to dziala:
1. Request przychodzi -> middleware generuje UUID4
2. UUID zapisywany w request.state.request_id
3. UUID dodawany do response header X-Request-ID
4. UUID dostepny w logach, audit trail, error reporting

Uzycie:
    from fasthub_core.middleware.request_id import RequestIDMiddleware
    app.add_middleware(RequestIDMiddleware)

    # W endpoincie:
    request_id = request.state.request_id
"""

import uuid

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class RequestIDMiddleware(BaseHTTPMiddleware):
    """
    Middleware dodajacy unique request ID.

    Parametry:
        header_name: nazwa headera (domyslnie X-Request-ID)
        trust_client: jesli True, akceptuje X-Request-ID od klienta
                      (przydatne gdy za load balancerem)
    """

    def __init__(self, app, header_name: str = "X-Request-ID", trust_client: bool = False):
        super().__init__(app)
        self.header_name = header_name
        self.trust_client = trust_client

    async def dispatch(self, request: Request, call_next) -> Response:
        # Generuj lub uzyj istniejacy request ID
        request_id = None
        if self.trust_client:
            request_id = request.headers.get(self.header_name)

        if not request_id:
            request_id = str(uuid.uuid4())

        # Zapisz w request.state (dostepne w endpointach)
        request.state.request_id = request_id

        # Wykonaj request
        response = await call_next(request)

        # Dodaj do response header
        response.headers[self.header_name] = request_id

        return response
