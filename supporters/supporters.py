import discord
from discord.ext import commands

from core import checks
from core.models import PermissionLevel

Cog = getattr(commands, 'Cog', object)


class Supporters(Cog):
    """Let your users know who is part of the support team.
    More info: [click here](https://github.com/papiersnipper/modmail-plugins/tree/master/supporters)
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['helpers', 'supporters', 'supportmembers'])
    @checks.has_permissions(PermissionLevel.REGULAR)
    async def support(self, ctx):
        """Send an embed with all the support members."""

        category_id = self.bot.config.get('main_category_id')

        if category_id is None:
            return await ctx.send('I couldn\'t find the modmail category.')

        categories = ctx.guild.categories

        for c in categories:
            if c.id != int(category_id):
                continue
            else:
                category = c

        member_list = []

        for member in ctx.guild.members:
            if member.permissions_in(category).read_messages:
                if not member.bot:
                    member_list.append(member.mention)
                else:
                    continue
            else:
                continue

        embed = discord.Embed(
            title='Support Members',
            colour=discord.Colour.blue(),
            description=', '.join(member_list)
        )

        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Supporters(bot))
