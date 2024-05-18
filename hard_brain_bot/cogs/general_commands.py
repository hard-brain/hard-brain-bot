import disnake
from aiohttp import ClientSession, ClientConnectorError
from disnake.ext import commands
from disnake.ext.commands import CommandInvokeError
from loguru import logger

from hard_brain_bot.client import HardBrain
from hard_brain_bot.message_templates import embeds


class GeneralCommands(commands.Cog):
    def __init__(self, bot: HardBrain) -> None:
        self.bot = bot

    @commands.slash_command(description="More information about Hard Brain")
    async def about(self, ctx: disnake.ApplicationCommandInteraction) -> None:
        embed = embeds.embed_about()
        await ctx.response.send_message(embed=embed)

    @commands.slash_command(description="Suggest alternate title(s) for a song")
    async def suggest(self, ctx: disnake.ApplicationCommandInteraction, current_song_title: str, suggested_title: str):
        author_name = ctx.author.name
        guild_name = ctx.guild.name
        embed = embeds.embed_suggest(author_name, guild_name, current_song_title, suggested_title)
        try:
            await GeneralCommands._send_feedback(embed)
            await ctx.response.send_message("Your suggestion has been received.", ephemeral=True)
            logger.info(
                f"Song title suggestion received from user '{author_name}' in guild '{guild_name}': "
                f"{current_song_title} -> {suggested_title}"
            )
        except (CommandInvokeError, ClientConnectorError) as e:
            await ctx.response.send_message(
                "An unexpected error occurred while sending feedback. Please start a discussion on GitHub instead "
                "(https://github.com/orgs/hard-brain/discussions/categories/song-title-changes)",
                ephemeral=True
            )
            logger.error(f"Unexpected {type(e)} error occurred while sending feedback")

    @staticmethod
    async def _send_feedback(embed):
        feedback_webhook_url = "https://discord.com/api/webhooks/1238906406032117821/" \
                               "hEZy1y2rafcmvPbY1_BkfuGw4GqicKbYPdxtO9JG5hbukZFXQZhc_UXdkqnAUR-ZK5WE"
        async with ClientSession() as session:
            feedback_webhook = disnake.Webhook.from_url(
                feedback_webhook_url,
                session=session)
            await feedback_webhook.send(embed=embed)


def setup(bot: HardBrain) -> None:
    bot.add_cog(GeneralCommands(bot))
