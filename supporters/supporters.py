import discord
from discord.ext import commands
from discord.ext.commands import Context

from core import checks
from core.models import PermissionLevel


class Supporters(commands.Cog):
    """Plugin that gives your server members the ability to view who's
    part of the support team.
    """

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(aliases=["helpers", "supporters", "supportmembers"])
    @checks.has_permissions(PermissionLevel.REGULAR)
    async def support(self, ctx: Context):
        """View who's part of the support team."""

        category_id = self.bot.config.get("main_category_id")

        if category_id is None:
            description = (
                "The Modmail category was could not be found.\nPlease make "
                "sure it has been set with the `?config set "
                "main_category_id` command."
            )

            embed = discord.Embed(
                title="Supporters",
                description=description,
                color=self.bot.main_color,
            )

            return await ctx.send(embed=embed)

        categories = self.bot.modmail_guild.categories

        members = {
            "online": [],
            "idle": [],
            "dnd": [],
            "offline": [],
        }

        status_fmt = {
            "online": "Online  🟢",
            "idle": "Idle  🟡",
            "dnd": "Do Not Disturb  🔴",
            "offline": "Offline  ⚪",
        }

        for category in categories:
            if category.id != int(category_id):
                continue

            for member in self.bot.modmail_guild.members:
                if (
                    member.permissions_in(category).read_messages
                    and not member.bot
                ):
                    members[str(member.status)].append(member.mention)

        embed = discord.Embed(
            title="Support Members", color=self.bot.main_color,
        )

        for status, member_list in members.items():
            if member_list:
                embed.add_field(
                    name=status_fmt[status], value=", ".join(member_list)
                )

        await ctx.send(embed=embed)


def setup(bot: commands.Bot):
    bot.add_cog(Supporters(bot))
