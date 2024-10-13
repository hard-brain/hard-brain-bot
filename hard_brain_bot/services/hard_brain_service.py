import os
from aiohttp import ClientSession

from hard_brain_bot.utils import http_requests


class HardBrainService:
    def __init__(
        self, hostname: str | None = None, port: int = 8000, use_https: bool = False
    ):
        """
        A service that provides connections to the Hard Brain API.
        :param hostname: hostname of the location where Hard Brain API is hosted
        :param port: on which Hard Brain API is listening
        :param use_https: whether to use HTTP or HTTPS for requests
        """
        if not hostname:
            hostname = os.getenv("HARD_BRAIN_API_HOSTNAME")
        self.hostname = hostname if hostname else "localhost"
        self.port = port
        self.use_https = use_https
        self.url = self.__set_url()

    async def get_question(
        self, number_of_songs: int = 1, versions: str = ""
    ) -> dict | list[dict]:
        if number_of_songs <= 0:
            raise ValueError("Number of songs requested must be greater than 0")
        params = {"number_of_songs": number_of_songs}
        if versions != "":
            params["version_string"] = versions
        async with ClientSession() as session:
            if number_of_songs != 1:
                return await http_requests.request_json(
                    "GET", f"{self.url}/question", session, params=params
                )
            return await http_requests.request_json(
                "GET", f"{self.url}/question", session
            )

    async def get_audio(self, song_id: str) -> bytes:
        async with ClientSession() as session:
            return await http_requests.request_bytes(
                "GET",
                f"{self.url}/audio/{song_id}",
                session,
            )

    def __set_url(self) -> str:
        protocol = "https" if self.use_https else "http"
        return f"{protocol}://{self.hostname}:{self.port}"
