import asyncio

from aioscrapy.typedefs import KT, VT, Proxy, Session

import pytest
from aiohttp import ClientResponse

from aioscrapy import SingleSessionPool, SessionPool, ProxySessionPool, ProxyPool

from aioscrapy.cache import MemoryCache, Cache
from aioscrapy.client import Client, FakeClient, CacheClient, RetryClient, CacheOnlyClient, CacheSkipClient, \
    WebClient, WebTextClient, WebByteClient, ImageClient, FetchError, WebFetchError, NoSessionLeftError


class ForRetryClient(Client[str, str]):
    def __init__(self, try_count: int):
        self._try_count = try_count
        self._tries = dict()

    async def fetch(self, key: str) -> str:
        if key not in self._tries:
            self._tries[key] = 0
        self._tries[key] += 1

        if self._tries[key] == self._try_count:
            return key
        raise FetchError()



class BrokenCache(Cache[KT, VT]):
    def get(self, key: KT) -> VT:
        raise LookupError()

    def set(self, key: KT, val: VT):
        raise OSError()


@pytest.mark.asyncio
async def test_broken_cache():
    cache = BrokenCache()
    key = 'key'
    value = 'value'
    with pytest.raises(LookupError):
        cache.get(key)
    with pytest.raises(OSError):
        cache.set(key, value)
    with pytest.raises(LookupError):
        cache.get(key)


class EmptySessionPool(SessionPool):
    def rand(self) -> Session:
        raise IndexError()

    def pop(self, key: Proxy) -> None:
        """
        """


@pytest.mark.asyncio
async def test_empty_session_pool():
    pool = EmptySessionPool()
    with pytest.raises(IndexError):
        pool.rand()


@pytest.mark.asyncio
async def test_fake_client():
    client = FakeClient()
    key = 'key'
    assert await client.fetch(key) == key


@pytest.mark.asyncio
async def test_cache_client():
    client = CacheClient(
        FakeClient(),
        MemoryCache()
    )

    key = 'key'
    assert await client.fetch(key) == key
    assert await client.fetch(key) == key


@pytest.mark.asyncio
async def test_cache_only_client():
    cache = MemoryCache()
    fake_client = FakeClient()
    key = 'key'
    client = CacheOnlyClient(
        FakeClient(),
        cache
    )

    with pytest.raises(FetchError):
        await client.fetch(key)
    cache.set(key, await fake_client.fetch(key))
    assert await client.fetch(key) == key


@pytest.mark.asyncio
async def test_cache_skip_client():
    client = CacheSkipClient(
        FakeClient(),
        MemoryCache()
    )

    key = 'key'
    assert await client.fetch(key) == key
    with pytest.raises(FetchError):
        await client.fetch(key)


@pytest.mark.asyncio
async def test_cache_skip_client_broken_cache():
    client = CacheSkipClient(
        FakeClient(),
        MemoryCache()
    )

    key = 'key'
    assert await client.fetch(key) == key
    with pytest.raises(FetchError):
        await client.fetch(key)


@pytest.mark.asyncio
async def test_for_retry_client():
    client = ForRetryClient(3)
    key = 'key'
    with pytest.raises(FetchError):
        await client.fetch(key)
    with pytest.raises(FetchError):
        await client.fetch(key)

    assert await client.fetch(key) is key


@pytest.mark.asyncio
async def test_retry_client_zero_tries():
    with pytest.raises(ValueError):
        RetryClient(FakeClient(), 0)


@pytest.mark.asyncio
async def test_retry_client_not_enough_tries():
    client = RetryClient(
        ForRetryClient(4),
        3
    )
    key = 'key'
    with pytest.raises(FetchError):
        await client.fetch(key)


@pytest.mark.asyncio
async def test_retry_client_enough_tries():
    client = RetryClient(
        ForRetryClient(4),
        4
    )
    key = 'key'
    assert await client.fetch(key) is key


@pytest.mark.asyncio
async def test_web_client_no_proxy_left():
    client = WebClient(EmptySessionPool())
    with pytest.raises(NoSessionLeftError):
        await client.fetch('https://google.com')


@pytest.mark.asyncio
async def test_web_client_bad_proxy():
    client = WebClient(ProxySessionPool(
        ProxyPool(['http://127.0.0.1:13337']), 1
    ))
    with pytest.raises(WebFetchError):
        await client.fetch('https://google.com')
    with pytest.raises(NoSessionLeftError):
        await client.fetch('https://google.com')


@pytest.mark.asyncio
async def test_web_client_bad_host():
    client = WebClient(SingleSessionPool())

    with pytest.raises(WebFetchError):
        await client.fetch('!@#$%^&*(')


@pytest.mark.asyncio
async def test_web_client_fetch_google():
    client = WebClient(SingleSessionPool())
    response = await client.fetch('https://google.com')
    assert isinstance(response, ClientResponse)


@pytest.mark.asyncio
async def test_web_client_fetch_google():
    client = WebClient(SingleSessionPool())
    response = await client.fetch('https://google.com')
    assert isinstance(response, ClientResponse)


@pytest.mark.asyncio
async def test_web_text_client_fetch_google():
    client = WebTextClient(SingleSessionPool())
    response = await client.fetch('https://google.com')
    assert isinstance(response, str)


@pytest.mark.asyncio
async def test_web_byte_client_fetch_google():
    client = WebByteClient(SingleSessionPool())
    response = await client.fetch('https://google.com')
    assert isinstance(response, bytes)


@pytest.mark.asyncio
async def test_image_client_fetch_google():
    client = ImageClient(SingleSessionPool())
    with pytest.raises(WebFetchError):
        assert await client.fetch('https://google.com') is None
    with pytest.raises(WebFetchError):
        assert await client.fetch('https://google.com/dwqdqwdqwdqwdwdqwwd') is None
    assert isinstance(await client.fetch('https://google.com/favicon.ico'), bytes)
