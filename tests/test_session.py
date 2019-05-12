import aiohttp
import pytest

from spider.session import ProxyPool, ProxySessionPool, SingleSessionPool


def test_proxy_pool():
    proxy1, proxy2 = '127.0.0.1:8080', '127.0.0.2:8081'
    proxy_pool = ProxyPool([proxy1, proxy2])
    rand_proxy = proxy_pool.rand()
    assert rand_proxy == proxy1 or rand_proxy == proxy2
    proxy_pool.pop(proxy2)
    assert proxy_pool.rand() == proxy1
    proxy_pool.pop(proxy2)
    assert proxy_pool.rand() == proxy1
    proxy_pool.pop(proxy1)
    assert proxy_pool.rand() is None
    proxy_pool.pop(proxy1)
    assert proxy_pool.rand() is None


@pytest.mark.asyncio
async def test_proxy_session_pool():
    proxy1, proxy2, proxy3 = '127.0.0.1:8080', '127.0.0.2:8081', '127.0.0.3:8082'
    header_name, header_value = "x-test-header", "somevalue"
    async with ProxySessionPool(ProxyPool([proxy1, proxy2, proxy3]), 2, {
        'headers': {header_name: header_value}
    }) as pool:
        proxy, session = pool.rand()
        assert proxy in (proxy1, proxy2, proxy3)
        assert isinstance(session, aiohttp.ClientSession)
        # noinspection PyProtectedMember
        assert session._default_headers[header_name] == header_value

        pool.pop(proxy)

        proxy, session = pool.rand()
        assert proxy in (proxy1, proxy2, proxy3)
        assert isinstance(session, aiohttp.ClientSession)

        pool.pop(proxy)

        proxy, session = pool.rand()
        assert proxy in (proxy1, proxy2, proxy3)
        assert isinstance(session, aiohttp.ClientSession)

        pool.pop(proxy)
        with pytest.raises(IndexError):
            pool.rand()


@pytest.mark.asyncio
async def test_single_session_pool():
    header_name, header_value = "x-test-header", "somevalue"
    pool = SingleSessionPool({
        'headers': {header_name: header_value}
    })
    proxy, session = pool.rand()
    assert proxy is None
    assert isinstance(session, aiohttp.ClientSession)
    # noinspection PyProtectedMember
    assert session._default_headers[header_name] == header_value

    pool.pop(proxy)
    proxy, session = pool.rand()
    assert proxy is None
    assert isinstance(session, aiohttp.ClientSession)
