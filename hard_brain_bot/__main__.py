import os
import sys
from loguru import logger

from hard_brain_bot.client import HardBrain

if __name__ == "__main__":
    bot = HardBrain()
    bot.load_extension("hard_brain_bot.cogs.general_commands")
    bot.load_extension("hard_brain_bot.cogs.quiz_commands")
    logger.add(sys.stderr, format="{time} {level} {message}", level="INFO")


    @bot.event
    async def on_ready():
        logger.info(f"Logged in as {bot.user} (ID: {bot.user.id})")


    if not (token := os.getenv("DISCORD_TOKEN")):
        logger.critical("DISCORD_TOKEN environment variable is not set. Exiting...")
        sys.exit(1)
    bot.run(token)
