import io
import logging

import disnake
from aiohttp import ClientSession
from disnake import FFmpegPCMAudio, VoiceClient
from disnake.ext import commands
from disnake.ext.commands import CommandInvokeError

from hard_brain_bot.client import HardBrain
from hard_brain_bot.utils import http_requests


class QuizCommands(commands.Cog):
    def __init__(self, bot: HardBrain):
        self.bot = bot
        self.round_in_progress = False
        self.current_round: dict | None = None
        self.voice: VoiceClient | None = None

    @commands.Cog.listener()
    async def on_message(self, ctx: disnake.Message):
        if not self.round_in_progress or ctx.author == self.bot.user.id:
            return
        answer = set(map(lambda s: s.lower(), (self.current_round["title"], *self.current_round["alt_titles"])))
        if ctx.content.lower() in answer:
            await ctx.channel.send(f"Correct! The answer was {self.current_round['title']}")
            self.round_in_progress = False
            await self.voice.disconnect()
            self.voice.cleanup()

    @commands.slash_command(description="Starts a quiz")
    async def start_quiz(self, ctx):
        # check user is in voice channel
        if not (connected := ctx.author.voice):
            await ctx.channel.send("Error: you are not connected to a voice channel")
            return
        try:
            async with ClientSession() as session:
                question_response = await http_requests.request_json(
                    "GET", "http://localhost:8000/question", session
                )
                self.current_round = question_response[0]
                song_id = self.current_round["song_id"]
                audio_response = await http_requests.request_bytes(
                    "GET", f"http://localhost:8000/audio/{song_id}", session
                )
        except CommandInvokeError as e:
            logging.error(e)
            await ctx.channel.send(f"Error occurred while fetching song response...")
            return

        await ctx.channel.send(f"Quiz starting in #{connected.channel}!")
        self.round_in_progress = True
        song_bytes = io.BytesIO(audio_response)
        stream = FFmpegPCMAudio(song_bytes, pipe=True)
        self.voice = await connected.channel.connect()
        self.voice.play(stream)


def setup(bot: HardBrain):
    bot.add_cog(QuizCommands(bot))
