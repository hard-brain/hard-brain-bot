from aiohttp import ClientSession


async def request(method: str, url: str, session: ClientSession = ClientSession(), params: dict | None = None) -> dict:
    try:
        if not params:
            params = {}
        async with session.request(method, url, params=params) as response:
            return await response.json()
    finally:
        await session.close()


async def get(url: str, session: ClientSession = ClientSession(), params: dict | None = None) -> dict:
    return await request("GET", url, session, params)


async def post(url: str, session: ClientSession = ClientSession(), params: dict | None = None) -> dict:
    return await request("POST", url, session, params)


async def put(url: str, session: ClientSession = ClientSession(), params: dict | None = None) -> dict:
    return await request("PUT", url, session, params)


async def delete(url: str, session: ClientSession = ClientSession(), params: dict | None = None) -> dict:
    return await request("DELETE", url, session, params)
