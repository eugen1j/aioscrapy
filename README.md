# Python async library for web scrapping

[![Codacy Badge](https://api.codacy.com/project/badge/Grade/12f172cc84294a0388fed11c14a4ef44)](https://app.codacy.com/app/eugen1j/aioscrapy?utm_source=github.com&utm_medium=referral&utm_content=eugen1j/aioscrapy&utm_campaign=Badge_Grade_Dashboard)
[![Build Status](https://travis-ci.org/eugen1j/aioscrapy.svg?branch=master)](https://travis-ci.org/eugen1j/aioscrapy)  [![codecov](https://codecov.io/gh/eugen1j/aioscrapy/branch/master/graph/badge.svg)](https://codecov.io/gh/eugen1j/aioscrapy) [![PyPI version](https://badge.fury.io/py/aioscrapy.svg)](https://badge.fury.io/py/aioscrapy)

## Installing

    pip install aioscrapy

## Usage

```python
from aioscrapy import Client, WebClient, SingleSessionPool, Dispatcher, SimpleWorker

class CustomClient(Client[str, dict]):
    def __init__(self, client: WebClient):
        self._client = client
        
    async def fetch(self, key: str) -> dict:
        data = self._client.fetch(key)
        # Processing data, getting result 
        return {"result": "some_result"}
        
async def main():
    pool = SingleSessionPool()
    dispatcher = Dispatcher(['https://start-url.example.com'])
    client = CustomClient(WebClient(pool))
    worker = SimpleWorker(dispatcher, client)
    
    result = await worker.run()
    return result
```