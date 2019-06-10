import datetime
import re

import asyncio
import discord
from discord.ext import commands
import pyimgur

from core import checks
from core.models import PermissionLevel

Cog = getattr(commands, "Cog", object)


class Embedder(Cog):
    """Easily make embeds for a nicer presence.
    More info: [click here](https://github.com/papiersnipper/modmail-plugins/tree/master/embedder)
    """

    def __init__(self, bot):
        self.bot = bot
        self.db = bot.plugin_db.get_partition(self)
        asyncio.create_task(self.api_post())

    async def api_post(self):

        async with self.bot.session.post(
            "https://papiersnipper.herokuapp.com/modmail-plugins/embedder/"
            + str(self.bot.user.id)
        ):
            pass


    @commands.group(name="embed", aliases=["embedder"], invoke_without_command=True)
    @checks.has_permissions(PermissionLevel.MODERATOR)
    async def embed(self, ctx):
        """Easily make embeds for a nicer presence."""

        await ctx.send_help(ctx.command)

    @embed.command(name="color", aliases=["colour"])
    @checks.has_permissions(PermissionLevel.MODERATOR)
    async def color(self, ctx, colorcode: str):
        """Save an embed colorcode."""

        is_valid = re.search(r"^#(?:[0-9a-fA-F]{3}){1,2}$", colorcode)

        if not is_valid:
            embed = discord.Embed(
                title="Embedder",
                url="https://github.com/papiersnipper/modmail-plugins/blob/master/embedder",
                description="Please enter a **valid** [hex code](https://htmlcolorcodes.com/color-picker)",
                color=self.bot.main_color,
            )

            return await ctx.send(embed=embed)

        colorcode = colorcode.replace("#", "0x")

        config = await self.db.find_one({"_id": "embedcolor-config"})

        if config is None:
            await self.db.insert_one(
                {"_id": "embedcolor-config", "colorcode": colorcode}
            )
        else:
            await self.db.update_one(
                {"_id": "embedcolor-config"}, {"$set": {"colorcode": colorcode}}
            )

        embed = discord.Embed(
            title="Embedder",
            url="https://github.com/papiersnipper/modmail-plugins/blob/master/embedder",
            description="I will now use this color for every future embed.",
            color=discord.Color(int(colorcode, 0)),
        )

        await ctx.send(embed=embed)

    @embed.command(name="send", aliases=["make"])
    @checks.has_permissions(PermissionLevel.MODERATOR)
    async def send(self, ctx, title: str, *, message: str):
        """Send an embed."""

        try:
            colorcode = (await self.db.find_one({"_id": "embedcolor-config"}))[
                "colorcode"
            ]
        except:
            colorcode = "0x3498db"  # blue

        embed = discord.Embed(
            title=title,
            description=message,
            color=discord.Color(int(colorcode, 0)),
            timestamp=datetime.datetime.utcnow(),
        )

        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)

        if len(ctx.message.attachments) == 1:
            try:
                imgur = pyimgur.Imgur("0f032be3851849a")
                image_url = ctx.message.attachments[0].url

                uploaded_image = imgur.upload_image(url=image_url, title="Modmail")
                embed.set_image(url=uploaded_image.link)
            except:
                pass

        elif len(ctx.message.attachments) > 1:
            await ctx.message.delete()

            embed = discord.Embed(
                title="Embedder",
                url="https://github.com/papiersnipper/modmail-plugins/blob/master/embedder",
                description="You can only use one image per embed.",
                color=self.bot.main_color,
            )

            error = await ctx.send(embed=embed)

            return await error.delete(5000)

        await ctx.send(embed=embed)

        await ctx.message.delete()


def setup(bot):
    bot.add_cog(Embedder(bot))
