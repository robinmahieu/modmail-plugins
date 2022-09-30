import discord
from discord.ext import commands

from core import checks
from core.models import PermissionLevel


class Supporters(commands.Cog):
    """Plugin to view which members are part of the support team."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command(aliases=["helpers", "supporters", "supportmembers"])
    @checks.has_permissions(PermissionLevel.REGULAR)
    async def support(self, ctx: commands.Context):
        """View which members are part of the support team."""

        category = self.bot.main_category

        if category is None:
            description = (
                "The Modmail category could not be found.\nPlease make sure "
                "that it has been set correctly with the `?config set "
                "main_category_id` command."
            )

            embed = discord.Embed(
                title="Supporters",
                description=description,
                color=self.bot.main_color,
            )

            return await ctx.send(embed=embed)

        members = {
            "online": [],
            "idle": [],
            "dnd": [],
            "offline": [],
        }

        status_fmt = {
            "online": "Online 🟢",
            "idle": "Idle 🟡",
            "dnd": "Do Not Disturb 🔴",
            "offline": "Offline ⚪",
        }

        for member in self.bot.modmail_guild.members:
            if (
                category.permissions_for(member).read_messages
                and not member.bot
            ):
                members[str(member.status)].append(member.mention)

        embed = discord.Embed(
            title="Support Members", color=self.bot.main_color
        )

        for status, member_list in members.items():
            if member_list:
                embed.add_field(
                    name=status_fmt[status], value=", ".join(member_list)
                )

        await ctx.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Supporters(bot))
