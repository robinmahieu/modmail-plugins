import datetime
import discord
import pyimgur
import re
from discord.ext import commands
from discord.ext.commands import has_permissions

Cog = getattr(commands, 'Cog', object)


class Embedder(Cog):
    """The embedder plugin for Modmail: https://github.com/papiersnipper/modmail-plugins/blob/master/embedder"""

    def __init__(self, bot):
        self.bot = bot
        self.db = bot.plugin_db.get_partition(self)

    @commands.command()
    @has_permissions(manage_messages=True)
    async def embedcolor(self, ctx, colorcode: str = None):
        """Saves the colorcode and will use them in the next embeds."""

        if colorcode is None:
            return await ctx.send('Please enter a hex colorcode')

        is_valid = re.search(r'^#(?:[0-9a-fA-F]{3}){1,2}$', str(colorcode))

        if not is_valid:
            await ctx.send('Please enter a **valid** hex colorcode')
        else:
            colorcode = colorcode.replace('#', '0x')
            try:
                self.db.delete_one({'_id': 'embedcolor-config'})

                self.db.insert_one({
                    '_id': 'embedcolor-config',
                    'colorcode': colorcode
                })
            except Exception:
                self.db.insert_one({
                    '_id': 'embedcolor-config',
                    'colorcode': colorcode
                })

            embed = discord.Embed(
                title="New Color!",
                description="I will now use this color for every embed.",
                color=discord.Color(int(colorcode, 0))
            )

            await ctx.send(embed=embed)

    @commands.command()
    @has_permissions(manage_messages=True)
    async def embed(self, ctx, title: str = None, *, message: str = None):
        """Sends an embed to the channel where you used the command."""

        if title is None:
            return await ctx.send('Please enter a title between double quotes.')

        if message is None:
            return await ctx.send('Please enter a message.')

        try:
            colorcode = (await self.db.find_one({'_id': 'embedcolor-config'}))['colorcode']
        except Exception:
            colorcode = '0x3498db'  # blue

        embed = discord.Embed(
            title=title,
            description=message,
            color=discord.Color(int(colorcode, 0)),
            timestamp=datetime.datetime.utcnow()
            )

        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.avatar_url)

        if len(ctx.message.attachments) == 1:
            try:
                imgur = pyimgur.Imgur('0f032be3851849a')
                image_url = ctx.message.attachments[0].url

                uploaded_image = imgur.upload_image(url=image_url, title='Modmail')
                embed.set_image(url=uploaded_image.link)

            except Exception:
                pass

        elif len(ctx.message.attachments) > 1:
            await ctx.message.delete()
            error = await ctx.send('You can only use one image per embed.')
            return await error.delete(5000)

        await ctx.send(embed=embed)
        await ctx.message.delete()


def setup(bot):
    bot.add_cog(Embedder(bot))
