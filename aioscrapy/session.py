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
        """ """

    @abc.abstractmethod
    def pop(self, key: Optional[Proxy]) -> None:
        """ """


class ProxySessionPool(SessionPool):
    def __init__(self, proxy_pool: ProxyPool, size: int, session_kwargs: dict = None, cookies: dict = None):
        self._size = size
        self._proxy_pool = proxy_pool
        self._session_kwargs = session_kwargs or {}
        self._cookies = cookies or {}
        self._session_pool: Dict[Proxy, aiohttp.ClientSession] = {}
        for _ in range(self._size):
            self._add_session()

    def rand(self) -> Session:
        if len(self._session_pool) == 0:
            raise IndexError('No sessions left')
        return random.choice(list(self._session_pool.items()))

    def pop(self, key: Optional[Proxy]) -> None:
        if key in self._session_pool:
            self._session_pool.pop(key)
            self._add_session()

    def _add_session(self) -> None:
        proxy = self._proxy_pool.rand()
        if proxy is not None:
            session_kwargs = self._session_kwargs
            if proxy in self._cookies:
                session_kwargs["cookies"] = self._cookies[proxy]
            self._session_pool[proxy] = aiohttp.ClientSession(**session_kwargs)
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
