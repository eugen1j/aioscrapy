"""
aiohttp.ClientSession wrappers
"""

import random
import abc
from typing import Dict, Iterable
import aiohttp
from .typedefs import Proxy, Session


class ProxyPool:
    """
    Proxy pool.
    """

    def __init__(self, proxies: Iterable[Proxy]):
        self._proxies = set(proxies)

    def rand(self) -> Proxy:
        """
        Returns random Proxy.

        Raises IndexError on empty pool.
        :return:
        """
        try:
            return random.sample(self._proxies, 1)[0]
        except ValueError:
            raise IndexError("No proxies left")

    def pop(self, proxy: str) -> None:
        """
        Remove proxy from pool if proxy exists.
        :param proxy:
        :return:
        """
        if proxy in self._proxies:
            self._proxies.remove(proxy)


class SessionPool(abc.ABC):
    """
    Session pool.
    """

    @abc.abstractmethod
    def rand(self) -> Session:
        """
        Returns random Session.

        Raises IndexError on empty pool.
        """

    @abc.abstractmethod
    def pop(self, key: Proxy) -> None:
        """
        Remove Session for Proxy.

        Usually used in case of proxy ban.
        """


class ProxySessionPool(SessionPool):
    """
    ProxySessionPool
    """

    def __init__(self, proxy_pool: ProxyPool, size: int,
                 session_kwargs: dict = None, cookies: dict = None):
        self._size = size
        self._proxy_pool = proxy_pool
        self._session_kwargs = session_kwargs or {}
        self._cookies = cookies or {}
        self._session_pool: Dict[Proxy, aiohttp.ClientSession] = {}
        for _ in range(self._size):
            self._add_session()

    def rand(self) -> Session:
        """

        :return:
        """
        try:
            return random.choice(list(self._session_pool.items()))
        except IndexError:
            raise IndexError('No sessions left')

    def pop(self, key: Proxy) -> None:
        """

        :param key:
        :return:
        """
        if key in self._session_pool:
            self._session_pool.pop(key)
            self._add_session()

    def _add_session(self) -> None:
        """

        :return:
        """
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
    """
    One Session without Proxy.
    """

    def __init__(self, session_kwargs: dict = None):
        if session_kwargs is None:
            session_kwargs = {}
        self.session = (None, aiohttp.ClientSession(**session_kwargs))

    def rand(self) -> Session:
        """
        Returns Session
        :return:
        """
        return self.session

    def pop(self, key: Proxy) -> None:
        """
        Keeps session.
        """
