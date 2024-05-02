import logging

import disnake
from aiohttp import ClientConnectorError
from disnake import VoiceClient, Webhook, Thread, TextChannel
from disnake.ext import commands
from disnake.ext.commands import CommandInvokeError

from hard_brain_bot.client import HardBrain
from hard_brain_bot.message_templates import embeds
from hard_brain_bot.services.hard_brain_service import HardBrainService
from hard_brain_bot.services.quiz_service import QuizService


class QuizCommands(commands.Cog):
    MIN_TIME_LIMIT: float = 5.0
    MAX_TIME_LIMIT: float = 60.0
    MIN_ROUNDS: int = 1
    MAX_ROUNDS: int = 100

    def __init__(self, bot: HardBrain) -> None:
        self.bot = bot
        self.voice: VoiceClient | None = None
        self.backend = HardBrainService()
        self.game: QuizService | None = None
        self.message_receiver: Webhook | Thread | None = None

    @commands.Cog.listener()
    async def on_message(self, ctx: disnake.Message) -> None:
        if (not self.game) or (ctx.author.id == self.bot.user.id):
            return
        await self.game.queue_answer_to_check(ctx)

    @commands.slash_command(description="More information about Hard Brain")
    async def about(self, ctx: disnake.ApplicationCommandInteraction) -> None:
        embed = embeds.embed_about()
        await ctx.response.send_message(embed=embed)

    @commands.slash_command(description="Starts a quiz")
    async def start_quiz(
            self,
            ctx: disnake.ApplicationCommandInteraction,
            rounds: int = 5,
            time_limit: float = 30.0,
    ) -> None:
        # check user is in voice channel
        if not ctx.author.voice:
            await ctx.response.send_message(
                "Error: you are not connected to a voice channel", ephemeral=True
            )
            return
        if self.game and self.game.is_in_progress():
            await ctx.response.send_message("A quiz is already in progress!", ephemeral=True)
            return
        if (
                time_limit < QuizCommands.MIN_TIME_LIMIT
                or time_limit > QuizCommands.MAX_TIME_LIMIT
        ):
            await ctx.response.send_message(
                "Invalid time limit. Time limit must be between %d and %d seconds."
                % (QuizCommands.MIN_TIME_LIMIT, QuizCommands.MAX_TIME_LIMIT),
                ephemeral=True
            )
            return
        if rounds < QuizCommands.MIN_ROUNDS or rounds > QuizCommands.MAX_ROUNDS:
            await ctx.response.send_message(
                "Invalid number of rounds. Number of rounds must be between %d and %d"
                % (QuizCommands.MIN_ROUNDS, QuizCommands.MAX_ROUNDS),
                ephemeral=True
            )
            return

        await ctx.response.defer()
        await ctx.edit_original_response("Please wait, preparing a quiz...")
        try:
            question_response = await self.backend.get_question(number_of_songs=rounds)
        except (CommandInvokeError, ClientConnectorError) as e:
            logging.error(e)
            await ctx.edit_original_response(f"Network error occurred while preparing quiz...")
            return

        if isinstance(ctx.channel, TextChannel):
            try:
                self.message_receiver = await ctx.channel.create_webhook(
                    name="Hard Brain",
                    avatar=self.bot.user.avatar,
                    reason="Created by Hard Brain and should be removed automatically - "
                           "if it persists when the quiz is not running, feel free to delete"
                )
            except disnake.Forbidden:
                await ctx.edit_original_response(
                    f"Error: Missing 'Manage Webhooks' permission, try starting in a Thread instead of a text channel")
                return
        elif isinstance(ctx.channel, Thread):
            self.message_receiver = ctx.channel
        else:
            await ctx.edit_original_response(f"Error: Channel '{ctx.channel.name}' is not a TextChannel or Thread")
            return

        self.game = QuizService(
            ctx,
            self.message_receiver,
            self.backend,
            song_data_list=question_response,
            round_time_limit=time_limit,
        )
        try:
            await self.game.start_game()
        finally:
            if self.message_receiver and isinstance(self.message_receiver, Webhook):
                await self.message_receiver.delete()
            self.game = None

    @commands.slash_command(description="Cancels an ongoing quiz")
    async def end_quiz(self, ctx: disnake.ApplicationCommandInteraction) -> None:
        if not self.game:
            await ctx.response.send_message("No quiz is in progress", ephemeral=True)
            return
        await ctx.response.defer()
        await ctx.edit_original_response("Cancelling quiz...")
        await self.game.end_game(show_embed=False)
        await ctx.edit_original_response("Cancelled quiz")
        self.game = None

    @commands.slash_command(description="Skip a round")
    async def skip_round(self, ctx: disnake.ApplicationCommandInteraction) -> None:
        if not self.game:
            await ctx.response.send_message("No quiz is in progress", ephemeral=True)
            return
        await ctx.response.send_message("Skipping round...")
        await self.game.skip_round()

    @commands.slash_command(description="Get the current scores")
    async def current_scores(self, ctx: disnake.ApplicationCommandInteraction) -> None:
        if not self.game:
            await ctx.response.send_message("No quiz is in progress", ephemeral=True)
            return
        scores = self.game.current_scores()
        await ctx.response.send_message(
            embed=embeds.embed_scores(scores, title="Current Scores")
        )


def setup(bot: HardBrain) -> None:
    bot.add_cog(QuizCommands(bot))
