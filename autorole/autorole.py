import discord
from discord.ext import commands

from core import checks
from core.models import PermissionLevel

Cog = getattr(commands, "Cog", object)


class Autorole(Cog):
    """Auto-assign a role to a user when they join your server.
    More info: [click here](https://github.com/papiersnipper/modmail-plugins/tree/master/autorole)
    """

    def __init__(self, bot):
        self.bot = bot
        self.db = bot.plugin_db.get_partition(self)

    @Cog.listener()
    async def on_member_join(self, member):
        rolename = (await self.db.find_one({"_id": "autorole-config"}))["rolename"]

        if rolename is None:
            return
        else:
            role = discord.utils.get(member.guild.roles, name=rolename)
            await member.add_roles(role)

    @commands.group(name="autorole", invoke_without_command=True)
    @checks.has_permissions(PermissionLevel.ADMINISTRATOR)
    async def autorole(self, ctx):
        """Auto-assign a role to a user when they join your server."""

        await ctx.send_help(ctx.command)

    @autorole.command(name="set")
    @checks.has_permissions(PermissionLevel.ADMINISTRATOR)
    async def set_(self, ctx, role: discord.Role):
        """Sets the default role a member gets when joining."""

        await self.db.find_one_and_update(
            {"_id": "autorole-config"}, {"$set": {"rolename": role.name}}
        )

        em = discord.Embed(
            title="Autorole",
            url="https://github.com/papiersnipper/modmail-plugins/blob/master/autorole",
            description=f"I will now give {role.mention} to all new members.",
            colour=self.bot.main_color,
        )

        await ctx.send(embed=em)

    @autorole.command(name="give")
    @checks.has_permissions(PermissionLevel.ADMINISTRATOR)
    async def give(self, ctx, role: discord.Role):
        """Gives this role to all members of your server."""

        users = 0
        for member in ctx.guild.members:
            if role.id in [role.id for role in member.roles]:
                continue
            else:
                await member.add_roles(role)
                users = users + 1

        em = discord.Embed(
            title="Autorole",
            url="https://github.com/papiersnipper/modmail-plugins/blob/master/autorole",
            description=f"Added {role.mention} for {users} members.",
            colour=self.bot.main_color,
        )

        await ctx.send(embed=em)


def setup(bot):
    bot.add_cog(Autorole(bot))
