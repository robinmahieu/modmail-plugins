import asyncio
import discord
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
        self.bot = bot
        self.db = bot.plugin_db.get_partition(self)
        self.ids = dict()
        asyncio.create_task(self._set_db())

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

    @role.command(aliases=["setlogs","setlog"])
    @checks.has_permissions(PermissionLevel.ADMINISTRATOR)
    async def log(self, ctx, channel: discord.TextChannel):
        """
        ( Optional )
        Set a channel to log who added role to the user.

        **Usage:**
        log #channel
        """
        await self.db.find_one_and_update(
            {"_id": "config"},
            {"$set": {"log": str(channel.id)}},
            upsert=True
        )

        await ctx.send(f'Done! Logs would be sent in {channel.mention}!')

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

        config = (await self.db.find_one({'_id': 'config'}))
        if config is None or config['log'] is None:
            return
        try:
            user = await self.bot.fetch_user(payload.user_id)
            channel = guild.get_channel(int(config))
            if channel is None:
                return
            embed = discord.Embed(
                color=discord.Colour.green(),
                timestamp=datetime.utcnow()
            )

            embed.set_author(name=f"Role Added | {member.name}#{member.discriminator}", icon_url=member.avatar_url)
            embed.add_field(name="Added By", value=f'{user.name}#{user.discriminator}')

            await channel.send(embed=embed)
        except Exception as e:
            raise e

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

        config = (await self.db.find_one({'_id': 'config'}))
        if config is None or config['log'] is None:
            return
        try:
            user = await self.bot.fetch_user(payload.user_id)
            channel = guild.get_channel(int(config))
            if channel is None:
                return
            embed = discord.Embed(
                color=discord.Colour.red(),
                timestamp=datetime.utcnow()
            )

            embed.set_author(name=f"Role Removed | {member.name}#{member.discriminator}", icon_url=member.avatar_url)
            embed.add_field(name="Removed By", value=f'{user.name}#{user.discriminator}')

            await channel.send(embed=embed)
        except Exception as e:
            raise e

    @Cog.listener()
    async def on_guild_channel_delete(self,channel):

        # Here, we check if the channel is a text channel
        if isinstance(channel, discord.TextChannel):

            # We check if the deleted channel is a thread channel or not, if it isn't in the main category, we return
            if channel.category_id != self.bot.config.get('main_category_id'):
                return

            # Further Code ..
            for msg_id, channel_id in self.ids.items():
                if channel_id == str(channel.id):
                    self.ids.pop(msg_id)
                    await self.update_db()

def setup(bot):
    bot.add_cog(RoleAssignment(bot))
