import hashlib
import os
import abc
import pickle
from typing import Generic, Optional
from .typedefs import VT, KT


class Cache(abc.ABC, Generic[KT, VT]):
    @abc.abstractmethod
    def get(self, key: KT) -> Optional[VT]:
        pass

    @abc.abstractmethod
    def set(self, key: KT, val: VT) -> None:
        pass


class FileCache(Cache[str, VT]):
    def __init__(self, folder: str):
        self._folder = folder

    def get(self, key: str) -> Optional[VT]:
        path = self._full_path(key)
        try:
            with open(path, 'rb') as file:
                return pickle.load(file)
        except FileNotFoundError:
            return None

    def set(self, key: str, val: VT) -> None:
        path = self._full_path(key)
        directory = os.path.dirname(path)
        if not os.path.exists(directory):
            os.makedirs(directory)
        with open(path, 'wb') as file:
            pickle.dump(val, file, pickle.HIGHEST_PROTOCOL)

    def _full_path(self, key: str) -> str:
        md5 = hashlib.md5(key.encode()).hexdigest()
        return os.path.join(self._folder, md5[:2], md5)


class FakeCache(Cache[KT, VT]):
    def __init__(self):
        self._cache = {}

    def get(self, key: KT) -> Optional[VT]:
        return self._cache.get(key, None)

    def set(self, key: KT, val: VT) -> None:
        self._cache[key] = val
