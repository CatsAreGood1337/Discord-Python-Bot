import json, requests, discord, random, asyncio
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
        embed.add_field( name = 'buy'.format( command_prefix = settings['prefix'] ), value = 'create new ticket' )
        embed.add_field( name = 'close'.format( command_prefix = settings['prefix'] ), value = 'close you own ticket' )
        await ctx.send(embed = embed)

@bot.command()
async def hello(ctx):
    author = ctx.message.author
    await ctx.send(f'Hello, {author.mention}!')

@bot.command()
async def buy(ctx, *, args = None):

    await bot.wait_until_ready()

    if args == None:
        message_content = "Подождите, мы скоро будем с вами!"
    
    else:
        message_content = "".join(args)

    with open("data.json") as f:
        data = json.load(f)

    ticket_number = int(data["ticket-counter"])
    ticket_number += 1

    ticket_channel = await ctx.guild.create_text_channel("ticket-{}".format(ticket_number))
    await ticket_channel.set_permissions(ctx.guild.get_role(ctx.guild.id), send_messages=False, read_messages=False)

    for role_id in data["valid-roles"]:
        role = ctx.guild.get_role(role_id)

        await ticket_channel.set_permissions(role, send_messages=True, read_messages=True, add_reactions=True, embed_links=True, attach_files=True, read_message_history=True, external_emojis=True)
    
    await ticket_channel.set_permissions(ctx.author, send_messages=True, read_messages=True, add_reactions=True, embed_links=True, attach_files=True, read_message_history=True, external_emojis=True)

    em = discord.Embed(title="Новый тикет создан {}#{}".format(ctx.author.name, ctx.author.discriminator), description= "{}".format(message_content), color=0x00a8ff)

    await ticket_channel.send(embed=em)

    pinged_msg_content = ""
    non_mentionable_roles = []

    if data["pinged-roles"] != []:

        for role_id in data["pinged-roles"]:
            role = ctx.guild.get_role(role_id)

            pinged_msg_content += role.mention
            pinged_msg_content += " "

            if role.mentionable:
                pass
            else:
                await role.edit(mentionable=True)
                non_mentionable_roles.append(role)
        
        await ticket_channel.send(pinged_msg_content)

        for role in non_mentionable_roles:
            await role.edit(mentionable=False)
    
    data["ticket-channel-ids"].append(ticket_channel.id)

    data["ticket-counter"] = int(ticket_number)
    with open("data.json", 'w') as f:
        json.dump(data, f)
    
    created_em = discord.Embed(title="CatsAreGood", description="Ваш тикет создан {}".format(ticket_channel.mention), color=0x00a8ff)
    
    await ctx.send(embed=created_em)

@bot.command()
async def close(ctx):
    with open('data.json') as f:
        data = json.load(f)

    if ctx.channel.id in data["ticket-channel-ids"]:

        channel_id = ctx.channel.id

        def check(message):
            return message.author == ctx.author and message.channel == ctx.channel and message.content.lower() == "close"

        try:

            em = discord.Embed(title="Вы закрыли тикет", description="Вы уверены, что хотите закрыть этот тикет? Ответьте close, если уверены.", color=0x00a8ff)
        
            await ctx.send(embed=em)
            await bot.wait_for('message', check=check, timeout=60)
            await ctx.channel.delete()

            index = data["ticket-channel-ids"].index(channel_id)
            del data["ticket-channel-ids"][index]

            with open('data.json', 'w') as f:
                json.dump(data, f)
        
        except asyncio.TimeoutError:
            em = discord.Embed(title="CatsAreGood", description="Вы не успели закрыть эту заявку. Пожалуйста, запустите команду еще раз.", color=0x00a8ff)
            await ctx.send(embed=em)

