import logging

import asyncio
import discord
from discord.ext import commands

from core import checks
from core.models import PermissionLevel

Cog = getattr(commands, "Cog", object)

logger = logging.getLogger("Modmail")


class Autorole(Cog):
    """Auto-assign a role to a user when they join your server.
    More info: [click here](https://github.com/papiersnipper/modmail-plugins/tree/master/autorole)
    """

    def __init__(self, bot):
        self.bot = bot
        self.db = bot.plugin_db.get_partition(self)
        asyncio.create_task(self.api_post())

    async def api_post(self):

        async with self.bot.session.post(
            "https://papiersnipper.herokuapp.com/modmail-plugins/autorole/"
            + str(self.bot.user.id)
        ):
            pass

    @Cog.listener()
    async def on_member_join(self, member):
        config = await self.db.find_one({"_id": "autorole-config"})

        if config is None:
            return logger.warning("Member joined while no role was set!")

        try:
            rolename = config["rolename"]
        except KeyError:
            return logger.error("Something went wrong in your database!")

        role = discord.utils.get(member.guild.roles, name=rolename)

        if role is None:
            return logger.error(f"Unknown role {rolename}!")

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

        config = await self.db.find_one({"_id": "autorole-config"})

        if config is None:
            await self.db.insert_one({"_id": "autorole-config"})
            logger.info("Created autorole config file.")

        await self.db.find_one_and_update(
            {"_id": "autorole-config"}, {"$set": {"rolename": role.name}}
        )

        embed = discord.Embed(
            title="Autorole",
            url="https://github.com/papiersnipper/modmail-plugins/blob/master/autorole",
            description=f"I will now give {role.mention} to all new members.",
            colour=self.bot.main_color,
        )

        await ctx.send(embed=embed)

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

        embed = discord.Embed(
            title="Autorole",
            url="https://github.com/papiersnipper/modmail-plugins/blob/master/autorole",
            description=f"Added {role.mention} for {users} members.",
            colour=self.bot.main_color,
        )

        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Autorole(bot))
