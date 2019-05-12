import asyncio
import discord
from discord.ext import commands


class Purger:
    """The purger plugin for Modmail: https://github.com/papiersnipper/modmail-plugins/blob/master/purger"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def purge(self, ctx, amount: str = None):
        """Deletes the specified amount of messages."""

        owners = self.bot.config.get('owners').split(',')

        if ctx.message.author.guild_permissions.manage_messages or ctx.message.author.id in (int(x) for x in owners):
            try:
                if amount is None:
                    return await ctx.send('Please specify amount of messages.')
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
                        return await ctx.send('The number of messages has been be between 1 and 100.')

            except discord.Forbidden:
                return await ctx.send('I don\'t have the proper permissions to delete messages.')
        else:
            return await ctx.send('You don\'t have the proper permissions to delete messages.')


def setup(bot):
    bot.add_cog(Purger(bot))
