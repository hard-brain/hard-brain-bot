import disnake
import io
import platform
import logging
from aiohttp import ClientError

from disnake import FFmpegPCMAudio, ApplicationCommandInteraction

from hard_brain_bot.data_models.requests import SongData
from hard_brain_bot.utils.async_helpers import AsyncTimer, CancellableTask
from hard_brain_bot.services.hard_brain_service import HardBrainService
from hard_brain_bot.message_templates.embeds import embed_song_data


class QuizService:
    def __init__(
        self,
        ctx: ApplicationCommandInteraction,
        backend: HardBrainService,
        song_data_list: list[SongData],
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
        self.song_data_list = song_data_list
        self.round_channel = ctx.channel
        self.voice_channel = ctx.author.voice.channel
        self._game_in_progress = False
        self._current_round = 0
        self._round_timer: AsyncTimer | None = None
        self._voice: disnake.VoiceClient | None = None
        self._game: CancellableTask | None = None

    async def start_game(self, ctx: ApplicationCommandInteraction):
        logging.info(
            f"Starting new game with {len(self.song_data_list)} questions in {self.voice_channel}"
        )

        async def _process_rounds():
            for song in self.song_data_list:
                await self._next_round(song.song_id)

        self._game = CancellableTask(_process_rounds)
        await self.end_game(ctx)

    async def _next_round(self, song_id: int):
        try:
            audio_response = await self.backend.get_audio(song_id)
        except ClientError as e:
            logging.error(f"Fetching audio for song id {song_id} failed: {e}")
            self.round_channel.send_message(
                "An error occurred while loading the next song..."
            )
            await self._end_round()
            return
        song_bytes = io.BytesIO(audio_response)
        self._stream = FFmpegPCMAudio(song_bytes, pipe=True)
        self._voice = await self.voice_channel.connect()
        self._voice.play(self._stream)
        self._round_timer = AsyncTimer(self.round_time_limit, self._end_round)
        self._round_timer.start()
        await self._round_timer.timeout()

    async def _end_round(self):
        embed = embed_song_data(
            "Correct answer",
            self.song_data_list[self._current_round],
            # thumbnail=winner.display_avatar,  # todo: change thumbnail to the round winner's pfp (or HardBrainBot?)
        )
        await self.round_channel.send(embed=embed)
        if self._voice.is_playing():
            self._voice.stop()
        self._stream.cleanup()

    async def check_answer(self, answer: str):
        current_song = self.song_data_list[self._current_round]
        logging.debug(f"Checking answer {answer} for song id {current_song.song_id}")
        if current_song.is_correct_answer(answer):
            self._round_timer.cancel()
            await self._end_round()

    async def end_game(self, ctx: ApplicationCommandInteraction):
        logging.info(
            f"Ending game with {len(self.song_data_list)} questions in {self.voice_channel}"
        )
        self._round_timer.cancel()
        await self._end_round()
        await ctx.response.send_message("Game ending. Thank you for playing!")

        # clean up game stuff
        self._game_in_progress = False
        self._current_round = 0

        # clean up voice
        await self._voice.disconnect()
        self._voice.cleanup()

    async def skip_round(self, ctx: ApplicationCommandInteraction):
        logging.debug(
            f"Skipping round {self._current_round} out of {len(self.song_data_list)}..."
        )
        await ctx.response.send_message("Skipping round...")
        await self._end_round()

    def is_in_progress(self):
        return self._game_in_progress
