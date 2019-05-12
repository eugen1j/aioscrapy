import aiohttp
import random
import abc
from typing import Dict, Collection, Optional
from .typedefs import Proxy, Session


class ProxyPool:
    def __init__(self, proxies: Collection[Proxy]):
        self._proxies = set(proxies)

    def rand(self) -> Optional[Proxy]:
        if len(self._proxies) == 0:
            return None
        return random.sample(self._proxies, 1)[0]

    def pop(self, proxy: str) -> None:
        if proxy in self._proxies:
            self._proxies.remove(proxy)


class SessionPool(abc.ABC):
    @abc.abstractmethod
    def rand(self) -> Session:
        pass

    @abc.abstractmethod
    def pop(self, key: Optional[Proxy]) -> None:
        pass


class ProxySessionPool(SessionPool):
    def __init__(self, proxy_pool: ProxyPool, size: int, session_kwargs: dict = None):
        self._size = size
        self._proxy_pool = proxy_pool
        if session_kwargs is None:
            session_kwargs = {}
        self._session_kwargs = session_kwargs
        self._session_pool: Dict[Proxy, aiohttp.ClientSession] = {}
        for _ in range(self._size):
            self._add_session()

    def rand(self) -> Session:
        if len(self._session_pool) == 0:
            raise IndexError('No sessions left')
        return random.choice(list(self._session_pool.items()))

    def pop(self, proxy: Proxy) -> None:
        if proxy in self._session_pool:
            self._session_pool.pop(proxy)
            self._add_session()

    def _add_session(self) -> None:
        proxy = self._proxy_pool.rand()
        if proxy is not None:
            self._session_pool[proxy] = aiohttp.ClientSession(**self._session_kwargs)
            self._proxy_pool.pop(proxy)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        for session in self._session_pool.values():
            await session.close()


class SingleSessionPool(SessionPool):
    def __init__(self, session_kwargs: dict = None):
        if session_kwargs is None:
            session_kwargs = {}
        self.session = (None, aiohttp.ClientSession(**session_kwargs))

    def rand(self) -> Session:
        return self.session

    def pop(self, key: Optional[Proxy]) -> None:
        pass
