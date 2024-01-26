import disnake
import dotenv
import os

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
    connection = await http_requests.get("http://localhost:8000/question")
    await message.channel.send(str(connection))


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
