import json
import requests
import discord
import random
from asyncio import sleep
from discord.ext import commands
from config import settings
from discord.utils import get

bot = commands.Bot(command_prefix = settings['prefix'])
bot.remove_command( 'help' )
text_filter = ['@everyone']

@bot.event
async def on_ready():
     while True:
          await bot.change_presence(status=discord.Status.idle, activity=discord.Game("| *help"))
          await sleep(10)

@bot.event
async def on_command_error( ctx, error ):
    pass

@bot.command(pass_context=True)
async def help(ctx):
        embed = discord.Embed(title="CatsAreGood", color = 0xff9900)
        embed.add_field( name = 'cat'.format( command_prefix = settings['prefix'] ), value = 'Random cat')
        embed.add_field( name = 'dog'.format( command_prefix = settings['prefix'] ), value = 'Random dog' )
        embed.add_field( name = 'author'.format( command_prefix = settings['prefix'] ), value = 'Send github bot author' ) 
        embed.add_field( name = 'hello'.format( command_prefix = settings['prefix'] ), value = 'Write ur bot welcome you' )
        embed.add_field( name = 'panda'.format( command_prefix = settings['prefix'] ), value = 'Random panda' )
        embed.add_field( name = 'join'.format( command_prefix = settings['prefix'] ), value = 'Bot joined voice')
        embed.add_field( name = 'leave'.format( command_prefix = settings['prefix'] ), value = 'Bot leave voice' )
        embed.add_field( name = 'members'.format( command_prefix = settings['prefix'] ), value = 'member counter' )
        embed.add_field( name = 'penis'.format( command_prefix = settings['prefix'] ), value = 'long your penis' )
        embed.add_field( name = 'clear'.format( command_prefix = settings['prefix'] ), value = 'clear amount messages' )
        await ctx.send(embed = embed)

@bot.command()
async def hello(ctx):
    author = ctx.message.author
    await ctx.send(f'Hello, {author.mention}!')

@bot.command()
async def members(ctx):
    await ctx.send(f'`{ctx.guild.member_count}, Количество человек на сервере`')

@bot.command()
async def penis(ctx):
    penis = "8" + ("=" * random.randint(4, 15)) + "D"
    await ctx.send(penis)

@bot.command()
async def cat(ctx):
    response = requests.get('https://some-random-api.ml/img/cat')
    json_data = json.loads(response.text)

    embed = discord.Embed(color = 0xff9900, title = 'Random cat')
    embed.set_image(url = json_data['link'])
    await ctx.send(embed = embed)

@bot.event
async def on_message( message ):
	await bot.process_commands( message )

	msg = message.content.lower()

	if msg in text_filter:
		await message.delete()
		await message.author.send( f'{ message.author.name}, AXUEL?')

@bot.command()
async def dog(ctx):
    response = requests.get('https://some-random-api.ml/img/dog')
    json_data = json.loads(response.text)

    embed = discord.Embed(color = 0xff9900, title = 'Random dog')
    embed.set_image(url = json_data['link'])
    await ctx.send(embed = embed)

@bot.command()
async def panda(ctx):
    response = requests.get('https://some-random-api.ml/img/panda')
    json_data = json.loads(response.text)

    embed = discord.Embed(color = 0xff9900, title = 'Random panda')
    embed.set_image(url = json_data['link'])
    await ctx.send(embed = embed)

@bot.command()
async def join(ctx):
	global voice
	channel = ctx.message.author.voice.channel
	voice = get(bot.voice_clients, guild = ctx.guild)

	if voice and voice.is_connected():
		await voice.move_to(channel)
	else:
		voice = await channel.connect()
		await ctx.send(f'`Bot connected voice channel: {channel}`')

@bot.command()
async def leave(ctx):
	global voice
	channel = ctx.message.author.voice.channel
	voice = get(bot.voice_clients, guild = ctx.guild)

	if voice and voice.is_connected():
		await voice.disconnect()
		await ctx.send(f"`Bot disconnect voice channel: {channel}`")
	else:
		voice = await channel.connect()

@bot.command()
async def author(ctx):
    embed = discord.Embed(
    	color = 0xff9900,
        title="click on me",
        description="Author github",
        url='https://github.com/CatsAreGood1337',
    )
    await ctx.send(embed=embed)

@bot.command()
@commands.has_permissions( administrator = True )
async def clear( ctx, amount : int ):
	await ctx.channel.purge( limit = amount )

@clear.error
async def clear_error( ctx, error ):
    if isinstance( error, commands.MissingRequiredArgument ):
        await ctx.send(f'`{ctx.author.name}, укажите аргумент`')

    if isinstance( error, commands.MissingPermissions ):
        await ctx.send(f'{ctx.author.name}, Вы не имеете  право использовать данную комманду!')

bot.run(settings['token'])