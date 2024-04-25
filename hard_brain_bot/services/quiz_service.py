import asyncio

import disnake
import io
import platform
import logging

from disnake import FFmpegOpusAudio, ApplicationCommandInteraction

from hard_brain_bot.data_models.requests import SongData
from hard_brain_bot.utils.async_helpers import AsyncTimer
from hard_brain_bot.services.hard_brain_service import HardBrainService
from hard_brain_bot.services.scoring_service import ScoringService
from hard_brain_bot.message_templates.embeds import embed_song_data, embed_scores


def _process_song_data_from_props(song_data_list):
    song_data_map = map(lambda props: SongData(
        song_id=props["song_id"],
        filename=props["filename"],
        title=props["title"],
        alt_titles=props["alt_titles"].split(", "),
        genre=props["genre"],
        artist=props["artist"]), song_data_list)
    return list(song_data_map)


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
        self.song_data_list = _process_song_data_from_props(song_data_list)
        self.score_service = ScoringService()
        self.followup = ctx.followup
        self.voice_channel = ctx.author.voice.channel
        self._game_in_progress = False
        self._current_song: SongData | None = None
        self._round_timer: AsyncTimer | None = None
        self._voice: disnake.VoiceClient | None = None
        self._stream: FFmpegOpusAudio | None = None
        self._tasks: list = []

    async def _process_rounds(self):
        self._tasks = [self._next_round(song) for song in self.song_data_list]
        for task in self._tasks:
            await asyncio.create_task(task)

    async def start_game(self):
        logging.info(
            f"Starting new game with {len(self.song_data_list)} questions in {self.voice_channel}"
        )
        self._voice = await self.voice_channel.connect()
        self._game_in_progress = True
        await self._process_rounds()
        await self.end_game()

    async def _next_round(self, song: SongData):
        while self._voice.is_playing():
            await asyncio.sleep(0.05)
        try:
            audio_response = await self.backend.get_audio(song.song_id)
        except Exception as e:
            logging.error(f"Fetching audio for song id {song.song_id} failed: {e}")
            self.followup.send("An error occurred while loading the next song, skipping round")
            await self._end_round()
            return
        song_bytes = io.BytesIO(audio_response)
        self._current_song = song
        self._stream = FFmpegOpusAudio(song_bytes, pipe=True)
        self._voice.play(self._stream)
        self._round_timer = AsyncTimer(self.round_time_limit, self._end_round)
        self._round_timer.start()
        await self._round_timer.timeout()

    async def _end_round(self, ctx: disnake.Message | None = None):
        if self._current_song is not None:
            await self._send_end_of_round_embed(ctx)
        self._current_song = None
        await self._cleanup_voice()

    async def check_answer(self, ctx: disnake.Message):
        current_song = self._current_song
        if current_song is not None and current_song.is_correct_answer(ctx.content):
            logging.debug(
                f"Checking answer {ctx.content} for song id {current_song.song_id}"
            )
            self._round_timer.cancel()
            await self._end_round(ctx)

    async def end_game(self):
        logging.info(
            f"Ending game with {len(self.song_data_list)} questions in {self.voice_channel}"
        )
        if self._round_timer and not self._round_timer.is_executed():
            try:
                self._round_timer.cancel()
            except RuntimeWarning as e:
                logging.warning(e)
        await self.followup.send(
            embed=embed_scores(
                self.score_service.get_scores(),
                title="Game ending. Thank you for playing!",
            )
        )

        # clean up game stuff
        self._game_in_progress = False
        self._tasks = []

        # clean up voice
        await self._voice.disconnect()
        await self._cleanup_voice()

    async def skip_round(self):
        logging.info(f"Skipping round...")
        self._round_timer.cancel()
        await self._end_round()

    def current_scores(self):
        return self.score_service.get_scores()

    def is_in_progress(self):
        return self._game_in_progress

    async def _cleanup_voice(self):
        if self._voice and self._voice.is_playing():
            self._voice.stop()
        if isinstance(self._stream, FFmpegOpusAudio):
            self._stream.cleanup()

    async def _send_end_of_round_embed(self, ctx: disnake.Message):
        winner: disnake.Member | disnake.User | None = None
        points = 3
        if ctx:
            winner = ctx.author
            self.score_service.add_points(winner.display_name, points)
        winner_name = winner.display_name if winner else "No one"
        embed = embed_song_data(
            title=f"{winner_name} got the correct answer{'' if winner else '...'}",
            song_data=self._current_song,
            thumbnail=winner.display_avatar if winner else None,
        )
        if winner:
            embed.description = f"{points} points go to {winner.display_name}"
        await self.followup.send(embed=embed)
