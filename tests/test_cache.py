from aioscrapy.cache import FileCache, FakeCache


def test_file_cache(tmpdir: str):
    key = 'key'
    fake_key = 'fake_key'
    value = [1, 2, 3]
    cache = FileCache(tmpdir)
    cache.set(key, value)
    assert cache.get(key) == value
    assert cache.get(fake_key) is None


def test_fake_cache():
    key = 'key'
    fake_key = 'fake_key'
    value = [1, 2, 3]
    cache = FakeCache()
    cache.set(key, value)
    assert cache.get(key) == value
    assert cache.get(fake_key) is None
