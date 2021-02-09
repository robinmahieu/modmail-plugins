import discord
from discord.ext import commands

from core import checks
from core.models import PermissionLevel


class Purger(commands.Cog):
    """Plugin to delete multiple messages at once."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command()
    @checks.has_permissions(PermissionLevel.MODERATOR)
    async def purge(self, ctx: commands.Context, amount: int):
        """Delete multiple messages at once."""

        if amount < 1:
            raise commands.BadArgument(
                "The amount of messages to delete should be a scrictly "
                f"positive integer, not `{amount}`."
            )

        try:
            deleted = await ctx.channel.purge(limit=amount + 1)
        except discord.Forbidden:
            embed = discord.Embed(color=self.bot.error_color)

            embed.description = (
                "This command requires the `Manage Messages` permission, "
                "which the bot does not have at the moment."
            )

            return await ctx.send(embed=embed)

        message = f"{len(deleted)} messages have been deleted!"
        to_delete = await ctx.send(message)

        await to_delete.delete(delay=3)


def setup(bot: commands.Bot):
    bot.add_cog(Purger(bot))
