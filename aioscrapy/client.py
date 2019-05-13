import traceback
import aiohttp
from abc import ABC, abstractmethod
from typing import Generic, Optional

from .cache import Cache
from .typedefs import KT, VT
from .session import SessionPool


class Client(ABC, Generic[KT, VT]):
    @abstractmethod
    async def fetch(self, key: KT) -> Optional[VT]:
        pass


class CacheClient(Client[str, VT]):
    def __init__(self, client: Client[str, VT], cache: Cache[str, VT]):
        self._client = client
        self._cache = cache

    async def fetch(self, key: str) -> Optional[VT]:
        cache_value = self._cache.get(key)
        if cache_value is not None:
            return cache_value
        else:
            new_value = await self._client.fetch(key)
            if new_value is not None:
                self._cache.set(key, new_value)
            return new_value


class WebClient(Client[str, bytes]):
    def __init__(self, session_pool: SessionPool):
        self._session_pool = session_pool

    async def fetch(self, url: str) -> Optional[bytes]:
        # noinspection PyBroadException
        proxy, session = self._session_pool.rand()
        try:
            response: aiohttp.ClientResponse = await session.get(url, proxy=proxy)
            data = await response.read()
            return data
        except (aiohttp.ClientHttpProxyError, aiohttp.ClientProxyConnectionError):
            if proxy is not None:
                self._session_pool.pop(proxy)
            return None
        except aiohttp.ClientError:
            print(traceback.format_exc())
            return None


class RetryClient(Client[KT, VT]):
    def __init__(self, client: Client, retry_count: int):
        self._retry_count = retry_count
        self._client = client

    async def fetch(self, key: KT) -> Optional[VT]:
        for i in range(self._retry_count):
            result = await self._client.fetch(key)
            if result is not None:
                return result
        return None


class FakeClient(Client[str, str]):
    async def fetch(self, key: str) -> str:
        return key
