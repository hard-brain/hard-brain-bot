import os

import dotenv

from client import HardBrain
from hard_brain_bot.utils import setup_logging

bot = HardBrain()
bot.load_extension("cogs.quiz_commands")


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")


# todo: get answers from messages and give them to some quiz manager thingy idk
# @bot.event
# async def on_message(ctx):
#     if not question_data:
#         return
#     if (
#         ctx.content == question_data[0]["title"]
#     ) or ctx.content in question_data[0]["alt_titles"]:
#         ctx.response.send_message(f"Correct! The song was {question_data[0]['title']}")


if __name__ == "__main__":
    dotenv.load_dotenv("../.env")
    setup_logging(
        "disnake",
        os.path.abspath("../discord.log"),
        "%(asctime)s:%(levelname)s:%(name)s: %(message)s",
    )
    bot.run(os.getenv("DISCORD_TOKEN"))
