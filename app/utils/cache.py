from aiocache import SimpleMemoryCache


class AppInMemoryCache:
    """
    Singleton class representing an in-memory cache for the application.

    This class provides methods for setting, getting, and deleting key-value pairs in the cache.

    Note:
        This class follows the Singleton design pattern to ensure that only one instance
        of the cache is created throughout the application.

    Attributes:
        _instance: The singleton instance of the cache.
        cache: The underlying cache implementation.

    """

    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            # Initialize the cache instance here
            cls._instance.cache = SimpleMemoryCache()
        return cls._instance

    async def set(self, key: str, value, ttl: int = 3600):
        """
        Sets a key-value pair in the cache with an optional time-to-live (TTL).

        Args:
            key (str): The key for the cache entry.
            value: The value to be stored in the cache.
            ttl (int, optional): The time-to-live (in seconds) for the cache entry. Defaults to 3600.

        """
        await self.cache.set(key=key, value=value, ttl=ttl)  # type: ignore[attr-defined]

    async def get(self, key):
        """
        Retrieves the value associated with the given key from the cache.

        Args:
            key: The key to retrieve the value for.

        Returns:
            The value associated with the key, or None if the key is not found in the cache.

        """
        return await self.cache.get(key=key)

    async def delete(self, key):
        """
        Deletes the entry associated with the given key from the cache.

        Args:
            key: The key of the entry to delete.

        Returns:
            bool: True if the entry was successfully deleted, False otherwise.

        """
        return await self.cache.delete(key=key)


cache = AppInMemoryCache()
