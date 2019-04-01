import discord
from discord.ext import commands
from discord.ext.commands import has_permissions


class Autorole:
    """The autorole plugin for Modmail: https://github.com/papiersnipper/modmail-plugins/autorole"""

    def __init__(self, bot):
        self.bot = bot
        self.db = bot.plugin_db.get_partition(self)

    async def on_member_join(self, member):
        rolename = (await self.db.find_one({'_id': 'autorole-config'}))['rolename']

        if rolename is None:
            return
        else:
            role = discord.utils.get(member.guild.roles, name=rolename)
            await member.add_roles(role)

    @commands.command()
    @has_permissions(administrator=True)
    async def setrole(self, ctx, rolename: str = None):
        """Sets the default role a member gets when joining."""

        role = discord.utils.get(ctx.author.guild.roles, name=rolename)

        if role is None:
            return await ctx.send('I couldn\'t find that role. Make sure to check the capitalisation.')

        try:
            self.db.delete_one({'_id': 'autorole-config'})

            self.db.insert_one({
                '_id': 'autorole-config',
                'rolename': role.name
            })
        except Exception:
            self.db.insert_one({
                '_id': 'autorole-config',
                'rolename': role.name
            })

        await ctx.send('I will now give that role to all new members!')

    @commands.command()
    @has_permissions(administrator=True)
    async def giveroles(self, ctx, rolename: str = None):
        """Gives all members of the server this role"""

        if rolename is None:
            rolename = (await self.db.find_one({'_id': 'autorole-config'}))['rolename']
            if rolename is None:
                return await ctx.send('Please supply a role, or set one with the `setrole` command.')

        role = discord.utils.get(ctx.author.guild.roles, name=rolename)

        if role is None:
            return await ctx.send('I couldn\'t find that role. Make sure to check the capitalisation.')

        users = 0
        for member in ctx.guild.members:
            if role.id in [role.id for role in member.roles]:
                continue
            else:
                await member.add_roles(role)
                users = users + 1

        await ctx.send(f'Added {role.name} for {users} members.')


def setup(bot):
    bot.add_cog(Autorole(bot))
