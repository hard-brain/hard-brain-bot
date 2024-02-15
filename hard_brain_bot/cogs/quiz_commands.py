import logging

import disnake
from disnake import VoiceClient
from disnake.ext import commands
from disnake.ext.commands import CommandInvokeError

from hard_brain_bot.client import HardBrain
from hard_brain_bot.data_models.requests import SongData
from hard_brain_bot.message_templates import embeds
from hard_brain_bot.services.hard_brain_service import HardBrainService
from hard_brain_bot.services.quiz_service import QuizService


class QuizCommands(commands.Cog):
    def __init__(self, bot: HardBrain) -> None:
        self.bot = bot
        self.voice: VoiceClient | None = None
        self.backend = HardBrainService()
        self.game: QuizService | None = None

    @commands.Cog.listener()
    async def on_message(self, ctx: disnake.Message) -> None:
        if not self.game or ctx.author == self.bot.user.id:
            return
        await self.game.check_answer(ctx.content)

    @commands.slash_command(description="More information about Hard Brain")
    async def about(self, ctx: disnake.ApplicationCommandInteraction) -> None:
        embed = embeds.embed_about()
        await ctx.response.send_message(embed=embed)

    @commands.slash_command(description="Test command to fetch data for a random song")
    async def debug_song(self, ctx: disnake.ApplicationCommandInteraction) -> None:
        fixture = SongData(
            song_id=30999,
            filename="test.mp3",
            title="TEST!! がんばって！！",
            alt_titles=["test!!", "test ganbatte"],
            artist="DJ TEST",
            genre="testcore",
        )
        embed = embeds.embed_song_data(
            "Example song data embed", fixture, thumbnail=self.bot.user.display_avatar
        )
        await ctx.response.send_message(embed=embed)

    @commands.slash_command(description="Starts a quiz")
    async def start_quiz(
        self,
        ctx: disnake.ApplicationCommandInteraction,
        rounds: int = 5,
        time_limit: float = 30.0,
    ) -> None:
        # check user is in voice channel
        if not (connected := ctx.author.voice):
            await ctx.response.send_message(
                "Error: you are not connected to a voice channel"
            )
            return
        if self.game:
            await ctx.response.send_message("A quiz is already in progress!")
            return
        await ctx.response.defer()
        await ctx.edit_original_response("Please wait, preparing a quiz...")
        try:
            question_response = await self.backend.get_question(number_of_songs=rounds)
        except CommandInvokeError as e:
            logging.error(e)
            await ctx.edit_original_response(f"Error occurred while preparing quiz...")
            return

        await ctx.edit_original_response(
            f"Quiz starting in #{connected.channel}! "
            f"You have {int(time_limit)} seconds to answer the name of the song."
        )
        self.game = QuizService(
            ctx,
            self.backend,
            song_data_list=question_response,
            round_time_limit=time_limit,
        )
        await self.game.start_game()

    @commands.slash_command(description="Cancels an ongoing quiz")
    async def end_quiz(self, ctx: disnake.ApplicationCommandInteraction) -> None:
        if not self.game:
            await ctx.response.send_message("No quiz is in progress", ephemeral=True)
            return
        await ctx.response.defer()
        await ctx.edit_original_response("Cancelling quiz...")
        await self.game.end_game()
        await ctx.edit_original_response("Cancelled quiz")
        self.game = None  # will have to investigate whether all tasks get cleaned up before we call this command

    @commands.slash_command(description="Skip a round")
    async def skip_round(self, ctx: disnake.ApplicationCommandInteraction) -> None:
        if not self.game:
            await ctx.response.send_message("No quiz is in progress", ephemeral=True)
            return
        await ctx.response.send_message("Skipping round...")
        await self.game.skip_round()


def setup(bot: HardBrain) -> None:
    bot.add_cog(QuizCommands(bot))
