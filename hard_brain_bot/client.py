import disnake
from disnake.ext import commands


class HardBrain(commands.Bot):
    def __init__(
        self,
        command_prefix: str = "hb!",
        intents: disnake.Intents | None = None,
        debug: bool = False,
    ) -> None:
        command_sync_flags = commands.CommandSyncFlags.default()
        if not intents:
            intents = disnake.Intents.default()
            intents.message_content = True
        if debug:
            command_sync_flags.sync_commands_debug = True
        super().__init__(command_prefix, intents=intents, command_sync_flags=command_sync_flags)
