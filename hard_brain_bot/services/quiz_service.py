import disnake
import io
import platform
import logging
from aiohttp import ClientError
import asyncio

from disnake import FFmpegOpusAudio, ApplicationCommandInteraction

from hard_brain_bot.data_models.requests import SongData
from hard_brain_bot.utils.async_helpers import AsyncTimer
from hard_brain_bot.services.hard_brain_service import HardBrainService
from hard_brain_bot.message_templates.embeds import embed_song_data


class QuizService:
    def __init__(
        self,
        ctx: ApplicationCommandInteraction,
        backend: HardBrainService,
        song_data_list: list[dict],
        round_time_limit: float = 30.0,
    ):
        """
        The service that manages and drives the quiz game.
        :param ctx: The Discord interaction that triggered the start of a game.
        :param backend: Application HardBrainService instance.
        :param song_data_list: A list of SongData to use in the game.
        :param round_time_limit: Maximum round time in seconds.
        """
        self.round_time_limit = round_time_limit
        try:
            if platform.system() != "Windows" and not disnake.opus.is_loaded():
                disnake.opus.load_opus("libopusenc.so.0")
        except OSError:
            logging.error("Could not load the opus shared library")
        self.backend = backend
        self.song_data_list = list(map(lambda props: SongData(**props), song_data_list))
        self.followup = ctx.followup
        self.voice_channel = ctx.author.voice.channel
        self._game_in_progress = False
        self._current_round = 1
        self._current_song: SongData | None = None
        self._round_timer: AsyncTimer | None = None
        self._voice: disnake.VoiceClient | None = None
        self._stream: FFmpegOpusAudio | None = None
        self._queue = asyncio.Queue()

    async def _process_rounds(self):
        for song in self.song_data_list:
            print(song)
            await self._queue.put(self._next_round(song.song_id))  # todo: blocked on this

    async def start_game(self):
        logging.info(
            f"Starting new game with {len(self.song_data_list)} questions in {self.voice_channel}"
        )
        self._voice = await self.voice_channel.connect()
        self._game_in_progress = True
        await self._process_rounds()

    async def _next_round(self, song_id: int):
        try:
            audio_response = await self.backend.get_audio(song_id)
        except ClientError as e:
            logging.error(f"Fetching audio for song id {song_id} failed: {e}")
            self.followup.send("An error occurred while loading the next song...")
            await self._end_round()
            return
        song_bytes = io.BytesIO(audio_response)
        self._stream = FFmpegOpusAudio(song_bytes, pipe=True)
        self._voice.play(self._stream)
        self._round_timer = AsyncTimer(self.round_time_limit, self._end_round)
        self._round_timer.start()

    async def _end_round(self):
        embed = embed_song_data(
            "Correct answer",
            self.song_data_list[self._current_round],
            # thumbnail=winner.display_avatar,  # todo: change thumbnail to the round winner's pfp (or HardBrainBot?)
        )
        await self.followup.send(embed=embed)
        if self._voice and self._voice.is_playing():
            self._voice.stop()
        if isinstance(self._stream, FFmpegOpusAudio):
            self._stream.cleanup()
        self._current_round += 1

    async def check_answer(self, answer: str):
        current_song = self.song_data_list[self._current_round]
        logging.debug(f"Checking answer {answer} for song id {current_song.song_id}")
        if current_song.is_correct_answer(answer):
            self._round_timer.cancel()
            await self._end_round()

    async def end_game(self):
        logging.info(
            f"Ending game with {len(self.song_data_list)} questions in {self.voice_channel}"
        )
        if self._round_timer:
            self._round_timer.cancel()
        await self._end_round()
        await self.followup.send("Game ending. Thank you for playing!")

        # clean up game stuff
        self._game_in_progress = False
        self._current_round = 1

        # clean up voice
        if self._voice:
            await self._voice.disconnect()
            self._voice.cleanup()

    async def skip_round(self):
        logging.info(
            f"Skipping round {self._current_round} out of {len(self.song_data_list)}..."
        )
        await self.followup.send("Skipping round...")
        await self._end_round()

    def is_in_progress(self):
        return self._game_in_progress
