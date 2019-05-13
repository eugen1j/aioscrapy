from aioscrapy.worker import Dispatcher


def test_dispatcher():
    dispatcher = Dispatcher([])
    assert dispatcher.empty() is True
    key1, key2, key3, error_key = 'key1', 'key2', 'key3', 'error_key'

    dispatcher.add(key1)
    assert dispatcher.empty() is False

    key = dispatcher.get()
    assert key == key1
    dispatcher.ack(key)
    assert dispatcher.empty() is True

    dispatcher.add(key2)
    dispatcher.add(key3)

    keys = {dispatcher.get(), dispatcher.get()}
    assert keys == {key2, key3}
    assert dispatcher.empty() is False
    dispatcher.ack(error_key)
    dispatcher.ack(key2)
    assert dispatcher.empty() is False
    dispatcher.ack(key3)
    assert dispatcher.empty() is True


def test_simple_worker():
    dispatcher = Dispatcher([])

