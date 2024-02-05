import io
import logging

import disnake
from aiohttp import ClientSession
from disnake import FFmpegPCMAudio, VoiceClient
from disnake.ext import commands
from disnake.ext.commands import CommandInvokeError

from hard_brain_bot.client import HardBrain
from hard_brain_bot.utils import http_requests
from hard_brain_bot.dataclazzes.requests import SongData
from hard_brain_bot.message_templates import embeds


class QuizCommands(commands.Cog):
    def __init__(self, bot: HardBrain) -> None:
        self.bot = bot
        self.round_in_progress = False
        self.current_round: SongData | None = None
        self.voice: VoiceClient | None = None

    @commands.Cog.listener()
    async def on_message(self, ctx: disnake.Message) -> None:
        if not self.round_in_progress or ctx.author == self.bot.user.id:
            return
        if self.current_round.is_correct_answer(ctx.content):
            embed = embeds.embed_song_data(
                "Correct answer",
                self.current_round,
                thumbnail=self.bot.user.display_avatar,
            )
            await ctx.channel.send(embed=embed)
            self.round_in_progress = False
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
        embed = embeds.embed_song_data("Example song data embed", fixture, thumbnail=self.bot.user.display_avatar)
        await ctx.response.send_message(embed=embed)

    @commands.slash_command(description="Starts a quiz")
    async def start_quiz(self, ctx: disnake.ApplicationCommandInteraction) -> None:
        # check user is in voice channel
        if not (connected := ctx.author.voice):
            await ctx.response.send_message(
                "Error: you are not connected to a voice channel"
            )
            return
        if self.round_in_progress:
            await ctx.response.send_message("A round is already in progress!")
            return
        try:
            async with ClientSession() as session:
                question_response = await http_requests.request_json(
                    "GET", "http://localhost:8000/question", session
                )
                self.current_round = SongData(**question_response[0])
                audio_response = await http_requests.request_bytes(
                    "GET",
                    f"http://localhost:8000/audio/{self.current_round.song_id}",
                    session,
                )
        except CommandInvokeError as e:
            logging.error(e)
            await ctx.response.send_message(
                f"Error occurred while fetching song response..."
            )
            return

        await ctx.response.send_message(f"Quiz starting in #{connected.channel}!")
        self.round_in_progress = True
        song_bytes = io.BytesIO(audio_response)
        stream = FFmpegPCMAudio(song_bytes, pipe=True)
        self.voice = await connected.channel.connect()
        self.voice.play(stream)


def setup(bot: HardBrain) -> None:
    bot.add_cog(QuizCommands(bot))
