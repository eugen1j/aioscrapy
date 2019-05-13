import asyncio
from abc import ABC, abstractmethod
from typing import Generic, List, Dict, Iterable, Optional, Set, Tuple

from .client import Client
from .typedefs import KT, VT


class Dispatcher(Generic[KT]):
    def __init__(self, state: Iterable[KT]):
        self._done: Set[KT] = set()
        self._new: List[KT] = list(set(state))
        self._all: Set[KT] = set(state)

    def add(self, key: KT):
        if key not in self._all:
            self._all.add(key)
            self._new.append(key)

    def ack(self, key: KT):
        if key in self._all and key not in self._done:
            self._done.add(key)

    def get(self) -> Optional[KT]:
        if len(self._new) != 0:
            return self._new.pop()

    def empty(self) -> bool:
        return len(self._done) == len(self._all)


class Worker(ABC, Generic[KT, VT]):
    @abstractmethod
    async def run(self) -> Dict[KT, VT]:
        pass


class Master(Generic[KT, VT]):
    def __init__(self, workers: List[Worker[KT, VT]]):
        self._workers = workers

    async def run(self) -> Dict[KT, VT]:
        result = {}
        worker_results = await asyncio.gather(*[
            worker.run() for worker in self._workers
        ])
        for worker_result in worker_results:
            result.update(worker_result)
        return result


class CrawlerWorker(Worker[KT, VT]):
    def __init__(self, dispatcher: Dispatcher[KT], client: Client[KT, VT]):
        self._dispatcher = dispatcher
        self._client = client

    async def run(self) -> Dict[KT, VT]:
        results: Dict[KT, VT] = {}
        while not self._dispatcher.empty():
            key = self._dispatcher.get()
            if key:
                result = await self._client.fetch(key)
                if result is not None:
                    new_keys, value = result
                    for new_key in new_keys:
                        self._dispatcher.add(new_key)
                    results[key] = value
                self._dispatcher.ack(key)
            else:
                await asyncio.sleep(1)
        return results


class SimpleWorker(Worker[KT, VT]):
    def __init__(self, dispatcher: Dispatcher[KT], client: Client[KT, VT]):
        self._dispatcher = dispatcher
        self._client = client

    async def run(self) -> Dict[KT, VT]:
        results: Dict[KT, VT] = {}
        while not self._dispatcher.empty():
            key = self._dispatcher.get()
            if key:
                result = await self._client.fetch(key)
                if result is not None:
                    results[key] = result
                self._dispatcher.ack(key)
            else:
                await asyncio.sleep(1)
        return results
