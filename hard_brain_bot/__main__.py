import os

from hard_brain_bot.client import HardBrain
from hard_brain_bot.utils import setup_logging


if __name__ == "__main__":
    bot = HardBrain()
    bot.load_extension("hard_brain_bot.cogs.quiz_commands")

    @bot.event
    async def on_ready():
        print(f"Logged in as {bot.user} (ID: {bot.user.id})")

    setup_logging(
        "disnake",
        os.path.abspath("discord.log"),
        "%(asctime)s:%(levelname)s:%(name)s: %(message)s",
        "INFO",
    )
    if not (token := os.getenv("DISCORD_TOKEN")):
        raise RuntimeError("DISCORD_TOKEN environment variable is not set.")
    bot.run(token)
