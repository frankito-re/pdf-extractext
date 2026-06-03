from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from presentation.main import app


@pytest.mark.asyncio
async def test_ping_server():
    with patch("presentation.main.get_database_connection", new_callable=AsyncMock):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            response = await ac.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "message": "pong"}
