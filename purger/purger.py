import asyncio
import discord
from discord.ext import commands

from core import checks
from core.models import PermissionLevel

Cog = getattr(commands, 'Cog', object)


class Purger(Cog):
    """The purger plugin for Modmail: https://github.com/papiersnipper/modmail-plugins/blob/master/purger"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @checks.has_permissions(PermissionLevel.MODERATOR)
    async def purge(self, ctx, amount: str = None):
        """Deletes the specified amount of messages."""

        try:
            if amount is None:
                return await ctx.send('Please specify an amount of messages to delete.')
            else:
                try:
                    amount = int(amount)
                except Exception:
                    return await ctx.send('That\'s not a valid amount of messages to delete.')

                if amount > 1 and amount < 100:
                    await ctx.channel.purge(limit=amount + 1)
                    delete_message = await ctx.send(f'I successfully deleted {amount} messages!')

                    await asyncio.sleep(3)
                    await delete_message.delete()
                else:
                    return await ctx.send('The number of messages to delete has been be between 1 and 100.')

        except discord.Forbidden:
            return await ctx.send('I don\'t have the proper permissions to delete messages.')


def setup(bot):
    bot.add_cog(Purger(bot))
