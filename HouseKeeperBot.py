import aiohttp
import discord
from discord import app_commands
import os
import math
#from keep_alive import keep_alive
from office_quotes import officeQuotes
from throw import throwItems
import random
#from discord_token import DiscordToken
from archipelago import Archi
#from replit import db


Token = os.getenv('DISCORD_TOKEN')
GUILD_ID = os.getenv('DISCORD_GUILD_ID')
MY_GUILD = discord.Object(id=GUILD_ID)

class MyClient(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        # A CommandTree is a special type that holds all the application command
        # state required to make it work. This is a separate class because it
        # allows all the extra state to be opt-in.
        # Whenever you want to work with application commands, your tree is used
        # to store and work with them.
        # Note: When using commands.Bot instead of discord.Client, the bot will
        # maintain its own tree instead.
        self.tree = app_commands.CommandTree(self)

    # In this basic example, we just synchronize the app commands to one guild.
    # Instead of specifying a guild to every command, we copy over our global commands instead.
    # By doing so, we don't have to wait up to an hour until they are shown to the end-user.
    async def setup_hook(self):
        # This copies the global commands over to your guild.
        self.tree.copy_global_to(guild=MY_GUILD)
        await self.tree.sync(guild=MY_GUILD)


intents = discord.Intents.all()
intents.members = True
#client = discord.Client(intents=intents)
client = MyClient(intents=intents)


@client.event
async def on_ready():
  print('We have logged in as {0.user}'.format(client))

@client.tree.command()
async def hello(interaction: discord.Interaction):
    """Says hello!"""
    await interaction.response.send_message(f'Hi, {interaction.user.mention}\nHow are you?')

@client.tree.command()
@app_commands.describe(
    room='This can be the room key or the room url',
    seed='(optional) This can be the seed key or the seed url',
)
async def share_multiworld(interaction: discord.Interaction, room: str, seed: str = None):
    """Testing of Embeds"""
    archi = Archi(room, seed)
    embed = discord.Embed()
    footer = None
    if archi.roomValid:
        embed.set_author(name='Archipelago', url="https://archipelago.gg/")
        embed.title = 'Room Information:'
        embed.color = discord.Color.green()
        embed.url = archi.roomUrl
        description = "Room Number: " + archi.roomNum
        description = description + "\nRoom URL: " + f"[Click Here]({archi.roomUrl})"
        if hasattr(archi, 'ip'):
            description = description + "\nAddress/IP: " + archi.ip
        if seed:
            if archi.seedValid:
                description = description + "\n*Seed Number: " + archi.seedNum
                description = description + "\n*Creation Date: " + archi.seedCreatedDate
                description = description + "\n*Seed URL: " + f"[Click here]({archi.seedUrl})"
                if hasattr(archi, 'spoiler'):
                    description = description + "\n*Spoiler Log: " + f"{archi.spoiler}"
                footer = "* Information is based on the seed number the user provided and may not match the room information"
            else:
                footer = f"Seed information could not be validated for seed number {archi.seedNum}"
        #table = "\n".join([" | ".join(row) for row in archi.worldTable])
        #embed.description = f"```\n{table}\n```"
        embed.description = description
        if hasattr(archi, "worldTable"):
            fields = archi.worldTable[0]
            for data in archi.worldTable[1:]:
                name = ""
                value = ""
                for index, item in enumerate(data):
                    if fields[index] == 'Id':
                        name = f"Player {item}"
                    else:
                        if len(value) != 0:
                            value = value + "\n"
                        value = value + f"{fields[index]}: {item}"
                embed.add_field(name=name, value=value, inline=False)
        if footer is not None:
            embed.set_footer(text=footer)
    else:
        embed.title = 'Invalid Room'
        embed.description = 'Either the room information provided is incorrect or something went wrong on our side... Please check the room key/url and try again'
    #embed.description = "This is a test to see how this embed works. [Click here](http://www.google.com) to go to google"
    await interaction.response.send_message(embed=embed)

@client.tree.command()
@app_commands.describe(
    first_value='The first value you want to add something to',
    second_value='The value you want to add to the first value',
)
async def add(interaction: discord.Interaction, first_value: int, second_value: int):
    """Adds two numbers together."""
    await interaction.response.send_message(f'{first_value} + {second_value} = {first_value + second_value}')

@client.event
async def on_member_update(before, after):
  activity_type = None
  streaming_role = discord.utils.get(after.guild.roles, name="live now")
  try:
    activity_type = after.activity.type
  except:
    pass

  if not (activity_type is discord.ActivityType.streaming):
    if streaming_role in after.roles:
      print(f"{after.display_name} has stopped streaming")
      await after.remove_roles(streaming_role)
  else:
    if streaming_role not in after.roles:
      print(f"{after.display_name} has started streaming")
      await after.add_roles(streaming_role)


@client.event
async def on_message(message):
  if message.author == client.user:
    return

  # Hello command
  if message.content.startswith('$hello'):
    author = message.author.name
    print(author)
    await message.channel.send(f"Hello {message.author.mention}!")

  # Throw command
  if message.content.startswith("$throw"):
    try:
      mentionedUser = message.mentions[0]
      # item = random.choice(throwItems)
      async with aiohttp.ClientSession() as cs:
        #async with cs.get(
          #  "https://throw-command.csobke.repl.co/api/throw") as r:
          #data = await r.json()
          #item = data["item"]
        item = random.choice(throwItems)
        await message.channel.send(
            f"{message.author.mention} threw {item} at {mentionedUser.mention}!"
        )
    except:
      await message.channel.send(
        f"Sorry {message.author.mention}, but either something went wrong or the command was not used correctly."
      )

  #Office Quote command
  if message.content == '$office-quote':
    quote = random.choice(officeQuotes)
    await message.channel.send(quote)

  # Cat Command
  if message.content == '$cat':
    try:
      async with message.channel.typing():
        async with aiohttp.ClientSession() as cs:
          async with cs.get("https://api.thecatapi.com/v1/images/search") as r:
            data = await r.json()
            embed = discord.Embed(title="Meow")
            embed.set_image(url=data[0]['url'])
            embed.set_footer(text="http://random.cat/")
            await message.channel.send(embed=embed)
    except:
      await message.channel.send('It seems like this command is not working right now... ):')

  # Duck Command
  if message.content == '$duck':
    try:
      async with message.channel.typing():
        async with aiohttp.ClientSession() as cs:
          async with cs.get("https://random-d.uk/api/v2/quack") as r:
            data = await r.json()
            embed = discord.Embed(title="Quack")
            embed.set_image(url=data['url'])
            embed.set_footer(text="http://random.duck/")
            await message.channel.send(embed=embed)
    except:
      await message.channel.send(
        'It seems like this command is not working right now... ):')

  # Dog Command
  if message.content == '$dog':
    try:
      async with message.channel.typing():
        async with aiohttp.ClientSession() as cs:
          async with cs.get("https://random.dog/woof.json") as r:
            data = await r.json()
            embed = discord.Embed(title="Woof")
            embed.set_image(url=data['url'])
            embed.set_footer(text="http://random.dog/")
            await message.channel.send(embed=embed)
    except:
      await message.channel.send(
        'It seems like this command is not working right now... ):')

  # NEW Conqueror Command
  if message.content.startswith('$start-conqueror'):
    # try:
    author = message.author.name
    print(db["conqueror"])
    print(db.keys())
    if db["conqueror"] == None:
      db["conqueror"] = {
        author: {
          'challenge': 'test',
          'distance': 'test2',
          'progress': 'test3'
        }
      }
    if author not in db['conqueror']:
      print("needs to be added")
      tempDb = db['conqueror']
      db['conqueror'] = tempDb.append(author)
      print(db['conqueror'])
      db['conqueror'][author] = {
        'challenge': 'test',
        'distance': 'test2',
        'progress': 'test3'
      }
    else:
      print("already added")
      print(db['conqueror'][author])
    # except:
    #   await message.channel.send('It seems like this command is not working right now... ):')
    # channel = client.get_channel(854794550262366259)
    # await channel.send("The '$start-conqueror' command is currently in development and will be available soon...")

  # Check to see if a role needs to be added based on rank up from MEE6
  if message.content.startswith('GG') and message.author.name == 'MEE6':
    # Extract the level from the default MEE6 message
    level = int(message.content.split("level ")[1][:-1])

    # Check to see if the rank requires a new role or not (roles are awarded every 5 levels)
    roles = []
    for role in message.guild.roles:
      if role.name == "live now":
        break
      roles.append(role.name)

    # Get role to be added to user
    role = discord.utils.get(message.guild.roles,
                             name=roles[math.floor(level / 5)])

    # Get the mentioned user
    mentionedUser = message.mentions[0]

    #Check to see if user needs the role added
    if role not in mentionedUser.roles:
      await mentionedUser.add_roles(role)
      await message.channel.send(
        f"Congrats {mentionedUser.mention}!, you earned the '{role.name}' role!"
      )
    else:
      print("role already added")


# keep_alive()
client.run(Token)
#client.run(DiscordToken)
