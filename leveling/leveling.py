import discord
from discord.ext import commands

from core import checks
from core.models import PermissionLevel

Cog = getattr(commands, "Cog", object)


class Leveling(Cog):
    """A leveling system for your server: see who's active and who's not.
    More info: [click here](https://github.com/papiersnipper/modmail-plugins/tree/master/leveling)
    """

    def __init__(self, bot):
        self.bot = bot
        self.db = bot.plugin_db.get_partition(self)

    @Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        config = await self.db.find_one({"_id": "leveling-config"})

        if config is None:
            return

        amount = config["amount_per_message"]

        person = await self.db.find_one({"id": message.author.id})

        if person is None:
            await self.db.insert_one(
                {
                    "id": message.author.id,
                    "name": message.author.name,
                    "gold": amount,
                    "exp": amount,
                    "level": 1,
                }
            )
        else:
            new_gold = person["gold"] + amount
            new_exp = person["exp"] + amount
            level = int(new_exp ** (1 / 4))

            if person["level"] < level:
                await message.channel.send(
                    f"Congratulations, {message.author.mention}, "
                    f"you advanced to level {level}!"
                )

                await self.db.update_one(
                    {"id": message.author.id},
                    {
                        "$set": {
                            "gold": new_gold,
                            "exp": new_exp,
                            "level": level,
                            "name": message.author.name,
                        }
                    },
                )
            else:
                await self.db.update_one(
                    {"id": message.author.id},
                    {
                        "$set": {
                            "gold": new_gold,
                            "exp": new_exp,
                            "name": message.author.name,
                        }
                    },
                )

    @commands.group(name="level", invoke_without_command=True)
    @checks.has_permissions(PermissionLevel.REGULAR)
    async def level(self, ctx):
        """A leveling system for your server: see who's active and who's not."""

        await ctx.send_help(ctx.command)

    @level.command(name="info")
    @checks.has_permissions(PermissionLevel.REGULAR)
    async def info(self, ctx, user: discord.User = None):
        """Check someone's current amount of gold, exp and level."""

        if user is None:
            user = ctx.author

        stats = await self.db.find_one({"id": user.id})

        if stats is None:
            embed = discord.Embed(
                title="Leveling",
                url="https://github.com/papiersnipper/modmail-plugins/blob/master/leveling",
                description=f"User {user.name} hasn't sent a single message here.",
                color=self.bot.main_color,
            )

            return await ctx.send(embed=embed)

        embed = discord.Embed(
            title="Leveling",
            url="https://github.com/papiersnipper/modmail-plugins/blob/master/leveling",
            description=f"{user.name} is level "
            + str(stats["level"])
            + " and has "
            + str(stats["exp"])
            + " experience points. They also have "
            + str(stats["gold"])
            + " gold.",
            color=self.bot.main_color,
        )

        await ctx.send(embed=embed)

    @level.command(name="amount")
    @checks.has_permissions(PermissionLevel.ADMINISTRATOR)
    async def amount(self, ctx, amount):
        """Change the amount of gold given to a user per message."""

        try:
            amount = int(amount)
        except ValueError:
            embed = discord.Embed(
                title="Leveling",
                url="https://github.com/papiersnipper/modmail-plugins/blob/master/leveling",
                description="That doesn't look like a valid number.",
                color=self.bot.main_color,
            )

            return await ctx.send(embed=embed)

        if amount < 1:
            embed = discord.Embed(
                title="Leveling",
                url="https://github.com/papiersnipper/modmail-plugins/blob/master/leveling",
                description="I can't give negative gold.",
                color=self.bot.main_color,
            )

            return await ctx.send(embed=embed)

        config = await self.db.find_one({"_id": "leveling-config"})

        if config is None:
            await self.db.insert_one(
                {"_id": "leveling-config", "amount_per_message": amount}
            )
            embed = discord.Embed(
                title="Leveling",
                url="https://github.com/papiersnipper/modmail-plugins/blob/master/leveling",
                description=f"I set the amount of gold given to {amount}.",
                color=self.bot.main_color,
            )

            await ctx.send(embed=embed)
        else:
            await self.db.update_one(
                {"id": "leveling-config"}, {"$set": {"amount": amount}}
            )
            embed = discord.Embed(
                title="Leveling",
                url="https://github.com/papiersnipper/modmail-plugins/blob/master/leveling",
                description=f"I updated the amount of gold given to {amount}.",
                color=self.bot.main_color,
            )

            await ctx.send(embed=embed)

    @level.command(name="leaderboard", aliases=["lb"])
    @checks.has_permissions(PermissionLevel.REGULAR)
    async def leaderboard(self, ctx):
        """Check who has the most experience points."""

        users = self.db.find({}).sort("exp", -1)

        embed = discord.Embed(
            title="Leaderboard for " + ctx.guild.name, colour=discord.Colour.blurple(),
            url="https://github.com/papiersnipper/modmail-plugins/blob/master/leveling",
        )

        for user in await users.to_list(length=11):
            try:
                embed.add_field(name=user["name"], value=str(user["exp"]) + " exp")
            except KeyError:
                continue

        await ctx.send(embed=embed)

    @level.command(name="give")
    @checks.has_permissions(PermissionLevel.ADMINISTRATOR)
    async def give(self, ctx, user: discord.User, amount):
        """Give a specific amount of gold to a user."""

        try:
            amount = int(amount)
        except ValueError:
            embed = discord.Embed(
                title="Leveling",
                url="https://github.com/papiersnipper/modmail-plugins/blob/master/leveling",
                description="That doesn't look like a valid number.",
                color=self.bot.main_color,
            )

            return await ctx.send(embed=embed)

        if amount < 1:
            embed = discord.Embed(
                title="Leveling",
                url="https://github.com/papiersnipper/modmail-plugins/blob/master/leveling",
                description="I can't give negative gold.",
                color=self.bot.main_color,
            )

            return await ctx.send(embed=embed)

        stats = await self.db.find_one({"id": user.id})

        if stats is None:
            embed = discord.Embed(
                title="Leveling",
                url="https://github.com/papiersnipper/modmail-plugins/blob/master/leveling",
                description=f"User {user.name} hasn't sent a single message here.",
                color=self.bot.main_color,
            )

            return await ctx.send(embed=embed)

        gold = int(stats["gold"])

        await self.db.update_one({"id": user.id}, {"$set": {"gold": gold + amount}})

        embed = discord.Embed(
            title="Leveling",
            url="https://github.com/papiersnipper/modmail-plugins/blob/master/leveling",
            description=f"I gave {amount} gold to {user.name}",
            color=self.bot.main_color,
        )

        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Leveling(bot))
