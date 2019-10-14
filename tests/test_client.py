from typing import Optional

import pytest
from aiohttp import ClientResponse

from aioscrapy import SingleSessionPool

from aioscrapy.cache import FakeCache
from aioscrapy.client import Client, FakeClient, CacheClient, RetryClient, CacheOnlyClient, CacheSkipClient, WebClient, \
    WebTextClient, WebByteClient


class ForRetryClient(Client[str, str]):
    def __init__(self, try_count: int):
        self._try_count = try_count
        self._tries = dict()

    async def fetch(self, key: str) -> Optional[str]:
        if key not in self._tries:
            self._tries[key] = 0
        self._tries[key] += 1

        if self._tries[key] == self._try_count:
            return key
        return None


@pytest.mark.asyncio
async def test_fake_client():
    client = FakeClient()
    key = 'key'
    assert await client.fetch(key) == key


@pytest.mark.asyncio
async def test_cache_client():
    client = CacheClient(
        FakeClient(),
        FakeCache()
    )

    key = 'key'
    assert await client.fetch(key) == key
    assert await client.fetch(key) == key


@pytest.mark.asyncio
async def test_cache_only_client():
    cache = FakeCache()
    fake_client = FakeClient()
    key = 'key'
    client = CacheOnlyClient(
        FakeClient(),
        cache
    )

    assert await client.fetch(key) is None
    cache.set(key, await fake_client.fetch(key))
    assert await client.fetch(key) == key


@pytest.mark.asyncio
async def test_cache_skip_client():
    client = CacheSkipClient(
        FakeClient(),
        FakeCache()
    )

    key = 'key'
    assert await client.fetch(key) == key
    assert await client.fetch(key) is None


@pytest.mark.asyncio
async def test_for_retry_client():
    for_retry_client = ForRetryClient(3)
    key = 'key'
    assert await for_retry_client.fetch(key) is None
    assert await for_retry_client.fetch(key) is None
    assert await for_retry_client.fetch(key) is key


@pytest.mark.asyncio
async def test_retry_client_not_enough_tries():
    client = RetryClient(
        ForRetryClient(4),
        3
    )
    key = 'key'
    assert await client.fetch(key) is None


@pytest.mark.asyncio
async def test_retry_client_enough_tries():
    client = RetryClient(
        ForRetryClient(4),
        4
    )
    key = 'key'
    assert await client.fetch(key) is key


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
