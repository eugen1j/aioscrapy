import aiohttp
import random
import abc
from typing import Dict, Iterable
from .typedefs import Proxy, Session


class ProxyPool:
    def __init__(self, proxies: Iterable[Proxy]):
        self._proxies = set(proxies)

    def rand(self) -> Proxy:
        """
        Raises IndexError on empty pool
        """
        try:
            return random.sample(self._proxies, 1)[0]
        except ValueError:
            raise IndexError("No proxies left")

    def pop(self, proxy: str) -> None:
        if proxy in self._proxies:
            self._proxies.remove(proxy)


class SessionPool(abc.ABC):
    @abc.abstractmethod
    def rand(self) -> Session:
        """
        Raises IndexError on empty pool
        """

    @abc.abstractmethod
    def pop(self, key: Proxy) -> None:
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
        try:
            return random.choice(list(self._session_pool.items()))
        except IndexError:
            raise IndexError('No sessions left')

    def pop(self, key: Proxy) -> None:
        if key in self._session_pool:
            self._session_pool.pop(key)
            self._add_session()

    def _add_session(self) -> None:
        try:
            proxy = self._proxy_pool.rand()
            session_kwargs = self._session_kwargs
            if proxy in self._cookies:
                session_kwargs["cookies"] = self._cookies[proxy]
            self._session_pool[proxy] = aiohttp.ClientSession(**session_kwargs)
            self._proxy_pool.pop(proxy)
        except IndexError:
            pass

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

    def pop(self, key: Proxy) -> None:
        """
        Keeps session
        """
