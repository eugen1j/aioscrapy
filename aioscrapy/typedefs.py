import aiohttp
from typing import TypeVar, Optional, Tuple

KT = TypeVar('KT')
VT = TypeVar('VT')
Proxy = str
Session = Tuple[Optional[Proxy], aiohttp.ClientSession]
