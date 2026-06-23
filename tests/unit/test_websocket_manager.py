import asyncio

import pytest


class FakeWS:
    def __init__(self, name="test"):
        self.name = name

    async def accept(self):
        pass

    async def send_json(self, data):
        pass


@pytest.mark.asyncio
class TestWebSocketManager:
    async def test_connect_disconnect(self):
        from backend.services.websocket_manager import WebSocketManager

        ws = FakeWS("test")
        mgr = WebSocketManager()
        await mgr.connect(ws, "cam_1")
        assert "cam_1" in mgr._connections
        mgr.disconnect(ws, "cam_1")
        assert "cam_1" not in mgr._connections

    async def test_per_camera_isolation(self):
        from backend.services.websocket_manager import WebSocketManager

        ws_a = FakeWS("a")
        ws_b = FakeWS("b")
        mgr = WebSocketManager()
        await mgr.connect(ws_a, "cam_a")
        await mgr.connect(ws_b, "cam_b")

        assert len(mgr._connections.get("cam_a", set())) == 1
        assert len(mgr._connections.get("cam_b", set())) == 1

    async def test_broadcast_sends_to_all(self):
        from backend.services.websocket_manager import WebSocketManager

        received = []

        class TrackingWS(FakeWS):
            async def send_json(self, data):
                received.append(data)

        mgr = WebSocketManager()
        ws1 = TrackingWS("1")
        ws2 = TrackingWS("2")
        await mgr.connect(ws1, "cam_1")
        await mgr.connect(ws2, "cam_1")

        await mgr.broadcast("cam_1", {"msg": "hello"})
        assert len(received) == 2

    async def test_broadcast_stale_client(self):
        from backend.services.websocket_manager import WebSocketManager
        from fastapi import WebSocketDisconnect

        class StaleWS(FakeWS):
            async def send_json(self, data):
                raise WebSocketDisconnect()

        mgr = WebSocketManager()
        ws1 = FakeWS("1")
        ws2 = StaleWS("2")
        await mgr.connect(ws1, "cam_1")
        await mgr.connect(ws2, "cam_1")

        await mgr.broadcast("cam_1", {"msg": "test"})
        assert "cam_1" in mgr._connections
