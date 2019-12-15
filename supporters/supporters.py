"""
Supporters plugin for Modmail.

Written by Papiersnipper.
All rights reserved.
"""

from discord import Embed
from discord.ext.commands import Bot, Cog, Context, command

from core.checks import has_permissions
from core.models import PermissionLevel


class Supporters(Cog):
    """Let your users know who is part of the support team.
    More info: [click here](https://github.com/papiersnipper/modmail-plugins/tree/master/supporters)
    """

    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @command(aliases=["helpers", "supporters", "supportmembers"])
    @has_permissions(PermissionLevel.REGULAR)
    async def support(self, ctx: Context) -> None:
        """Send an embed with all the support members."""

        category_id = self.bot.config.get("main_category_id")

        if category_id is None:
            embed = Embed(
                title="Supporters",
                url="https://github.com/papiersnipper/modmail-plugins/blob/master/supporters",
                description=f"I couldn't find the modmail category.\nMake sure it's set using the `?config set main_category_id` command.",
                color=self.bot.main_color,
            )

            return await ctx.send(embed=embed)

        categories = self.bot.modmail_guild.categories

        for category in categories:
            if category.id != int(category_id):
                continue

            member_list = []
            for member in self.bot.modmail_guild.members:
                if member.permissions_in(category).read_messages:
                    if not member.bot:
                        member_list.append(member.mention)

        embed = Embed(
            title="Support Members",
            url="https://github.com/papiersnipper/modmail-plugins/blob/master/supporters",
            colour=self.bot.main_color,
            description=", ".join(member_list),
        )

        await ctx.send(embed=embed)


def setup(bot: Bot) -> None:
    """Bot cog load."""
    bot.add_cog(Supporters(bot))
