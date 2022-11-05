import datetime

import discord
from discord.ext import commands, tasks

from core import checks
from core.models import PermissionLevel, getLogger
from core.time import UserFriendlyTime

logger = getLogger(__name__)


class StaleAlert(commands.Cog):
    """Plugin to alert when tickets are going stale."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

        self.db = self.bot.api.get_plugin_partition(self)

    async def cog_load(self):
        self.check_threads_loop.start()

    @tasks.loop(minutes=5)
    async def check_threads_loop(self):
        """Function that executes every five minutes.

        It checks every open thread to see if the last sent message in
        the channel was sent earlier than the configured time duration.
        If so, it will send the configured alert message and make a
        note entry in the logs.
        """
        config = await self.db.find_one({"_id": "stale-alert-config"})

        if not config:
            return

        try:
            duration = config["duration"]
        except KeyError:
            return logger.error(
                "Something went wrong in the database! The `duration` field "
                "could not be found in the configuration file."
            )

        message = config.get("message", "alert")

        open_threads = await self.bot.api.get_open_logs()

        counter = 0

        for thread in open_threads:
            most_recent_message = None

            for thread_message in thread["messages"]:
                if thread_message["type"] == "thread_message":
                    most_recent_message = thread_message

            if most_recent_message["author"]["mod"]:
                continue

            timestamp = datetime.datetime.fromisoformat(
                most_recent_message["timestamp"]
            ).astimezone(datetime.timezone.utc)

            delta = (discord.utils.utcnow() - timestamp).total_seconds()

            if delta > duration:
                channel = self.bot.get_channel(int(thread["channel_id"]))
                recipient = self.bot.get_user(int(thread["recipient"]["id"]))

                if not channel:
                    return logger.warning(
                        "Found an open thread without a valid channel ID: "
                        f"{thread['key']}."
                    )

                if not recipient:
                    return logger.warning(
                        "Found an open thread without a valid recipient ID: "
                        f"{thread['key']}."
                    )

                sent_message = await channel.send(message)
                await self.bot.api.append_log(sent_message, type_="system")

                counter += 1

        logger.debug(f"Sent {counter} stale alert(s).")

    @check_threads_loop.before_loop
    async def before_check_threads_loop(self):
        await self.bot.wait_for_connected()

    @commands.group(name="stale", invoke_without_command=True)
    @checks.has_permissions(PermissionLevel.SUPPORTER)
    async def stale(self, ctx: commands.Context):
        """Alert when tickets are going stale."""

        await ctx.send_help(ctx.command)

    @stale.command(name="message")
    @checks.has_permissions(PermissionLevel.MODERATOR)
    async def stale_message(
        self, ctx: commands.Context, *, message: str = None
    ):
        """Set the message to send when a ticket is considered stale."""

        if not message:
            return await ctx.send_help(ctx.command)

        config = await self.db.find_one({"_id": "stale-alert-config"})

        if not config:
            await self.db.insert_one({"_id": "stale-alert-config"})

        await self.db.find_one_and_update(
            {"_id": "stale-alert-config"}, {"$set": {"message": message}}
        )

        embed = discord.Embed(
            title="Stale Alert",
            color=self.bot.main_color,
            description=f"The alert message was set to `{message}`.",
        )

        await ctx.send(embed=embed)

    @stale.command(name="time")
    @checks.has_permissions(PermissionLevel.MODERATOR)
    async def stale_time(
        self, ctx: commands.Context, *, duration: UserFriendlyTime = None
    ):
        """Set the time before a ticket is considered stale."""

        if not duration:
            return await ctx.send_help(ctx.command)

        config = await self.db.find_one({"_id": "stale-alert-config"})

        if not config:
            await self.db.insert_one({"_id": "stale-alert-config"})

        seconds = (duration.dt - duration.now).total_seconds()

        await self.db.find_one_and_update(
            {"_id": "stale-alert-config"}, {"$set": {"duration": seconds}}
        )

        embed = discord.Embed(
            title="Stale Alert",
            color=self.bot.main_color,
            description=f"The time duration was set to {seconds} seconds.",
        )

        await ctx.send(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(StaleAlert(bot))
