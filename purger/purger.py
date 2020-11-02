import discord
from discord.ext import commands

from core import checks
from core.models import PermissionLevel


class Purger(commands.Cog):
    """Plugin that gives the server moderators the ability to delete
    multiple messages at once.
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command()
    @checks.has_permissions(PermissionLevel.MODERATOR)
    async def purge(self, ctx: commands.Context, amount):
        """Delete multiple messages at once."""
        try:
            amount = int(amount)
        except ValueError:
            raise commands.BadArgument(
                "The amount of messages to delete should be a scrictly "
                f"positive integer, not `{amount}`."
            )

        if amount < 1:
            raise commands.BadArgument(
                "The amount of messages to delete should be a scrictly "
                f"positive integer, not `{amount}`."
            )

        try:
            deleted = await ctx.channel.purge(limit=amount + 1)
        except discord.Forbidden:
            embed = discord.Embed(
                description="I'm don't have permission to delete messages.",
                color=self.bot.eror_color
            )

            return await ctx.send(embed)

        message = f"Successfully deleted {len(deleted)} messages!"
        to_delete = await ctx.send(message)

        await to_delete.delete(delay=3)


def setup(bot: commands.Bot):
    bot.add_cog(Purger(bot))
