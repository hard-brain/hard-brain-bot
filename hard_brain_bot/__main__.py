import io

import disnake
from disnake import FFmpegPCMAudio
import dotenv
import os
from aiohttp import ClientSession

from client import HardBrain
from hard_brain_bot.utils import setup_logging, http_requests

bot = HardBrain()


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} (ID: {bot.user.id})')


@bot.command()
async def question(message: disnake.Message):
    if message.author.id == bot.user.id:
        return

    # check user is in voice channel
    if not (connected := message.author.voice):
        return await message.channel.send("Error: you are not connected to a voice channel")

    async with ClientSession() as session:
        question_response = await http_requests.request_json("GET", "http://localhost:8000/question", session)
        song_id = question_response[0]['song_id']
        song_response = await http_requests.request_bytes("GET", f"http://localhost:8000/audio/{song_id}", session)

    song_bytes = io.BytesIO(song_response)  # todo: make this close once no longer needed
    stream = FFmpegPCMAudio(song_bytes, pipe=True)
    voice = disnake.utils.get(bot.voice_clients, guild=message.guild)
    if voice and voice.is_connected:
        await voice.move_to(connected.channel)
    else:
        voice = await connected.channel.connect()
    voice.play(stream)
    await message.channel.send(f"Now playing in {connected.channel}")


# todo: wtf is a cog lmao
@bot.slash_command(description="say hello")
async def hello(ctx):
    await ctx.response.send_message("Hello")


@bot.slash_command(description="Starts a quiz")
async def start_quiz(ctx):
    connection = await http_requests.get("localhost:8000/question", params={"no_of_rounds": 3})
    await ctx.response.send_message(str(connection))


if __name__ == '__main__':
    dotenv.load_dotenv("../.env")
    setup_logging('disnake', os.path.abspath('../discord.log'), '%(asctime)s:%(levelname)s:%(name)s: %(message)s')
    bot.run(os.getenv("DISCORD_TOKEN"))
