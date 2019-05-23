import asyncio
import discord
import os
from datetime import datetime
from discord.ext import commands

from core import checks
from core.models import PermissionLevel

Cog = getattr(commands, 'Cog', object)


class RoleAssignment(Cog):
    """Assign roles using reactions.
    More info: [click here](https://github.com/papiersnipper/modmail-plugins/tree/master/role-assignment)
    """

    def __init__(self, bot):
        self.bot: discord.Client = bot
        self.db = bot.plugin_db.get_partition(self)
        self.ids = dict()

    async def update_db(self):
        await self.db.find_one_and_update(
            {"_id": "role-config"},
            {"$set": {"ids": self.ids}},
            upsert=True
        )

    async def _set_db(self):
        config = await self.db.find_one({'_id': 'role-config'})

        if config is None:
            return

        self.ids = dict(config.get("ids", {}))
    
    @commands.group(name='role', aliases=['roles'], invoke_without_command=True)
    @checks.has_permissions(PermissionLevel.ADMINISTRATOR)
    async def role(self, ctx):
        """Automaticly assign roles when you click on the emoji."""

        await ctx.send_help(ctx.command)

    @role.command(name='add')
    @checks.has_permissions(PermissionLevel.ADMINISTRATOR)
    async def add(self, ctx, emoji: discord.Emoji, *, role: discord.Role):
        """Add a clickable emoji to each new message."""

        config = await self.db.find_one({'_id': 'role-config'})

        if config is None:
            await self.db.insert_one({
                '_id': 'role-config',
                'emoji': {}
            })

            config = await self.db.find_one({'_id': 'role-config'})
        
        emoji_dict = config['emoji']

        try:
            emoji_dict[str(emoji.id)]
            failed = True
        except KeyError:
            failed = False
        
        if failed:
            return await ctx.send('That emoji already assigns a role.')
        
        emoji_dict[f'<:{emoji.name}:{emoji.id}>'] = role.name

        await self.db.update_one({'_id': 'role-config'}, {'$set': {'emoji': emoji_dict}})

        await ctx.send(f'I successfully pointed <:{emoji.name}:{emoji.id}> to "{role.name}"')
    
    @role.command(name='remove')
    @checks.has_permissions(PermissionLevel.ADMINISTRATOR)
    async def remove(self, ctx, emoji: discord.Emoji):
        """Remove a clickable emoji from each new message."""

        config = await self.db.find_one({'_id': 'role-config'})

        if config is None:
            return await ctx.send('There are no emoji set for this server.')
        
        emoji_dict = config['emoji']

        try:
            del emoji_dict[f'<:{emoji.name}:{emoji.id}>']
        except KeyError:
            return await ctx.send('That emoji is not configured')

        await self.db.update_one({'_id': 'role-config'}, {'$set': {'emoji': emoji_dict}})

        await ctx.send(f'I successfully deleted <:{emoji.name}:{emoji.id}>.')

    @Cog.listener()
    async def on_thread_ready(self, thread):
        message = thread.genesis_message

        for k, v in (await self.db.find_one({'_id': 'role-config'}))['emoji'].items():
            await message.add_reaction(k)

        self.ids[str(message.id)] = str(message.channel.id)
        await self.update_db()

    @Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):

        if str(payload.message_id) not in self.ids:
            return

        guild_id = payload.guild_id
        guild: discord.Guild = discord.utils.find(lambda g : g.id == guild_id, self.bot.guilds)

        if payload.user_id == self.bot.user.id:
            return

        member_id = int(guild.get_channel(payload.channel_id).topic[9:])

        role = (await self.db.find_one({'_id': 'role-config'}))['emoji'][f'<:{payload.emoji.name}:{payload.emoji.id}>']

        role = discord.utils.get(guild.roles, name=role)

        if role is None:
            await guild.get_channel(payload.channel_id).send('Configured role not found.')
            return

        for m in guild.members:
            if m.id == member_id:
                member = m
            else:
                continue

        await member.add_roles(role)
        await guild.get_channel(payload.channel_id).send(f'Successfully added {role} to {member.name}')

    @Cog.listener()
    async def on_raw_reaction_remove(self, payload):

        if str(payload.message_id) not in self.ids:
            return

        guild_id = payload.guild_id
        guild = discord.utils.find(lambda g : g.id == guild_id, self.bot.guilds)

        member_id = int(guild.get_channel(payload.channel_id).topic[9:])

        role = (await self.db.find_one({'_id': 'role-config'}))['emoji'][f'<:{payload.emoji.name}:{payload.emoji.id}>']

        role = discord.utils.get(guild.roles, name=role)

        if role is None:
            await guild.get_channel(payload.channel_id).send('Configured role not found.')
            return

        for m in guild.members:
            if m.id == member_id:
                member = m
            else:
                continue

        await member.remove_roles(role)
        await guild.get_channel(payload.channel_id).send(f'Successfully removed {role} from {member.name}')

    @Cog.listener()
    async def on_guild_channel_delete(self,channel):
        if isinstance(channel, discord.TextChannel):
            if channel.category_id != self.bot.config.get('main_category_id'):
                return

            for msg_id, channel_id in self.ids.items():
                if channel_id == str(channel.id):
                    self.ids.pop(msg_id)
                    await self.update_db()



    @Cog.listener()
    async def on_plugin_ready(self):
        asyncio.create_task(self._set_db())
        await asyncio.sleep(30)
        guild: discord.Guild = self.bot.get_guild(int(os.getenv("GUILD_ID")))

        category: discord.CategoryChannel = guild.get_channel(int(self.bot.config.get('main_category_id')))

        # if category is None:
        #     return

        for c in category.channels:
            if isinstance(c,discord.TextChannel):
                if "User ID: " not in c.topic:
                    return
                messages = await c.history(oldest_first=True).flatten()
                if str(messages[0].id) not in self.ids:
                    self.ids[str(messages[0].id)] = str(c.id)



def setup(bot):
    bot.add_cog(RoleAssignment(bot))
