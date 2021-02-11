"""
Type definition
"""

from typing import TypeVar, Optional, Tuple
import aiohttp

KT = TypeVar('KT')
VT = TypeVar('VT')
Proxy = str
Session = Tuple[Optional[Proxy], aiohttp.ClientSession]
