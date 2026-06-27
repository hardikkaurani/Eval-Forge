from redis.asyncio import ConnectionPool, Redis
import structlog

logger = structlog.get_logger()


class RedisManager:
    """Manages Redis connection pooling and health checks.

    Provides a clean interface for initializing, checking health of, and
    closing Redis connections in the application.
    """

    def __init__(self) -> None:
        self.pool: ConnectionPool | None = None
        self.client: Redis | None = None

    def init(self, url: str) -> None:
        """Initializes the Redis connection pool and client.

        Args:
            url: The Redis connection URL.
        """
        logger.info("Initializing Redis connection pool", url=url)
        self.pool = ConnectionPool.from_url(
            url,
            encoding="utf-8",
            decode_responses=True,
            max_connections=50,
        )
        self.client = Redis(connection_pool=self.pool)

    async def close(self) -> None:
        """Gracefully disconnects and shuts down the connection pool."""
        if self.client:
            logger.info("Closing Redis client connection")
        if self.pool:
            logger.info("Disconnecting Redis connection pool")
            await self.pool.disconnect()
            self.pool = None
            self.client = None

    async def ping(self) -> bool:
        """Pings the Redis server to verify connectivity.

        Returns:
            bool: True if connection is alive, False otherwise.
        """
        if not self.client:
            logger.warning("Redis client not initialized")
            return False
        try:
            return await self.client.ping()
        except Exception as e:
            logger.error("Redis health check failed", error=str(e))
            return False

    def get_client(self) -> Redis:
        """Returns the Redis client instance.

        Raises:
            RuntimeError: If the client is not initialized.
        """
        if not self.client:
            raise RuntimeError("Redis client is not initialized.")
        return self.client


redis_manager = RedisManager()
