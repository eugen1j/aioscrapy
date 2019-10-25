"""
Data storage
"""

import hashlib
import os
import abc
import pickle
from typing import Generic
from .typedefs import VT, KT


class Cache(abc.ABC, Generic[KT, VT]):
    """
    Cache interface
    """

    @abc.abstractmethod
    def get(self, key: KT) -> VT:
        """
        Raises LookupError
        """

    @abc.abstractmethod
    def set(self, key: KT, val: VT) -> None:
        """
        Raises OSError
        """


class FileCache(Cache[str, VT]):
    """
    Store data into folder in following structure
    BASE_FOLDER/ab/abcdef1234567890abcdef1234567890
    where abcdef1234567890abcdef1234567890 is md5(key)
    """

    def __init__(self, folder: str):
        self._folder = folder

    def get(self, key: str) -> VT:
        """

        :param key:
        :return:
        """
        try:
            path = self._full_path(key)
            with open(path, 'rb') as file:
                return pickle.load(file)
        except OSError:
            raise LookupError

    def set(self, key: str, val: VT) -> None:
        """

        :param key:
        :param val:
        :return:
        """
        path = self._full_path(key)
        directory = os.path.dirname(path)
        if not os.path.exists(directory):
            os.makedirs(directory)
        with open(path, 'wb') as file:
            pickle.dump(val, file, pickle.HIGHEST_PROTOCOL)

    def _full_path(self, key: str) -> str:
        """

        :param key:
        :return:
        """
        md5 = hashlib.md5(key.encode()).hexdigest()
        return os.path.join(self._folder, md5[:2], md5)


class MemoryCache(Cache[KT, VT]):
    """
    Store data into dict
    """

    def __init__(self):
        self._cache = {}

    def get(self, key: KT) -> VT:
        """

        :param key:
        :return:
        """
        return self._cache[key]

    def set(self, key: KT, val: VT) -> None:
        """

        :param key:
        :param val:
        :return:
        """
        self._cache[key] = val
