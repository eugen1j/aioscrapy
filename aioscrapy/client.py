import traceback
import aiohttp
from abc import ABC, abstractmethod
from typing import Generic, Optional, Tuple, Iterable

from aiohttp import ClientResponse
from http import HTTPStatus

from .cache import Cache
from .typedefs import KT, VT
from .session import SessionPool


class Client(ABC, Generic[KT, VT]):
    @abstractmethod
    async def fetch(self, key: KT) -> Optional[VT]:
        pass


class CrawlerClient(Client, ABC, Generic[KT, VT]):
    @abstractmethod
    async def fetch(self, key: KT) -> Optional[Tuple[Iterable[KT], VT]]:
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


class CacheOnlyClient(Client[str, VT]):
    def __init__(self, client: Client[str, VT], cache: Cache[str, VT]):
        self._client = client
        self._cache = cache

    async def fetch(self, key: str) -> Optional[VT]:
        return self._cache.get(key)


class CacheSkipClient(Client[str, VT]):
    def __init__(self, client: Client[str, VT], cache: Cache[str, VT]):
        self._client = client
        self._cache = cache

    async def fetch(self, key: str) -> Optional[VT]:
        cache_value = self._cache.get(key)
        if cache_value is not None:
            return None
        else:
            new_value = await self._client.fetch(key)
            if new_value is not None:
                self._cache.set(key, new_value)
            return new_value


class WebClient(Client[str, ClientResponse]):
    def __init__(self, session_pool: SessionPool):
        self._session_pool = session_pool

    async def fetch(self, key: str) -> Optional[ClientResponse]:
        proxy, session = self._session_pool.rand()
        try:
            response: aiohttp.ClientResponse = await session.get(key, proxy=proxy)
            await response.read()
            return response
        except (aiohttp.ClientHttpProxyError, aiohttp.ClientProxyConnectionError):
            if proxy is not None:
                self._session_pool.pop(proxy)
            return None
        except aiohttp.ClientError:
            print(traceback.format_exc())
            return None


class WebTextClient(Client[str, str]):
    def __init__(self, session_pool: SessionPool):
        self._session_pool = session_pool

    async def fetch(self, key: str) -> Optional[str]:
        client = WebClient(self._session_pool)
        response = await client.fetch(key)
        if response is None:
            return None
        return await response.text()


class WebByteClient(Client[str, bytes]):
    def __init__(self, session_pool: SessionPool):
        self._session_pool = session_pool

    async def fetch(self, key: str) -> Optional[bytes]:
        client = WebClient(self._session_pool)
        response = await client.fetch(key)
        if response is None:
            return None
        # noinspection PyProtectedMember
        return response._body


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


class ImageClient(Client[str, bytes]):
    def __init__(self, session_pool: SessionPool):
        self._session_pool = session_pool

    async def fetch(self, key: str) -> Optional[bytes]:
        client = WebClient(self._session_pool)
        response = await client.fetch(key)
        if response is None:
            return None

        if response.status != HTTPStatus.OK:
            return None

        content_type = response.headers.get('content-type')
        if content_type and isinstance(content_type, str) and content_type.startswith('image'):
            await response.read()
            # noinspection PyProtectedMember
            return response._body

        return None


class FakeClient(Client[str, str]):
    async def fetch(self, key: str) -> str:
        return key
