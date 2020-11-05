import re
import datetime

import discord
from discord.ext import commands

from core import checks
from core.models import PermissionLevel


class Embedder(commands.Cog):
    """Plugin that gives you the ability to easily embed text."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.db = self.bot.plugin_db.get_partition(self)

    @commands.group(name="embedder", invoke_without_command=True)
    @checks.has_permissions(PermissionLevel.MODERATOR)
    async def embedder(self, ctx: commands.Context):
        """Easily embed text."""

        await ctx.send_help(ctx.command)

    @embedder.command(name="color", aliases=["colour"])
    @checks.has_permissions(PermissionLevel.MODERATOR)
    async def color(self, ctx: commands.Context, colorcode: str):
        """Save a hex code for use in embeds."""

        is_valid = re.search(r"^#(?:[0-9a-fA-F]{3}){1,2}$", colorcode)

        if not is_valid:
            link = "https://htmlcolorcodes.com/color-picker"

            embed = discord.Embed(
                title="Embedder",
                description=f"Enter a valid [hex code]({link}).",
                color=self.bot.main_color,
            )

            return await ctx.send(embed=embed)

        color = discord.Color(int(colorcode.replace("#", "0x"), 0))

        await self.db.find_one_and_update(
            {"_id": "embedcolor-config"},
            {"$set": {"colorcode": colorcode.replace("#", "0x").lower()}},
            upsert=True,
        )

        embed = discord.Embed(
            title="Embedder",
            description=f"`{color}` will be used for every future embed.",
            color=color,
        )

        await ctx.send(embed=embed)

    @embedder.command(name="send", aliases=["make"])
    @checks.has_permissions(PermissionLevel.MODERATOR)
    async def send(self, ctx: commands.Context, title: str, *, message: str):
        """Send an embed."""

        config = await self.db.find_one({"_id": "embedcolor-config"})

        colorcode = config.get("colorcode", str(discord.Color.blue()))

        embed = discord.Embed(
            title=title,
            description=message,
            color=discord.Color(int(colorcode, 0)),
            timestamp=datetime.datetime.utcnow(),
        )

        embed.set_author(
            name=ctx.author.display_name, icon_url=ctx.author.avatar_url
        )

        await ctx.send(embed=embed)

        await ctx.message.delete()


def setup(bot: commands.Bot):
    bot.add_cog(Embedder(bot))
