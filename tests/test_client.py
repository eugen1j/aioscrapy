from typing import Optional

import pytest

from spider.cache import FakeCache
from spider.client import Client, FakeClient, CacheClient, RetryClient


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
    assert key == await client.fetch(key)


@pytest.mark.asyncio
async def test_cache_client():
    client = CacheClient(
        FakeClient(),
        FakeCache()
    )

    key = 'key'
    assert key == await client.fetch(key)
    assert key == await client.fetch(key)


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
async def test_retry_client_enough_tries():
    client = RetryClient(
        ForRetryClient(4),
        4
    )
    key = 'key'
    assert await client.fetch(key) is key
