import asyncio

import discord
from discord.ext import commands

from core import checks
from core.models import PermissionLevel, getLogger

logger = getLogger(__name__)


class RoleAssignment(commands.Cog):
    """Plugin to assign roles by clicking reactions."""

    def __init__(self, bot):
        self.bot = bot
        self.db = self.bot.plugin_db.get_partition(self)

        asyncio.create_task(self.remove_obsolete_ids())

    async def remove_obsolete_ids(self):
        """Function that gets invoked whenever this plugin is loaded.

        It will look for a configuration file in the database and
        remove message IDs that no longer exist, in order to prevent
        them from cluttering the database.
        """
        config = await self.db.find_one({"_id": "role-config"})

        if config is None:
            return

        category_id = int(self.bot.config["main_category_id"] or 0)

        if category_id == 0:
            logger.warning("No main_category_id set.")
            return

        guild = self.bot.modmail_guild

        if guild is None:
            logger.warning("No guild_id set.")
            return

        category = discord.utils.get(guild.categories, id=category_id)

        if category is None:
            logger.warning("Invalid main_category_id set.")

        message_ids = []

        for channel in category.text_channels:
            thread = await self.bot.threads.find(channel=channel)

            if thread is None:
                continue

            if thread.genesis_message is None:
                messages = await channel.history(oldest_first=True).flatten()
                thread.genesis_message = messages[0]

            message_ids.append(str(thread.genesis_message.id))

        await self.db.find_one_and_update(
            {"_id": "role-config"}, {"$set": {"ids": message_ids}}
        )

    @commands.group(
        name="role", aliases=["roles"], invoke_without_command=True
    )
    @checks.has_permissions(PermissionLevel.ADMINISTRATOR)
    async def role(self, ctx):
        """Assign roles by clicking a reaction."""

        await ctx.send_help(ctx.command)

    @role.command(name="add")
    @checks.has_permissions(PermissionLevel.ADMINISTRATOR)
    async def role_add(self, ctx, emoji: discord.Emoji, *, role: discord.Role):
        """Add a reaction to each new thread."""

        config = await self.db.find_one({"_id": "role-config"})

        if config is None:
            await self.db.insert_one({"_id": "role-config", "emoji": {}, "ids": []})
            config = await self.db.find_one({"_id": "role-config"})

        failed = config["emoji"].get(str(emoji)) is not None

        if failed:
            return await ctx.send("That emoji already assigns a role.")

        config["emoji"][str(emoji)] = role.name

        await self.db.update_one(
            {"_id": "role-config"}, {"$set": {"emoji": config["emoji"]}}
        )

        await ctx.send(f"{emoji} will now assign the {role.name} role.")

    @role.command(name="remove")
    @checks.has_permissions(PermissionLevel.ADMINISTRATOR)
    async def role_remove(self, ctx, emoji: discord.Emoji):
        """Remove a reaction from each new thread."""

        config = await self.db.find_one({"_id": "role-config"})

        if config is None:
            return await ctx.send("There are no roles set up at the moment.")

        config["emoji"]

        try:
            del config["emoji"][str(emoji)]
        except KeyError:
            return await ctx.send("That emoji doesn't assign any role.")

        await self.db.update_one(
            {"_id": "role-config"}, {"$set": {"emoji": config["emoji"]}}
        )

        await ctx.send(f"The {emoji} emoji has been unlinked.")

    @role.command(name="list")
    @checks.has_permissions(PermissionLevel.ADMINISTRATOR)
    async def role_list(self, ctx):
        """View a list of reactions added to each new thread."""

        config = await self.db.find_one({"_id": "role-config"})

        if config is None:
            return await ctx.send("There are no roles set up at the moment.")

        embed = discord.Embed(
            title="Role Assignment", color=self.bot.main_color, description=""
        )

        for emoji, role_name in config["emoji"].items():
            role = discord.utils.get(self.bot.guild.roles, name=role_name)

            embed.description += f"{emoji} — {role.mention}\n"

        await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_thread_ready(
        self, thread, creator, category, initial_message
    ):
        """Function that gets invoked whenever a new thread is created.

        It will look for a configuration file in the database and add
        all emoji as reactions to the genesis message. Furthermore, it
        will update the list of genesis message IDs.
        """
        message = thread.genesis_message

        config = await self.db.find_one({"_id": "role-config"})

        if config is None:
            return

        for emoji in config["emoji"].keys():
            await message.add_reaction(emoji)

        config["ids"].append(str(message.id))

        await self.db.find_one_and_update(
            {"_id": "role-config"}, {"$set": {"ids": config["ids"]}}
        )

    @commands.Cog.listener()
    async def on_raw_reaction_add(
        self, payload: discord.RawReactionActionEvent
    ):
        """Function that gets invoked whenever a reaction is added.

        It will look for a configuration file in the database and
        update the member's role according to the added emoji.
        """
        config = await self.db.find_one({"_id": "role-config"})

        if config is None:
            return

        if str(payload.message_id) not in config["ids"]:
            return

        if str(payload.emoji) not in config["emoji"].keys():
            return

        if payload.user_id == self.bot.user.id:
            return

        channel = self.bot.get_channel(payload.channel_id)
        thread = await self.bot.threads.find(channel=channel)

        if thread is None:
            return

        user = thread.recipient

        if not isinstance(user, int):
            user = user.id

        member = self.bot.guild.get_member(user)

        role_name = config["emoji"][str(payload.emoji)]
        role = discord.utils.get(self.bot.guild.roles, name=role_name)

        if role is None:
            message = (
                f"The role associated with {payload.emoji} ({role_name}) "
                "could not be found."
            )

            await channel.send(message)

        await member.add_roles(role)

        await channel.send(f"The {role} role has been added to {member}.")

    @commands.Cog.listener()
    async def on_raw_reaction_remove(
        self, payload: discord.RawReactionActionEvent
    ):
        """Function that gets invoked whenever a reaction is removed.

        It will look for a configuration file in the database and
        update the member's role according to the removed emoji.
        """
        config = await self.db.find_one({"_id": "role-config"})

        if config is None:
            return

        if str(payload.message_id) not in config["ids"]:
            return

        if str(payload.emoji) not in config["emoji"].keys():
            return

        if payload.user_id == self.bot.user.id:
            return

        channel = self.bot.get_channel(payload.channel_id)
        thread = await self.bot.threads.find(channel=channel)

        if thread is None:
            return

        user = thread.recipient

        if not isinstance(user, int):
            user = user.id

        member = self.bot.guild.get_member(user)

        role_name = config["emoji"][str(payload.emoji)]
        role = discord.utils.get(self.bot.guild.roles, name=role_name)

        if role is None:
            await channel.send(
                f"The role associated with {payload.emoji} ({role_name}) "
                "could not be found."
            )

        await member.remove_roles(role)

        await channel.send(f"The {role} role has been removed from {member}.")


def setup(bot):
    bot.add_cog(RoleAssignment(bot))
