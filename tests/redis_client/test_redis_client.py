import ssl
from unittest.mock import MagicMock, patch

import pytest

from fastapi_constance.clients.redis import RedisClient


class TestRedisClient:
    """Test suite for RedisClient singleton and configuration behavior."""

    def test_get_client_returns_single_instance(self, monkeypatch):
        """Ensure get_client creates a single Redis instance."""

        mock_redis = MagicMock()
        monkeypatch.setenv("REDIS_URL", "redis://localhost:6379/0")
        monkeypatch.setenv("REDIS_DB", "0")

        with patch("fastapi_constance.clients.redis.redis.Redis.from_url", return_value=mock_redis) as mock_from_url:
            client1 = RedisClient.get_client()
            client2 = RedisClient.get_client()

        assert client1 is client2, "Should return same singleton instance"
        mock_from_url.assert_called_once_with("redis://localhost:6379/0", decode_responses=True, db=0)

    def test_get_client_reads_env_variables(self, monkeypatch):
        """Ensure environment variables are correctly read."""

        mock_redis = MagicMock()
        monkeypatch.setenv("REDIS_URL", "redis://testserver:6379/1")
        monkeypatch.setenv("REDIS_DB", "1")

        with patch("fastapi_constance.clients.redis.redis.Redis.from_url", return_value=mock_redis) as mock_from_url:
            client = RedisClient.get_client()

        assert client == mock_redis
        mock_from_url.assert_called_once()
        args, kwargs = mock_from_url.call_args
        assert kwargs["decode_responses"] is True
        assert kwargs["db"] == 1

    def test_get_client_missing_env_vars(self, monkeypatch):
        """Should raise error when REDIS_URL is missing."""

        monkeypatch.delenv("REDIS_URL", raising=False)
        monkeypatch.delenv("REDIS_DB", raising=False)

        with pytest.raises((TypeError, ValueError)):
            RedisClient.get_client()

    def test_get_client_invalid_db_value(self, monkeypatch):
        """Should raise ValueError if REDIS_DB is not integer."""

        monkeypatch.setenv("REDIS_URL", "redis://localhost")
        monkeypatch.setenv("REDIS_DB", "not_an_int")

        with pytest.raises(ValueError):
            RedisClient.get_client()

    def test_get_client_caches_instance(self, monkeypatch):
        """Subsequent calls should not recreate Redis client."""

        mock_redis = MagicMock()
        monkeypatch.setenv("REDIS_URL", "redis://localhost:6379/0")
        monkeypatch.setenv("REDIS_DB", "0")

        with patch("fastapi_constance.clients.redis.redis.Redis.from_url", return_value=mock_redis) as mock_from_url:
            RedisClient.get_client()
            RedisClient.get_client()
            RedisClient.get_client()

        assert mock_from_url.call_count == 1, "Redis.from_url should only be called once"

    def test_get_client_default_db_when_not_set(self, monkeypatch):
        """REDIS_DB defaults to 0 when not set."""

        mock_redis = MagicMock()
        monkeypatch.setenv("REDIS_URL", "redis://localhost:6379")
        monkeypatch.delenv("REDIS_DB", raising=False)

        with patch("fastapi_constance.clients.redis.redis.Redis.from_url", return_value=mock_redis) as mock_from_url:
            RedisClient.get_client()

        mock_from_url.assert_called_once_with("redis://localhost:6379", decode_responses=True, db=0)

    def test_get_client_managed_redis_ssl_cert_reqs_none(self, monkeypatch):
        """Managed Redis (e.g. AWS ElastiCache) can disable SSL cert verification via REDIS_SSL_CERT_REQS=none."""

        mock_redis = MagicMock()
        monkeypatch.setenv("REDIS_URL", "rediss://my-cluster.cache.amazonaws.com:6379")
        monkeypatch.setenv("REDIS_DB", "0")
        monkeypatch.setenv("REDIS_SSL_CERT_REQS", "none")

        with patch("fastapi_constance.clients.redis.redis.Redis.from_url", return_value=mock_redis) as mock_from_url:
            RedisClient.get_client()

        mock_from_url.assert_called_once()
        args, kwargs = mock_from_url.call_args
        assert kwargs["decode_responses"] is True
        assert kwargs["db"] == 0
        assert kwargs["ssl_cert_reqs"] is ssl.CERT_NONE
