import traceback
import aiohttp
from abc import ABC, abstractmethod
from typing import Generic, Optional, Tuple, Iterable

from aiohttp import ClientResponse, ClientError
from http import HTTPStatus

from .cache import Cache
from .typedefs import KT, VT
from .session import SessionPool


class FetchError(Exception):
    pass


class OSFetchError(FetchError, OSError):
    pass


class WebFetchError(FetchError, ClientError):
    pass


class NoSessionLeftError(FetchError, IndexError):
    pass


class Client(ABC, Generic[KT, VT]):
    @abstractmethod
    async def fetch(self, key: KT) -> VT:
        """
        Raises FetchError
        :param key:
        :return:
        """


class CrawlerClient(Client, ABC, Generic[KT, VT]):
    @abstractmethod
    async def fetch(self, key: KT) -> Tuple[Iterable[KT], VT]:
        pass


class CacheClient(Client[str, VT]):
    def __init__(self, client: Client[str, VT], cache: Cache[str, VT]):
        self._client = client
        self._cache = cache

    async def fetch(self, key: str) -> Optional[VT]:
        try:
            value = self._cache.get(key)
        except LookupError:
            value = await self._client.fetch(key)

        try:
            self._cache.set(key, value)
        except OSError:
            raise OSFetchError(f"Cannot set key '{key}' to cache")
        return value


class CacheOnlyClient(Client[str, VT]):
    def __init__(self, client: Client[str, VT], cache: Cache[str, VT]):
        self._client = client
        self._cache = cache

    async def fetch(self, key: str) -> VT:
        try:
            return self._cache.get(key)
        except LookupError:
            raise FetchError(f"Key '{key}' does not exist")


class CacheSkipClient(Client[str, VT]):
    def __init__(self, client: Client[str, VT], cache: Cache[str, VT]):
        self._client = client
        self._cache = cache

    async def fetch(self, key: str) -> VT:
        try:
            self._cache.get(key)
            raise FetchError(f"Key {key} exists")
        except LookupError:
            pass

        value = await self._client.fetch(key)
        try:
            self._cache.set(key, value)
        except OSError:
            raise OSFetchError(f"Cannot set key '{key}' to cache")

        return value


class WebClient(Client[str, ClientResponse]):
    def __init__(self, session_pool: SessionPool):
        self._session_pool = session_pool

    async def fetch(self, key: str) -> ClientResponse:
        try:
            proxy, session = self._session_pool.rand()
        except IndexError:
            raise NoSessionLeftError()

        try:
            response: aiohttp.ClientResponse = await session.get(key, proxy=proxy)
            await response.read()
            return response
        except (aiohttp.ClientHttpProxyError, aiohttp.ClientProxyConnectionError):
            if proxy is not None:
                self._session_pool.pop(proxy)
            raise WebFetchError()
        except aiohttp.ClientError:
            raise WebFetchError()


class WebTextClient(Client[str, str]):
    def __init__(self, session_pool: SessionPool):
        self._session_pool = session_pool

    async def fetch(self, key: str) -> str:
        client = WebClient(self._session_pool)
        response = await client.fetch(key)
        return await response.text()


class WebByteClient(Client[str, bytes]):
    def __init__(self, session_pool: SessionPool):
        self._session_pool = session_pool

    async def fetch(self, key: str) -> Optional[bytes]:
        client = WebClient(self._session_pool)
        response = await client.fetch(key)
        # noinspection PyProtectedMember
        return response._body


class RetryClient(Client[KT, VT]):
    def __init__(self, client: Client[KT, VT], retry_count: int):
        if retry_count <= 0:
            raise ValueError("retry_count must be greater than zero")
        self._retry_count = retry_count
        self._client = client

    async def fetch(self, key: KT) -> VT:
        for _ in range(self._retry_count - 1):
            try:
                return await self._client.fetch(key)
            except FetchError:
                pass
        return await self._client.fetch(key)


class ImageClient(Client[str, bytes]):
    def __init__(self, session_pool: SessionPool):
        self._session_pool = session_pool

    async def fetch(self, key: str) -> Optional[bytes]:
        client = WebClient(self._session_pool)
        response = await client.fetch(key)
        if response.status != HTTPStatus.OK:
            raise WebFetchError("HTTP status is not 200 ")

        content_type = response.headers.get('content-type')

        if content_type and isinstance(content_type, str) and content_type.startswith('image'):
            # noinspection PyProtectedMember
            return response._body

        raise WebFetchError(f"Invalid content type {content_type}")


class FakeClient(Client[str, str]):
    async def fetch(self, key: str) -> str:
        return key
