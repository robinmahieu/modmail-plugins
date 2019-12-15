"""
Purger plugin for Modmail.

Written by Papiersnipper.
All rights reserved.
"""

import asyncio

from discord import Forbidden, Message
from discord.ext.commands import Bot, Cog, Context, command

from core.checks import has_permissions
from core.models import PermissionLevel


class Purger(Cog):
    """Delete multiple messages at a time.
    More info: [click here](https://github.com/papiersnipper/modmail-plugins/tree/master/purger)
    """

    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @command()
    @has_permissions(PermissionLevel.MODERATOR)
    async def purge(self, ctx: Context, amount: int) -> None:
        """Delete the specified amount of messages."""
        if amount < 1:
            return

        try:
            deleted = await ctx.channel.purge(limit=amount + 1)
        except Forbidden:
            return await ctx.send("I don't have permission to delete messages here.")

        delete_message: Message = await ctx.send(f"Successfully deleted {len(deleted)} messages!")
        await asyncio.sleep(3)
        await delete_message.delete()


def setup(bot: Bot) -> None:
    """Bot cog load."""
    bot.add_cog(Purger(bot))
