import pytest

from fastapi_constance.services.database_sync import ConstanceConfigDatabaseSyncService


@pytest.mark.asyncio
class TestConstanceConfigDatabaseSyncService:
    """
    Test suite for the ConstanceConfigDatabaseSyncService class.

    Verifies correct syncing of configuration values between the database
    and cache layers, ensuring proper async behavior and type handling.
    """

    async def test_sync_sets_all_config_values_in_cache(self, mock_cache, mock_db_session):
        """
        Test that `sync()` correctly sets configuration values in the cache.

        Ensures that for each key-value pair in the configuration dictionary,
        the cache.set() method is awaited with the expected arguments.
        """

        service = ConstanceConfigDatabaseSyncService(database_session=mock_db_session)
        config = {
            "DEBUG": {"value": "True", "type": bool},
            "TIMEOUT": {"value": "15", "type": int},
        }

        await service.sync(config=config, cache=mock_cache)

        mock_cache.set.assert_any_await("DEBUG", "True")
        mock_cache.set.assert_any_await("TIMEOUT", "15")
        assert mock_cache.set.await_count == 2

    async def test_sync_empty_config(self, mock_cache, mock_db_session):
        """
        Test that `sync()` does not attempt to set any values when the config is empty.

        Ensures no unnecessary cache operations occur when an empty dictionary
        is passed to the sync method.
        """

        service = ConstanceConfigDatabaseSyncService(database_session=mock_db_session)
        await service.sync(config={}, cache=mock_cache)
        mock_cache.set.assert_not_awaited()

    async def test_sync_type_casting(self, mock_cache, mock_db_session):
        """
        Test that `sync()` handles type casting correctly before storing values in the cache.

        Although type casting is internal, this test verifies that the correct
        keys and values are passed to cache.set(), maintaining expected behavior.
        """

        service = ConstanceConfigDatabaseSyncService(database_session=mock_db_session)
        config = {
            "ENABLED": {"value": "False", "type": bool},
            "RETRIES": {"value": "3", "type": int},
        }

        await service.sync(config=config, cache=mock_cache)

        mock_cache.set.assert_any_await("ENABLED", "False")
        mock_cache.set.assert_any_await("RETRIES", "3")
