"""
worker module.
"""
import asyncio
from abc import ABC, abstractmethod
from typing import Generic, List, Dict, Iterable, Set

from .client import Client, CrawlerClient, FetchError
from .typedefs import KT, VT


class Dispatcher(Generic[KT]):
    """
    Handles tasks.
    """

    def __init__(self, state: Iterable[KT]):
        self._done: Set[KT] = set()
        self._new: List[KT] = list(set(state))
        self._all: Set[KT] = set(state)

    def add(self, key: KT):
        """

        :param key:
        :return:
        """
        if key not in self._all:
            self._all.add(key)
            self._new.append(key)

    def ack(self, key: KT):
        """

        :param key:
        :return:
        """
        if key in self._all and key not in self._done:
            self._done.add(key)

    def get(self) -> KT:
        """
        Raises IndexError if there are no tasks left.
        """
        return self._new.pop()

    def empty(self) -> bool:
        """

        :return:
        """
        return len(self._done) == len(self._all)


class Worker(ABC, Generic[KT, VT]):
    """
    Worker
    """

    @abstractmethod
    async def run(self) -> Dict[KT, VT]:
        """

        :return:
        """


class Master(Generic[KT, VT]):
    """
    Runs multiple Workers together
    """

    def __init__(self, workers: Iterable[Worker[KT, VT]]):
        self._workers = workers

    async def run(self) -> Dict[KT, VT]:
        """

        :return:
        """
        result: Dict[KT, VT] = {}
        worker_results = await asyncio.gather(*[
            worker.run() for worker in self._workers
        ])
        for worker_result in worker_results:
            result.update(worker_result)
        return result


class CrawlerWorker(Worker[KT, VT]):
    """
    CrawlerWorker
    """

    def __init__(self, dispatcher: Dispatcher[KT],
                 client: CrawlerClient[KT, VT]):
        self._dispatcher = dispatcher
        self._client = client

    async def run(self) -> Dict[KT, VT]:
        """

        :return:
        """
        results: Dict[KT, VT] = {}
        while not self._dispatcher.empty():
            try:
                key = self._dispatcher.get()
            except IndexError:
                await asyncio.sleep(0.05)
            else:
                try:
                    new_keys, result = await self._client.fetch(key)
                    for new_key in new_keys:
                        self._dispatcher.add(new_key)
                    results[key] = result
                except FetchError:
                    pass
                finally:
                    self._dispatcher.ack(key)

        return results


class SimpleWorker(Worker[KT, VT]):
    """
    SimpleWorker
    """

    def __init__(self, dispatcher: Dispatcher[KT], client: Client[KT, VT]):
        self._dispatcher = dispatcher
        self._client = client

    async def run(self) -> Dict[KT, VT]:
        """

        :return:
        """
        results: Dict[KT, VT] = {}
        while not self._dispatcher.empty():
            try:
                key = self._dispatcher.get()
            except IndexError:
                await asyncio.sleep(0.05)
            else:
                try:
                    results[key] = await self._client.fetch(key)
                    self._dispatcher.ack(key)
                except FetchError:
                    pass
                finally:
                    self._dispatcher.ack(key)

        return results
