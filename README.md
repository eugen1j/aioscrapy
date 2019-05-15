# Python async library for web scrapping

[![PyPI version](https://badge.fury.io/py/aioscrapy.svg)](https://badge.fury.io/py/aioscrapy)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://github.com/eugen1j/aioscrapy/blob/master/LICENSE)

[![Build Status](https://travis-ci.org/eugen1j/aioscrapy.svg?branch=master)](https://travis-ci.org/eugen1j/aioscrapy)
[![codecov](https://codecov.io/gh/eugen1j/aioscrapy/branch/master/graph/badge.svg)](https://codecov.io/gh/eugen1j/aioscrapy)
[![codebeat badge](https://codebeat.co/badges/c494c251-c554-4f61-be57-6ca484ae7ba9)](https://codebeat.co/projects/github-com-eugen1j-aioscrapy-master) 
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/54e3d1b41bed4c9fb62e25483d1fe1eb)](https://www.codacy.com/app/eugen1j/aioscrapy?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=eugen1j/aioscrapy&amp;utm_campaign=Badge_Grade)

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