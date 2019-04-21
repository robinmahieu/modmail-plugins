import discord
from discord.ext import commands


class Supporters:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['helpers', 'supporters', 'supportmembers'])
    async def support(self, ctx):
        channel_id = self.bot.config.get('log_channel_id')
        channel = ctx.guild.get_channel(int(channel_id))

        member_list = []

        for member in channel.members:
            if member.bot:
                continue
            else:
                member_list.append(member.mention)

        embed = discord.Embed(
            title='Support Members',
            colour=discord.Colour.blue(),
            description=', '.join(member_list)
        )

        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Supporters(bot))
