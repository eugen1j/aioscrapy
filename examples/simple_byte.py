import asyncio

from aioscrapy import Client, WebByteClient, SingleSessionPool, Dispatcher, SimpleWorker


class CustomClient(Client[str, bytes]):
    def __init__(self, client: WebByteClient):
        self._client = client

    async def fetch(self, key: str) -> bytes:
        data = await self._client.fetch(key)
        return data


async def main():
    pool = SingleSessionPool()
    dispatcher = Dispatcher(['https://httpbin.org/image'])
    client = CustomClient(WebByteClient(pool))
    worker = SimpleWorker(dispatcher, client)

    result = await worker.run()
    return result

loop = asyncio.get_event_loop()
data: dict = loop.run_until_complete(main())
for url, byte_content in data.items():
    print(url + ": " + str(len(byte_content)) + " bytes")
