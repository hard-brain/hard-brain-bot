import os

import dotenv

from client import HardBrain
from hard_brain_bot.utils import setup_logging


if __name__ == "__main__":
    bot = HardBrain(debug=True)
    bot.load_extension("cogs.quiz_commands")

    @bot.event
    async def on_ready():
        print(f"Logged in as {bot.user} (ID: {bot.user.id})")

    dotenv.load_dotenv("../.env")
    setup_logging(
        "disnake",
        os.path.abspath("../discord.log"),
        "%(asctime)s:%(levelname)s:%(name)s: %(message)s",
    )
    bot.run(os.getenv("DISCORD_TOKEN"))
