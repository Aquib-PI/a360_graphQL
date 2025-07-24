from collections import defaultdict
from typing import Callable, Iterable, Any, Dict, Optional
import asyncio

class DataLoader:
    """
    A simple DataLoader for batching and caching keys to values.

    Example:
        def batch_load_fn(keys: List[int]) -> Dict[int, User]:
            # perform one SQL query: SELECT * FROM user WHERE id IN (:keys)
            return {u.id: u for u in users}

        loader = DataLoader(batch_load_fn)
        user = await loader.load(123)
    """
    def __init__(self, batch_load_fn: Callable[[Iterable[Any]], Dict[Any, Any]]):
        self.batch_load_fn = batch_load_fn
        self._cache: Dict[Any, Any] = {}
        self._queue: Optional[asyncio.Future] = None
        self._keys: list = []

    async def load(self, key: Any) -> Any:
        # Return from cache if available
        if key in self._cache:
            return self._cache[key]

        # Queue up the key
        if self._queue is None:
            loop = asyncio.get_event_loop()
            self._queue = loop.create_future()
            # Schedule dispatch on next loop iteration
            loop.call_soon(self._dispatch)

        self._keys.append(key)
        await self._queue
        return self._cache.get(key)

    def _dispatch(self):
        # Called in event loop to batch load
        keys = list(set(self._keys))
        self._keys.clear()

        try:
            results = self.batch_load_fn(keys)
        except Exception as exc:
            # Fail all pending
            self._queue.set_exception(exc)
            self._queue = None
            return

        # Populate cache and resolve
        for k, v in results.items():
            self._cache[k] = v
        self._queue.set_result(True)
        self._queue = None

    def clear(self, key: Any):
        """Clears a specific key from the cache."""
        self._cache.pop(key, None)

    def clear_all(self):
        """Clears the entire cache."""
        self._cache.clear() 