"""
Null/no-op Redis stub used when Redis is not available (e.g., memory:// broker).
All operations are no-ops or return safe defaults.
"""
import time


class NullRedis:
    """Drop-in replacement for redis.asyncio.Redis when Redis is not configured."""

    async def exists(self, key: str) -> int:
        return 0

    async def set(self, key: str, value, ex: int = None) -> None:
        pass

    async def delete(self, key: str) -> None:
        pass

    async def publish(self, channel: str, message: str) -> None:
        pass

    async def aclose(self) -> None:
        pass

    def pubsub(self):
        return _NullPubSub()


class _NullPubSub:
    async def psubscribe(self, *args, **kwargs):
        pass

    async def unsubscribe(self, *args, **kwargs):
        pass

    async def listen(self):
        """Async iterable that never produces real messages.

        The real redis client's `pubsub.listen()` returns an async iterator.
        For the NullPubSub we provide an async generator that yields periodic
        noop messages so callers using `async for` won't raise a TypeError.
        """
        import asyncio
        while True:
            # sleep for a long time to avoid busy loops, then yield a noop
            await asyncio.sleep(3600)
            yield {"type": "noop", "data": ""}
