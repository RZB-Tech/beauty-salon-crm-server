import asyncio
from collections.abc import Callable, Coroutine
from typing import TypeVar

T = TypeVar("T")

def run_async(coro: Callable[[], Coroutine[None, None, T]]) -> T:
    return asyncio.run(coro())  # creates a fresh event loop each time