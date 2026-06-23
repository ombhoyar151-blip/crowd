from datetime import datetime, timedelta, timezone

import pytest
from jose import JWTError, jwt


class TestAuth:
    def test_create_access_token(self):
        from backend.api.routers.auth import create_access_token

        token = create_access_token("testuser")
        assert token is not None
        assert isinstance(token, str)

    def test_verify_valid_token(self):
        from backend.api.routers.auth import create_access_token
        from config.settings import Settings

        token = create_access_token("testuser")
        settings = Settings()
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        assert payload["sub"] == "testuser"

    def test_verify_expired_token(self):
        from config.settings import Settings

        settings = Settings()
        expired = jwt.encode(
            {"sub": "user", "exp": datetime.now(timezone.utc) - timedelta(hours=1)},
            settings.jwt_secret_key,
            algorithm=settings.jwt_algorithm,
        )
        with pytest.raises(JWTError):
            jwt.decode(expired, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])

    def test_verify_wrong_secret(self):
        from backend.api.routers.auth import create_access_token
        from config.settings import Settings

        token = create_access_token("testuser")
        with pytest.raises(JWTError):
            jwt.decode(token, "wrong_secret", algorithms=[Settings().jwt_algorithm])

    def test_hash_and_verify_password(self):
        from backend.api.routers.auth import hash_password, verify_password

        hashed = hash_password("mypassword")
        assert verify_password("mypassword", hashed) is True
        assert verify_password("wrong", hashed) is False
