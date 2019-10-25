import os

import pytest

from aioscrapy.cache import FileCache, MemoryCache


def test_file_cache(tmpdir: str):
    key = 'key'
    fake_key = 'fake_key'
    value = [1, 2, 3]
    cache = FileCache(tmpdir)
    cache.set(key, value)
    assert cache.get(key) == value
    with pytest.raises(LookupError):
        cache.get(fake_key)


def test_file_cache_wrong_dir(tmpdir: str):
    key = 'key'
    value = [1, 2, 3]
    os.chmod(tmpdir, 0o400)
    cache = FileCache(tmpdir)
    with pytest.raises(OSError):
        cache.set(key, value)


def test_memory_cache():
    key = 'key'
    fake_key = 'fake_key'
    value = [1, 2, 3]
    cache = MemoryCache()
    cache.set(key, value)
    assert cache.get(key) == value
    with pytest.raises(LookupError):
        cache.get(fake_key)
