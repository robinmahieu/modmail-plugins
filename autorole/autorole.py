import discord
from discord.ext import commands

from core import checks
from core.models import PermissionLevel, getLogger

logger = getLogger(__name__)


class Autorole(commands.Cog):
    """Plugin that gives you the ability to automatically assign roles
    to users who join your server.
    """

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.db = bot.plugin_db.get_partition(self)

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        """Function that gets invoked whenever a user joins a server.

        It will looks for a configuration file in the database and if
        one is found, the set roles will be assigned to the user.
        """
        if member.guild.id != self.bot.guild_id:
            return

        config = await self.db.find_one({"_id": "autorole-config"})

        if config is None:
            return

        try:
            role_ids = config["roles"]
        except KeyError:
            return logger.error("Something went wrong in the database!")

        if not role_ids:
            return

        roles = [member.guild.get_role(role_id) for role_id in role_ids]
        roles = [role for role in roles if role is not None]

        await member.add_roles(*roles)

    @commands.group(name="autorole", invoke_without_command=True)
    @checks.has_permissions(PermissionLevel.ADMINISTRATOR)
    async def autorole(self, ctx: commands.Context):
        """Automatically assign roles to users who join your server."""

        await ctx.send_help(ctx.command)

    @autorole.command(name="set")
    @checks.has_permissions(PermissionLevel.ADMINISTRATOR)
    async def autorole_set(
        self, ctx: commands.Context, roles: commands.Greedy[discord.Role]
    ):
        """Set the roles to assign to users who join your server."""

        if not roles:
            return await ctx.send_help(ctx.command)

        config = await self.db.find_one({"_id": "autorole-config"})

        if config is None:
            await self.db.insert_one({"_id": "autorole-config"})

        role_ids = [role.id for role in roles]
        role_mentions = [role.mention for role in roles]

        await self.db.find_one_and_update(
            {"_id": "autorole-config"}, {"$set": {"roles": role_ids}}
        )

        description = (
            f"{', '.join(role_mentions)} will now be assigned to users who "
            "join your server."
        )

        embed = discord.Embed(
            title="Autorole",
            description=description,
            color=self.bot.main_color,
        )

        await ctx.send(embed=embed)

    @autorole.command(name="give")
    @checks.has_permissions(PermissionLevel.ADMINISTRATOR)
    async def autorole_give(self, ctx: commands.Context, role: discord.Role):
        """Assign a role to all member of your server."""

        members = [
            member
            for member in ctx.guild.members
            if member not in role.members
        ]

        s = "" if len(members) == 1 else "s"

        description = (
            f"Adding {role.mention} to {len(members)} member{s}!\n"
            "Please note that this operation might take a while."
        )

        embed = discord.Embed(
            title="Autorole",
            description=description,
            color=self.bot.main_color,
        )

        await ctx.send(embed=embed)

        for member in members:
            await member.add_roles(role)

        embed = discord.Embed(
            title="Autorole",
            description=f"Added {role.mention} to {len(members)} member{s}!",
            colour=self.bot.main_color,
        )

        await ctx.send(embed=embed)

    @autorole.command(name="clear", aliases=["reset"])
    @checks.has_permissions(PermissionLevel.ADMINISTRATOR)
    async def autorole_clear(self, ctx: commands.Context):
        """Clear the list of roles to assign to users."""

        embed = discord.Embed(
            title="Autorole",
            description="No more roles will be assigned.",
            color=self.bot.main_color,
        )

        config = await self.db.find_one({"_id": "autorole-config"})

        if config is None:
            return await ctx.send(embed=embed)

        await self.db.find_one_and_update(
            {"_id": "autorole-config"}, {"$set": {"roles": []}}
        )

        await ctx.send(embed=embed)


def setup(bot: commands.Bot):
    bot.add_cog(Autorole(bot))
