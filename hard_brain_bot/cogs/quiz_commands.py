import io
import logging
import platform
import threading

import disnake
from disnake import FFmpegPCMAudio, VoiceClient
from disnake.ext import commands
from disnake.ext.commands import CommandInvokeError

from hard_brain_bot.client import HardBrain
from hard_brain_bot.data_models.requests import SongData
from hard_brain_bot.message_templates import embeds
from hard_brain_bot.services.hard_brain_service import HardBrainService
from hard_brain_bot.utils.async_helpers import AsyncTimer


class QuizCommands(commands.Cog):
    def __init__(self, bot: HardBrain) -> None:
        self.bot = bot
        self.round_channel = None
        self.round_time_limit = 30.0
        self.round_timer: threading.Timer | None = None
        self.current_round: SongData | None = None
        self.voice: VoiceClient | None = None
        self.backend = HardBrainService()

    @commands.Cog.listener()
    async def on_message(self, ctx: disnake.Message) -> None:
        if not self.round_channel or ctx.author == self.bot.user.id:
            return
        if self.current_round.is_correct_answer(ctx.content):
            self.round_timer.cancel()
            await self._end_round()

    async def _end_round(self):
        embed = embeds.embed_song_data(
            "Correct answer",
            self.current_round,
            thumbnail=self.bot.user.display_avatar,
        )
        await self.round_channel.send(embed=embed)
        self.round_channel = None
        await self.voice.disconnect()
        self.voice.cleanup()

    @commands.slash_command(description="More information about Hard Brain")
    async def about(self, ctx: disnake.ApplicationCommandInteraction) -> None:
        embed = embeds.embed_about()
        await ctx.response.send_message(embed=embed)

    @commands.slash_command(description="Test command to fetch data for a random song")
    async def debug_song(self, ctx: disnake.ApplicationCommandInteraction) -> None:
        fixture = SongData(
            song_id=30999,
            filename="test.mp3",
            title="TEST!! がんばって！！",
            alt_titles=["test!!", "test ganbatte"],
            artist="DJ TEST",
            genre="testcore",
        )
        embed = embeds.embed_song_data(
            "Example song data embed", fixture, thumbnail=self.bot.user.display_avatar
        )
        await ctx.response.send_message(embed=embed)

    @commands.slash_command(description="Starts a quiz")
    async def start_quiz(self, ctx: disnake.ApplicationCommandInteraction) -> None:
        # check user is in voice channel
        if not (connected := ctx.author.voice):
            await ctx.response.send_message(
                "Error: you are not connected to a voice channel"
            )
            return
        if self.round_channel:
            await ctx.response.send_message("A round is already in progress!")
            return
        await ctx.response.defer()
        await ctx.edit_original_response("Please wait, preparing a quiz...")
        try:
            question_response = await self.backend.get_question()
            self.current_round = SongData(**question_response[0])
            audio_response = await self.backend.get_audio(self.current_round.song_id)
        except CommandInvokeError as e:
            logging.error(e)
            await ctx.edit_original_response(
                f"Error occurred while fetching song response..."
            )
            return

        await ctx.edit_original_response(
            f"Quiz starting in #{connected.channel}! "
            f"You have {int(self.round_time_limit)} seconds to answer the name of the song."
        )
        if platform.system() != "Windows":
            disnake.opus.load_opus("libopusenc.so.0")
        self.round_channel = ctx.channel
        song_bytes = io.BytesIO(audio_response)
        stream = FFmpegPCMAudio(song_bytes, pipe=True)
        self.voice = await connected.channel.connect()
        self.voice.play(stream)
        self.round_timer = AsyncTimer(self.round_time_limit, self._end_round)
        self.round_timer.start()


def setup(bot: HardBrain) -> None:
    bot.add_cog(QuizCommands(bot))
