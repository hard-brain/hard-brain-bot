from collections import Counter

from disnake import Embed, Asset
from hard_brain_bot.data_models.requests import SongData


def embed_about() -> Embed:
    embed = Embed(
        title="Hard Brain",
        description="A IIDX music quiz bot. Made by corndog.",
    )
    embed.add_field(
        name="Commands",
        value="`about`, `start_quiz`",
        inline=False,
    )
    return embed


def embed_song_data(
    title: str, song_data: SongData, thumbnail: Asset | None = None
) -> Embed:
    embed = Embed(
        title=title,
    )
    if thumbnail:
        embed.set_thumbnail(thumbnail)
    embed.add_field(name="Song Title", value=song_data.title, inline=False)
    embed.add_field(name="Song Artist", value=song_data.artist, inline=False)
    embed.add_field(name="Genre", value=song_data.genre, inline=False)
    if len(song_data.alt_titles) > 0:
        titles = [f"`{title}`" for title in song_data.alt_titles]
        embed.add_field(name="Alternate titles", value=", ".join(titles), inline=False)
    return embed


def embed_scores(scores: Counter, title: str = "Scores") -> Embed:
    embed = Embed(title=title)
    player_limit = min(5, len(scores))
    players = [
        f"#{rank}: {player} - `{score}`"
        for rank, player, score in enumerate(scores.most_common(5))
    ]
    field_name = (
        # "Top n player(s)"
        f"Top {player_limit} Player{'s' if len(scores) != 1 else ''}"
    )
    embed.add_field(
        name="Results" if len(scores) == 0 else field_name,
        value="\n".join(players) if len(players) > 0 else "No one got any points!",
    )
    return embed
