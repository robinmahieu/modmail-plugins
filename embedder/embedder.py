import datetime
import discord
from discord.ext import commands
from discord.ext.commands import has_permissions


class Embedder:
    """The embedder plugin for Modmail: https://github.com/papiersnipper/modmail-plugins/embedder"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @has_permissions(manage_messages=True)
    async def embed(self, ctx, title: str = None, *, message: str = None):
        """Sends an embed to the channel where you used the command."""

        if title is None:
            return await ctx.send('Please enter a title between double quotes.')

        if message is None:
            return await ctx.send('Please enter a message.')

        embed = discord.Embed(
            title=title,
            description=message,
            color=discord.Color.blue(),
            timestamp=datetime.datetime.utcnow()
            )

        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)

        await ctx.send(embed=embed)
        await ctx.message.delete()


def setup(bot):
    bot.add_cog(Embedder(bot))