@bot.command()
@commands.has_permissions( administrator = True )
async def addaccess(ctx, role_id=None):

    with open('data.json') as f:
        data = json.load(f)
    
    valid_user = False

    for role_id in data["verified-roles"]:
        try:
            if ctx.guild.get_role(role_id) in ctx.author.roles:
                valid_user = True
        except:
            pass
    
    if valid_user or ctx.author.guild_permissions.administrator:
        role_id = int(role_id)

        if role_id not in data["valid-roles"]:

            try:
                role = ctx.guild.get_role(role_id)

                with open("data.json") as f:
                    data = json.load(f)

                data["valid-roles"].append(role_id)

                with open('data.json', 'w') as f:
                    json.dump(data, f)
                
                em = discord.Embed(title="Auroris Tickets", description="You have successfully added `{}` to the list of roles with access to tickets.".format(role.name), color=0x00a8ff)

                await ctx.send(embed=em)

            except:
                em = discord.Embed(title="Auroris Tickets", description="That isn't a valid role ID. Please try again with a valid role ID.")
                await ctx.send(embed=em)
        
        else:
            em = discord.Embed(title="Auroris Tickets", description="That role already has access to tickets!", color=0x00a8ff)
            await ctx.send(embed=em)
    
    else:
        em = discord.Embed(title="Auroris Tickets", description="Sorry, you don't have permission to run that command.", color=0x00a8ff)
        await ctx.send(embed=em)

@bot.command()
@commands.has_permissions( administrator = True )
async def delaccess(ctx, role_id=None):
    with open('data.json') as f:
        data = json.load(f)
    
    valid_user = False

    for role_id in data["verified-roles"]:
        try:
            if ctx.guild.get_role(role_id) in ctx.author.roles:
                valid_user = True
        except:
            pass

    if valid_user or ctx.author.guild_permissions.administrator:

        try:
            role_id = int(role_id)
            role = ctx.guild.get_role(role_id)

            with open("data.json") as f:
                data = json.load(f)

            valid_roles = data["valid-roles"]

            if role_id in valid_roles:
                index = valid_roles.index(role_id)

                del valid_roles[index]

                data["valid-roles"] = valid_roles

                with open('data.json', 'w') as f:
                    json.dump(data, f)

                em = discord.Embed(title="Auroris Tickets", description="You have successfully removed `{}` from the list of roles with access to tickets.".format(role.name), color=0x00a8ff)

                await ctx.send(embed=em)
            
            else:
                
                em = discord.Embed(title="Auroris Tickets", description="That role already doesn't have access to tickets!", color=0x00a8ff)
                await ctx.send(embed=em)

        except:
            em = discord.Embed(title="Auroris Tickets", description="That isn't a valid role ID. Please try again with a valid role ID.")
            await ctx.send(embed=em)
    
    else:
        em = discord.Embed(title="Auroris Tickets", description="Sorry, you don't have permission to run that command.", color=0x00a8ff)
        await ctx.send(embed=em)

@bot.command()
@commands.has_permissions( administrator = True )
async def addpingedrole(ctx, role_id=None):

    with open('data.json') as f:
        data = json.load(f)
    
    valid_user = False

    for role_id in data["verified-roles"]:
        try:
            if ctx.guild.get_role(role_id) in ctx.author.roles:
                valid_user = True
        except:
            pass
    
    if valid_user or ctx.author.guild_permissions.administrator:

        role_id = int(role_id)

        if role_id not in data["pinged-roles"]:

            try:
                role = ctx.guild.get_role(role_id)

                with open("data.json") as f:
                    data = json.load(f)

                data["pinged-roles"].append(role_id)

                with open('data.json', 'w') as f:
                    json.dump(data, f)

                em = discord.Embed(title="Auroris Tickets", description="You have successfully added `{}` to the list of roles that get pinged when new tickets are created!".format(role.name), color=0x00a8ff)

                await ctx.send(embed=em)

            except:
                em = discord.Embed(title="Auroris Tickets", description="That isn't a valid role ID. Please try again with a valid role ID.")
                await ctx.send(embed=em)
            
        else:
            em = discord.Embed(title="Auroris Tickets", description="That role already receives pings when tickets are created.", color=0x00a8ff)
            await ctx.send(embed=em)
    
    else:
        em = discord.Embed(title="Auroris Tickets", description="Sorry, you don't have permission to run that command.", color=0x00a8ff)
        await ctx.send(embed=em)

