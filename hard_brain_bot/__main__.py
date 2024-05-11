import os
import sys

from hard_brain_bot.client import HardBrain
from hard_brain_bot.utils.logging_utils import setup_logging


if __name__ == "__main__":
    bot = HardBrain()
    bot.load_extension("hard_brain_bot.cogs.quiz_commands")
    _logger = setup_logging("disnake", "CRITICAL", format_string="%(asctime)s:%(levelname)s:%(name)s: %(message)s")


    @bot.event
    async def on_ready():
        print(f"Logged in as {bot.user} (ID: {bot.user.id})")


    if not (token := os.getenv("DISCORD_TOKEN")):
        _logger.critical("DISCORD_TOKEN environment variable is not set. Exiting...")
        sys.exit(1)
    bot.run(token)
