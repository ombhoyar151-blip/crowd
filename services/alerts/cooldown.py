import time


class CooldownStore:
    """
    Alert cooldown gate.

    Uses Redis when available; falls back to an in-memory dict (per-process)
    when a NullRedis stub is passed (i.e. no Redis configured).
    """

    def __init__(self, redis_client, cooldown_seconds: int):
        self._redis = redis_client
        self._cooldown_seconds = cooldown_seconds
        # In-memory fallback: key -> expiry timestamp
        self._mem: dict[str, float] = {}

    def _key(self, camera_id: str, zone_id: str) -> str:
        return f"alert_cooldown:{camera_id}:{zone_id}"

    async def is_cooling(self, camera_id: str, zone_id: str) -> bool:
        key = self._key(camera_id, zone_id)
        try:
            exists = await self._redis.exists(key)
            return bool(exists)
        except Exception:
            # Fallback: check in-memory
            exp = self._mem.get(key)
            if exp is None:
                return False
            if time.time() > exp:
                del self._mem[key]
                return False
            return True

    async def set(self, camera_id: str, zone_id: str) -> None:
        key = self._key(camera_id, zone_id)
        try:
            await self._redis.set(key, str(time.time()), ex=self._cooldown_seconds)
        except Exception:
            pass
        # Always set in-memory as well (covers NullRedis case)
        self._mem[key] = time.time() + self._cooldown_seconds

    async def clear(self, camera_id: str, zone_id: str) -> None:
        key = self._key(camera_id, zone_id)
        try:
            await self._redis.delete(key)
        except Exception:
            pass
        self._mem.pop(key, None)
