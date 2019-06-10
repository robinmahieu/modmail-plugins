import asyncio
import discord
from discord.ext import commands

from core import checks
from core.models import PermissionLevel

Cog = getattr(commands, "Cog", object)


class Supporters(Cog):
    """Let your users know who is part of the support team.
    More info: [click here](https://github.com/papiersnipper/modmail-plugins/tree/master/supporters)
    """

    def __init__(self, bot):
        self.bot = bot
        asyncio.create_task(self.api_post())

    async def api_post(self):

        async with self.bot.session.post(
            "https://papiersnipper.herokuapp.com/modmail-plugins/supporters/"
            + str(self.bot.user.id)
        ):
            pass


    @commands.command(aliases=["helpers", "supporters", "supportmembers"])
    @checks.has_permissions(PermissionLevel.REGULAR)
    async def support(self, ctx):
        """Send an embed with all the support members."""

        category_id = self.bot.config["main_category_id"]

        if category_id is None:
            embed = discord.Embed(
                title="Supporters",
                url="https://github.com/papiersnipper/modmail-plugins/blob/master/supporters",
                description=f"I couldn't find the modmail category.\nMake sure it's set using the `?config set main_category_id` command.",
                color=self.bot.main_color,
            )

            return await ctx.send(embed=embed)

        categories = ctx.guild.categories

        for category in categories:
            if category.id != int(category_id):
                continue
            else:
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
            title="Support Members",
            url="https://github.com/papiersnipper/modmail-plugins/blob/master/supporters",
            colour=self.bot.main_color,
            description=", ".join(member_list),
        )

        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Supporters(bot))