@bot.command()
@commands.has_permissions( administrator = True )
async def delpingedrole(ctx, role_id=None):

    with open('data.json') as f:
        data = json.load(f)
    
    valid_user = False

    for role_id in data["verified-roles"]:
        try:
            if ctx.guild.get_role(role_id) in ctx.author.roles:
                valid_user = True
        except:
            pass
    
    if valid_user or ctx.author.guild_permissions.administrator:

        try:
            role_id = int(role_id)
            role = ctx.guild.get_role(role_id)

            with open("data.json") as f:
                data = json.load(f)

            pinged_roles = data["pinged-roles"]

            if role_id in pinged_roles:
                index = pinged_roles.index(role_id)

                del pinged_roles[index]

                data["pinged-roles"] = pinged_roles

                with open('data.json', 'w') as f:
                    json.dump(data, f)

                em = discord.Embed(title="Auroris Tickets", description="You have successfully removed `{}` from the list of roles that get pinged when new tickets are created.".format(role.name), color=0x00a8ff)
                await ctx.send(embed=em)
            
            else:
                em = discord.Embed(title="Auroris Tickets", description="That role already isn't getting pinged when new tickets are created!", color=0x00a8ff)
                await ctx.send(embed=em)

        except:
            em = discord.Embed(title="Auroris Tickets", description="That isn't a valid role ID. Please try again with a valid role ID.")
            await ctx.send(embed=em)
    
    else:
        em = discord.Embed(title="Auroris Tickets", description="Sorry, you don't have permission to run that command.", color=0x00a8ff)
        await ctx.send(embed=em)


@bot.command()
@commands.has_permissions( administrator = True )
async def addadminrole(ctx, role_id=None):

    try:
        role_id = int(role_id)
        role = ctx.guild.get_role(role_id)

        with open("data.json") as f:
            data = json.load(f)

        data["verified-roles"].append(role_id)

        with open('data.json', 'w') as f:
            json.dump(data, f)
        
        em = discord.Embed(title="Auroris Tickets", description="You have successfully added `{}` to the list of roles that can run admin-level commands!".format(role.name), color=0x00a8ff)
        await ctx.send(embed=em)

    except:
        em = discord.Embed(title="Auroris Tickets", description="That isn't a valid role ID. Please try again with a valid role ID.")
        await ctx.send(embed=em)

@bot.command()
@commands.has_permissions( administrator = True )
async def deladminrole(ctx, role_id=None):
    try:
        role_id = int(role_id)
        role = ctx.guild.get_role(role_id)

        with open("data.json") as f:
            data = json.load(f)

        admin_roles = data["verified-roles"]

        if role_id in admin_roles:
            index = admin_roles.index(role_id)

            del admin_roles[index]

            data["verified-roles"] = admin_roles

            with open('data.json', 'w') as f:
                json.dump(data, f)
            
            em = discord.Embed(title="Auroris Tickets", description="You have successfully removed `{}` from the list of roles that get pinged when new tickets are created.".format(role.name), color=0x00a8ff)

            await ctx.send(embed=em)
        
        else:
            em = discord.Embed(title="Auroris Tickets", description="That role isn't getting pinged when new tickets are created!", color=0x00a8ff)
            await ctx.send(embed=em)

    except:
        em = discord.Embed(title="Auroris Tickets", description="That isn't a valid role ID. Please try again with a valid role ID.")
        await ctx.send(embed=em)

@bot.command()
async def members(ctx):
    await ctx.send(f':cat: Количество человек на сервере `{ctx.guild.member_count}`')

@bot.command() #1
async def penis(ctx):
    penis = "8" + ("=" * random.randint(5, 20)) + "D"
    await ctx.send(penis)

@bot.command() #1
async def bebra(ctx):
    bebra = "(o)"
    await ctx.send(bebra)

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

@commands.has_permissions( administrator = True )
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