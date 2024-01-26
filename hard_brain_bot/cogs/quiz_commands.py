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

    @commands.slash_command(description="say hello")
    async def hello(self, ctx: disnake.ApplicationCommandInteraction):
        await ctx.response.send_message("Hello")

    @commands.slash_command(description="Starts a quiz")
    async def start_quiz(self, ctx):
        if ctx.author.id == self.bot.user.id:
            return

        # check user is in voice channel
        if not (connected := ctx.author.voice):
            return await ctx.channel.send(
                "Error: you are not connected to a voice channel"
            )

        await ctx.channel.send(f"Quiz starting in #{connected.channel}!")

        try:
            async with ClientSession() as session:
                question_response = await http_requests.request_json(
                    "GET", "http://localhost:8000/question", session
                )
                song_id = question_response[0]["song_id"]
                audio_response = await http_requests.request_bytes(
                    "GET", f"http://localhost:8000/audio/{song_id}", session
                )
        except CommandInvokeError as e:
            logging.error(e)
            await ctx.channel.send(f"Error occurred while fetching song response...")
            return

        song_bytes = io.BytesIO(audio_response)
        stream = FFmpegPCMAudio(song_bytes, pipe=True)
        voice: VoiceClient = await connected.channel.connect()
        voice.play(stream)


def setup(bot: HardBrain):
    bot.add_cog(QuizCommands(bot))
