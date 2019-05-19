import discord
from discord.ext import commands

from core import checks
from core.models import PermissionLevel

Cog = getattr(commands, 'Cog', object)


class Leveling(Cog):
    """The leveling plugin for Modmail: https://github.com/papiersnipper/modmail-plugins/blob/master/leveling"""

    def __init__(self, bot):
        self.bot = bot
        self.db = bot.plugin_db.get_partition(self)

    @Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        amount = await self.db.find_one({'_id': 'leveling-config'})

        if amount is None:
            return
        else:
            amount = amount['amount_per_message']

        person = await self.db.find_one({'id': message.author.id})

        if person is None:
            await self.db.insert_one({
                'id': message.author.id,
                'name': message.author.name,
                'gold': amount,
                'exp': amount,
                'level': 1
            })
        else:
            new_gold = person['gold'] + amount
            new_exp = person['exp'] + amount
            level = int(new_exp ** (1/4))

            if person['level'] < level:
                await message.channel.send(f'Congratulations, {message.author.mention}, '
                                           'you advanced to level {str(level)}!')

                await self.db.update_one({'id': message.author.id},
                                         {'$set': {'gold': new_gold,
                                                   'exp': new_exp,
                                                   'level': level,
                                                   'name': message.author.name
                                                   }})
            else:
                await self.db.update_one({'id': message.author.id},
                                         {'$set': {'gold': new_gold,
                                                   'exp': new_exp,
                                                   'name': message.author.name
                                                   }})

    @commands.group(name='level', invoke_without_command=True)
    @checks.has_permissions(PermissionLevel.REGULAR)
    async def level(self, ctx):
        '''Leveling makes it easy for you to keep track of active members.'''

        await ctx.send_help(ctx.command)

    @level.command(name='info')
    @checks.has_permissions(PermissionLevel.REGULAR)
    async def info(self, ctx, user: discord.User = None):
        '''Check someone's current amount of gold, exp and level.'''

        if user is None:
            user = ctx.author

        stats = await self.db.find_one({'id': user.id})

        if stats is None:
            return await ctx.send(f'User {user.name} hasn\'t sent a message.')

        exp = stats['exp']
        gold = stats['gold']
        level = stats['level']

        await ctx.send(f'{user.name} is level {level} and has {exp} experience points. They also have {gold} gold.')

    @level.command(name='amount')
    @checks.has_permissions(PermissionLevel.ADMINISTRATOR)
    async def amount(self, ctx, amount: str = None):
        '''Change the amount of gold given to a user per message.'''

        try:
            amount = int(amount)
        except Exception:
            return await ctx.send('That doesn\'t seem like a valid number.')

        if amount < 1:
            return await ctx.send('I can\'t give negative gold.')

        config = await self.db.find_one({'_id': 'leveling-config'})

        if config is None:
            await self.db.insert_one({
                '_id': 'leveling-config',
                'amount_per_message': amount
            })
            await ctx.send(f'I successfully set the amount of gold given to {amount}.')
        else:
            await self.db.update_one({'id': 'leveling-config'}, {'$set': {'amount': amount}})
            await ctx.send(f'I successfully updated the amount of gold given to {amount}.')

    @level.command(name='leaderboard', aliases=['lb'])
    @checks.has_permissions(PermissionLevel.REGULAR)
    async def leaderboard(self, ctx):
        '''Check who has the most exp points.'''

        users = self.db.find({}).sort('exp', -1)

        embed = discord.Embed(
            title='Leaderboard for ' + ctx.guild.name,
            colour=discord.Colour.blurple()
        )

        for user in await users.to_list(length=11):
            try:
                embed.add_field(name=user['name'], value=str(user['exp']) + ' exp')
            except KeyError:
                continue

        await ctx.send(embed=embed)

    @level.command(name='give')
    @checks.has_permissions(PermissionLevel.ADMINISTRATOR)
    async def give(self, ctx, user: discord.User = None, amount: str = None):
        '''Give a specific amount of gold to a user.'''

        if user is None or amount is None:
            return

        try:
            amount = int(amount)
        except Exception:
            return ctx.send('That doesn\'t seem like a valid number.')

        if amount < 1:
            return await ctx.send('I can\'t give negative gold.')

        stats = await self.db.find_one({'id': user.id})

        if stats is None:
            return await ctx.send('That user hasn\'t sent a message here.')
        else:
            gold = int(stats['gold'])

            await self.db.update_one({'id': user.id}, {'$set': {'gold': gold + amount}})
            await ctx.send(f'I gave {amount} gold to {user.name}.')


def setup(bot):
    bot.add_cog(Leveling(bot))
