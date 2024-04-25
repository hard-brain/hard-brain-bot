from typing import Literal
from aiohttp import ClientSession


async def request_json(
    method: Literal["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    url: str,
    session: ClientSession,
    params: dict | None = None,
) -> dict:
    if not params:
        params = {}
    async with session.request(method, url, params=params) as response:
        return await response.json(content_type=None)


async def request_bytes(
    method: Literal["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    url: str,
    session: ClientSession,
    params: dict | None = None,
) -> bytes:
    if not params:
        params = {}
    async with session.request(method, url, params=params) as response:
        return await response.read()
