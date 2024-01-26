import disnake
from disnake.ext import commands


class HardBrain(commands.Bot):
    def __init__(self, command_prefix: str = "hb!", intents: disnake.Intents | None = None):
        if not intents:
            intents = disnake.Intents.default()
            intents.message_content = True
        super().__init__(command_prefix, intents=intents)
