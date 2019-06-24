import asyncio
import json

from aioscrapy import Client, WebTextClient, SingleSessionPool, Dispatcher, SimpleWorker


class CustomClient(Client[str, dict]):
    def __init__(self, client: WebTextClient):
        self._client = client

    async def fetch(self, key: str) -> dict:
        data = await self._client.fetch(key)
        return json.loads(data)


async def main():
    pool = SingleSessionPool()
    dispatcher = Dispatcher(['https://httpbin.org/get'])
    client = CustomClient(WebTextClient(pool))
    worker = SimpleWorker(dispatcher, client)

    result = await worker.run()
    return result

loop = asyncio.get_event_loop()
print(loop.run_until_complete(main()))
