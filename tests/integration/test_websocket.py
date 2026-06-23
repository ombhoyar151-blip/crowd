import pytest


@pytest.mark.skip(reason="Requires running server with WebSocket support")
class TestWebSocket:
    async def test_ws_connect_valid_token(self):
        pass

    async def test_ws_connect_invalid_token(self):
        pass

    async def test_ws_receives_broadcast(self):
        pass
