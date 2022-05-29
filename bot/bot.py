import discord # import discord.py
from discord.ext import commands # import additional discord.py functionality
import random # RNG
import typing # allow parameters to be optional
import os # import the OS details, including our hidden bot token
import asyncpg # import async/await postgres
import asyncio
import datetime
import io
# import DiscordUtils
import json
from aiohttp import request
import aiohttp

from config.names import *

db = None
serverID = 769343298749202452 #cliffside
#serverID = 817445327686467655 # personal bs

greetResponses = [
    "Yes? :flushed:",
    "Let's all be kind to one another. :relaxed:",
    "Thank you for thinking about me. :pleading_face:",
    ":slight_smile: :heartpulse:",
    "Mind the clan borders... :unamused:",
    "I'm pretty Fly for a Toes guy. :relieved:",
    "Does anyone have any birch bark? :anguished:"
]

kissResponses = [
    "If it's okay, here's a kiss for you too! :kissing_closed_eyes:",
    "Don't forget to ask before you kiss anyone. :relieved:",
    "Kisses on my nose and paws are my favourite. :pleading_face:",
    ":point_right: :point_left:",
    "May I also have a kiss? :pleading_face:",
    "May I also give you a kiss? :pleading_face:",
    "Have you thought about... giving a kiss to someone called Flytoes? :pleading_face:"
]

ghostResponses = [
    "Just a friendly reminder that ghosts aren't real. :expressionless:",
    "Ghosts aren't real. StarClan is where our ancestral *spirits* live, thank you. :unamused:",
    ":rolling_eyes:",
    "I'm not afraid of no ghosts. :angry:"
]

#https://discord.com/api/oauth2/authorize?client_id=943245257947091004&permissions=93248&scope=bot

## Connecting the DB ----------------------------------------------------------
async def run():
    global db
    
    dbURL = os.environ.get('DATABASE_URL')
    db = await asyncpg.connect(dsn=dbURL, ssl='require')
    
## Bot Setup ----------------------------------------------------------
token = os.environ.get('DISCORD_BOT_TOKEN') # This is hosted on HEROKU

client = discord.Client()

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix=["c!","c,","c."], intents=intents, db=db)

def is_dev():
    def predicate(ctx):
        return ctx.message.author.id == 191278750032330753
    return commands.check(predicate)
    
#def is_staff():
#    def predicate(ctx):
#        return ctx.message.author.id in modIDs
#    return commands.check(predicate)
    
def is_admin():
    def predicate(ctx):
        return ctx.message.author.id in [475855997416505344,191278750032330753]
    return commands.check(predicate)

## Code Here ----------------------------------------------------------
@bot.event
async def on_message(message):
    if message.guild.id != 817445327686467655:
        contents = message.content
        cleanContents = contents.replace(" ","").lower()
        semicleanContents = contents.replace("'","").lower()
        semicleanContents = semicleanContents.replace(",","").lower()
        semicleanContents = semicleanContents.replace("nows","now is").lower()
        semicleanContents = semicleanContents.replace("favourite","favorite").lower()
        currentChannel = message.channel
        guildName = bot.get_guild(serverID)
        emptyList = []
        user = message.author.id
        if user in [245616657899323394]:
            print("WARNING: Attempted blocked access, in " + str(message.guild) + " | " + str(message.channel) + ". Content: " + message.content)
            alertMessage = "WARNING: Attempted blocked access, in " + str(message.guild) + " | " + str(message.channel) + ". Content: " + message.content
            await dm_user(191278750032330753,alertMessage,"Alert")
            return
        try:
            serverNickname = message.author.nick
        except AttributeError:
            serverNickname = str(message.author)

        if message.author != bot.user:
            if bot.user.mentioned_in(message):
                messageChoice = random.choice(greetResponses)
                await message.channel.send(messageChoice)

            #if currentChannel.id in spadesChannels:
            if "ghost" in semicleanContents:
                responseList = ghostResponses
            elif any(responseCue in semicleanContents for responseCue in ["flytoes","mrtoes","mistertoes","mr.toes"]):
                responseList = greetResponses
            elif "kiss" in semicleanContents:
                responseList = kissResponses
            elif "kendall" in semicleanContents:
                responseList = ["This is your reminder to drink some water!"]
            else:
                responseList = []

            if responseList != emptyList:
                responseCheck = random.choices([True,False],cum_weights=[1,4])[0]
                if responseCheck:
                    response = random.choice(responseList)
                    await message.channel.send(response)
            
    ctx = await bot.get_context(message)
    await bot.invoke(ctx)
    
@bot.command(aliases=["names","name"])
async def namegen(ctx, numberNames: typing.Optional[int]):
    user = ctx.author.mention
    if numberNames is None:
        numberNames = 1
        
    if numberNames > 157:
        await ctx.send("Sorry! I can only send up to 157 names at a time due to Discord's character limit.")
        return
        
    nameText = ""
    for i in range(numberNames):
        name = ""
        name += random.choice(prefixesList)
        name += random.choice(suffixesList)
        nameText += name
        if i != (numberNames - 1):
            nameText += ", "
    await ctx.send(f"{user}\n{nameText}")
    
@bot.group(aliases=["w"])
async def weather(ctx):
    pass
    
@weather.command(aliases=["now","here","rp","irp"])
async def cliffside(ctx):
    async with aiohttp.ClientSession() as session:
        jsonURL = "https://api.openweathermap.org/data/2.5/weather?id=5892532&units=imperial&appid=f9db8388d6cbfc933dba43778b763a2e"

        async with session.get(jsonURL) as thing:
            try:
                load = await thing.read()
                jdata = json.loads(load)
                currentTemp = jdata['main']['temp']
                feelTemp = jdata['main']['feels_like']
                currentWeather = jdata['weather'][0]['main']
                weatherDesc = jdata['weather'][0]['description']
                windSpeed = jdata['wind']['speed']
                humidity = jdata['main']['humidity']
                try:
                    rainfall = jdata['rain']['rainfall']
                except:
                    rainfall = None
                try:
                    snowfall = jdata['snow']['snowfall']
                except:
                    snowfall = None
            except:
                await ctx.send("Whoops! Something went wrong. `Line: 176`")
                return

        jsonURL = "https://api.openweathermap.org/data/2.5/weather?id=5892532&units=metric&appid=f9db8388d6cbfc933dba43778b763a2e"
        async with session.get(jsonURL) as thing:
            try:
                load = await thing.read()
                jdata = json.loads(load)
                currentTempC = jdata['main']['temp']
                feelTempC = jdata['main']['feels_like']
            except:
                await ctx.send("Whoops! Something went wrong. `Line: 187`")
                return

            if currentWeather == "Clouds":
                emoji = ":cloud:"
            elif currentWeather == "Thunderstorm":
                emoji = ":thunder_cloud_rain:"
            elif currentWeather == "Clear":
                emoji = ":sunny:"
            elif currentWeather in ["Rain","Drizzle"]:
                emoji = ":cloud_rain:"
            elif currentWeather == "Snow":
                emoji = ":snowflake:"
            elif currentWeather in ["Mist","Smoke","Haze","Dust","Fog","Ash","Sand","Squall"]:
                emoji = ":fog:"
            elif currentWeather == "Tornado":
                emoji = ":cloud_tornado:"

            messageText = f"{emoji} **{currentWeather}** {emoji} - *{weatherDesc}*"
            messageText += f"\n:thermometer: The current temperature is **{currentTempC} C | {currentTemp} F**. It feels like **{feelTempC} C | {feelTemp} F**"
            messageText += f"\nHumidity: *{humidity}%*\nWind Speed: *{windSpeed} MPH*"
            await ctx.send(messageText)
    
@bot.command()
@is_admin()
async def reset(ctx):
    global db
    
    try:
        userCheck = await db.fetchval("SELECT uid FROM users WHERE uid = $1;",user)
        await ctx.send("The connection is fine! The command you were trying may not be formatted correctly, or there's a different bug that needs to be reported.")
    except:
        dbURL = os.environ.get('DATABASE_URL')
        db = await asyncpg.connect(dsn=dbURL, ssl='require')
        try:
            userCheck = await db.fetchval("SELECT uid FROM users WHERE uid = $1;",user)
            await ctx.send("Database connection reset!")
        except:
            await ctx.send("It looks like I can't reset the database. Let Kendall know `line 161`!")

@bot.group()
async def dev(ctx):
    pass

@dev.command(pass_context=True)
@is_dev()
async def email(ctx):
    await ctx.send("Email: cliffsidebot@gmail.com")
    
@dev.command(pass_context=True)
@is_dev()
async def sql(ctx, *, sqlText: str):
    if ";" not in sqlText:
        sqlText += ";"
    await db.execute(sqlText)
    await ctx.send("Complete.")
    
@bot.group(invoke_without_command=True, aliases=["rp","roleplays","rps"])
async def roleplay(ctx):
    user = ctx.message.author.id
    emptyList = []

    userCheck = await db.fetchval("SELECT uid FROM users WHERE uid = $1;",user)
    if userCheck is None:
        await db.execute("INSERT INTO users (uid, rp_list) VALUES ($1,$2);",user,emptyList)

    rpList = await db.fetchval("SELECT rp_list FROM users WHERE uid = $1;",user)

    header = await db.fetchval("SELECT header FROM users WHERE uid = $1;",user)

    if header is None:
        header = "**You have the following RPs:**"

    if (rpList == None) or (rpList == emptyList):
        await ctx.send("I could not find any rps for you.")
    else:
        sendMessage = header + "\n"
        for rp in rpList:
            rpChannel = await db.fetchval("SELECT channel FROM rps WHERE id = $1;",rp)
            rpCharacters = await db.fetchval("SELECT characters FROM rps WHERE id = $1;",rp)
            rpPartners = await db.fetchval("SELECT partners FROM rps WHERE id = $1;",rp)
            rpNotes = await db.fetchval("SELECT notes FROM rps WHERE id = $1;",rp)

            channelDict = {}
            cliffside = bot.get_guild(serverID)
            channelList = cliffside.channels
            for channel in channelList:
                channelDict[channel.name] = channel.id

            sendMessage += " " + str(rp) + ". "
            if rpChannel is not None:
                try:
                    sendMessage += "<#" + str(channelDict[rpChannel]) + ">"
                except:
                    sendMessage += "#" + rpChannel
            if rpCharacters is not None:
                sendMessage += ": " + rpCharacters
            if rpPartners is not None:
                sendMessage += " with " + rpPartners
            if rpNotes is not None:
                sendMessage += " [" + rpNotes + "]"
            sendMessage += "\n"
        await ctx.send(sendMessage)

@roleplay.command(aliases=["n","add"])
async def new(ctx, channel: str, *, notes: typing.Optional[str]):
    user = ctx.message.author.id
    emptyList = []

    await db.execute("INSERT INTO rps (uid, channel, status, notes) VALUES ($1,$2,'OPEN',$3);",user,channel,notes)

    userCheck = await db.fetchval("SELECT uid FROM users WHERE uid = $1;",user)
    if userCheck is None:
        await db.execute("INSERT INTO users (uid,rp_list) VALUES ($1,$2);",user,emptyList)

    currentList = await db.fetchval("SELECT rp_list FROM users WHERE uid = $1;",user)
    if currentList is None:
        currentList = []

    currentID = await db.fetchval("SELECT id FROM rps WHERE uid = $1 AND channel = $2 ORDER BY id DESC;",user,channel)
    currentList.append(currentID)
    await db.execute("UPDATE users SET rp_list = $1 WHERE uid = $2;",currentList,user)
    await ctx.send("Your roleplay (ID #" + str(currentID) + ") has been added to the list!")

@roleplay.command(aliases=["v"])
async def view(ctx):
    user = ctx.message.author.id
    emptyList = []

    userCheck = await db.fetchval("SELECT uid FROM users WHERE uid = $1;",user)
    if userCheck is None:
        await db.execute("INSERT INTO users (uid, rp_list) VALUES ($1,$2);",user,emptyList)

    rpList = await db.fetchval("SELECT rp_list FROM users WHERE uid = $1;",user)

    header = await db.fetchval("SELECT header FROM users WHERE uid = $1;",user)

    if header is None:
        header = "**You have the following RPs:**"

    if (rpList == None) or (rpList == emptyList):
        await ctx.send("I could not find any rps for you.")
    else:
        sendMessage = header + "\n"
        for rp in rpList:
            rpChannel = await db.fetchval("SELECT channel FROM rps WHERE id = $1;",rp)
            rpCharacters = await db.fetchval("SELECT characters FROM rps WHERE id = $1;",rp)
            rpPartners = await db.fetchval("SELECT partners FROM rps WHERE id = $1;",rp)
            rpNotes = await db.fetchval("SELECT notes FROM rps WHERE id = $1;",rp)

            channelDict = {}
            cliffside = bot.get_guild(serverID)
            channelList = cliffside.channels
            for channel in channelList:
                channelDict[channel.name] = channel.id

            sendMessage += " " + str(rp) + ". "
            if rpChannel is not None:
                try:
                    sendMessage += "<#" + str(channelDict[rpChannel]) + ">"
                except:
                    sendMessage += "#" + rpChannel
            if rpCharacters is not None:
                sendMessage += ": " + rpCharacters
            if rpPartners is not None:
                sendMessage += " with " + rpPartners
            if rpNotes is not None:
                sendMessage += " [" + rpNotes + "]"
            sendMessage += "\n"
        await ctx.send(sendMessage)

@roleplay.command(aliases=["reopen"])
@is_admin()
async def open(ctx, rpID: int):
    await db.execute("UPDATE rps SET status = 'OPEN' WHERE id = $1;",rpID)
    user = await db.fetchval("SELECT uid FROM rps WHERE id = $1;",rpID)
    rpList = await db.fetchval("SELECT rp_list FROM users WHERE uid = $1;",user)
    rpList.append(rpID)
    await db.execute("UPDATE users SET rp_list = $1 WHERE uid = $2;",rpList,user)
    await ctx.send(f"RP #{rpID} has been reopened.")

@roleplay.command(aliases=["c"])
async def close(ctx, rpID: int):
    user = ctx.message.author.id
    cliffside = bot.get_guild(serverID)
    serverMember = await cliffside.fetch_member(user)
    serverNickname = serverMember.display_name

    rpList = await db.fetchval("SELECT rp_list FROM users WHERE uid = $1;",user)

    if rpID in rpList:
        rpList.remove(rpID)
        await db.execute("UPDATE users SET rp_list = $1 WHERE uid = $2;",rpList,user)
        await db.execute("UPDATE rps SET status = 'CLOSED' WHERE id = $1;",rpID)
        await ctx.send("The RP has been closed and will no longer show in your tracker :blush:")
    else:
        await ctx.send("Sorry, I couldn't find that roleplay. :worried:")

@roleplay.command(aliases=["e","update","u","set"])
async def edit(ctx, rpID: int, editType: str, *, newValue: typing.Optional[str]):
    user = ctx.message.author.id
    rpList = await db.fetchval("SELECT rp_list FROM users WHERE uid = $1;",user)

    if editType not in ["channel","characters","partners","notes","players","location","humans","people","writers"]:
        await ctx.send("Please use one of the following: *channel, characters, partners, notes*")
    else:
        if rpID not in rpList:
            await ctx.send("Sorry, I couldn't find that roleplay. :worried:")
        else:
            if editType in ["players","humans","people","writers"]:
                editType = "partners"
            if editType == "location":
                editType = "channel"
            updateText = "UPDATE rps SET " + editType + " = $1 WHERE id = $2;"
            await db.execute(updateText,newValue,rpID)
            await ctx.send("Your RP has been updated!")

@roleplay.command(aliases=["s"])
async def sort(ctx, *, newList: str):
    user = ctx.message.author.id
    originalList = await db.fetchval("SELECT rp_list FROM users WHERE uid = $1;",user)

    originalList.sort()

    strList=list(newList.split())
    intList=list(map(int,strList))
    sortedList=list(map(int,strList))

    sortedList.sort()

    if sortedList != originalList:
        await ctx.send("Your list does not match. Perhaps you forgot an RP?")
    else:
        await db.execute("UPDATE users SET rp_list = $1 WHERE uid = $2;",intList,user)
        await ctx.send("Your list order has been updated.")

@roleplay.command()
async def header(ctx, *, newHeader: typing.Optional[str]):
    user = ctx.message.author.id

    oldHeader = await db.fetchval("SELECT header FROM users WHERE uid = $1;",user)

    if oldHeader is None:
        oldHeader = "*Default*"

    await db.execute("UPDATE users SET header = $1 WHERE uid = $2;", newHeader, user)

    if newHeader is None:
        newHeader = "*Default*"

    await ctx.send("Your tracker header has been updated.\n" + oldHeader + " ? " + newHeader)

@bot.group(invoke_without_command=True, aliases=["plan","pl"])
async def planner(ctx):
    user = ctx.message.author.id
    emptyList = []

    userCheck = await db.fetchval("SELECT uid FROM users WHERE uid = $1;",user)
    if userCheck is None:
        await db.execute("INSERT INTO users (uid, plan_list) VALUES ($1,$2);",user,emptyList)

    planList = await db.fetchval("SELECT plan_list FROM users WHERE uid = $1;",user)

    header = await db.fetchval("SELECT plan_header FROM users WHERE uid = $1;",user)

    if header is None:
        header = "**You have the following plans:**"

    if (planList == None) or (planList == emptyList):
        await ctx.send("I could not find any plans for you.")
    else:
        sendMessage = header + "\n"
        for rp in planList:
            rpChannel = await db.fetchval("SELECT channel FROM rps WHERE id = $1;",rp)
            rpCharacters = await db.fetchval("SELECT characters FROM rps WHERE id = $1;",rp)
            rpPartners = await db.fetchval("SELECT partners FROM rps WHERE id = $1;",rp)
            rpNotes = await db.fetchval("SELECT notes FROM rps WHERE id = $1;",rp)

            channelDict = {}
            cliffside = bot.get_guild(serverID)
            channelList = cliffside.channels
            for channel in channelList:
                channelDict[channel.name] = channel.id

            sendMessage += " " + str(rp) + ". "
            if rpChannel is not None:
                try:
                    sendMessage += "<#" + str(channelDict[rpChannel]) + ">"
                except:
                    sendMessage += rpChannel
                sendMessage += ": "
            if rpCharacters is not None:
                sendMessage += f"{rpCharacters} "
            if rpPartners is not None:
                sendMessage += f"with {rpPartners} "
            if rpNotes is not None:
                sendMessage += "[" + rpNotes + "]"
            sendMessage += "\n"
        await ctx.send(sendMessage)

# s.new <channel> [*notes]
@planner.command(aliases=["n","add","new"])
async def _new(ctx, *, characters: typing.Optional[str]):
    user = ctx.message.author.id
    emptyList = []

    await db.execute("INSERT INTO rps (uid, status, characters) VALUES ($1,'OPEN',$2);",user,characters)

    userCheck = await db.fetchval("SELECT uid FROM users WHERE uid = $1;",user)
    if userCheck is None:
        await db.execute("INSERT INTO users (uid,plan_list) VALUES ($1,$2);",user,emptyList)

    currentList = await db.fetchval("SELECT plan_list FROM users WHERE uid = $1;",user)
    if currentList is None:
        currentList = []

    currentID = await db.fetchval("SELECT id FROM rps WHERE uid = $1 ORDER BY id DESC;",user)
    currentList.append(currentID)
    await db.execute("UPDATE users SET plan_list = $1 WHERE uid = $2;",currentList,user)
    await ctx.send("Your plan (ID #" + str(currentID) + ") has been added to your planner!")

@planner.command(aliases=["v","view"])
async def _view(ctx):
    user = ctx.message.author.id
    emptyList = []

    userCheck = await db.fetchval("SELECT uid FROM users WHERE uid = $1;",user)
    if userCheck is None:
        await db.execute("INSERT INTO users (uid, plan_list) VALUES ($1,$2);",user,emptyList)

    planList = await db.fetchval("SELECT plan_list FROM users WHERE uid = $1;",user)

    header = await db.fetchval("SELECT plan_header FROM users WHERE uid = $1;",user)

    if header is None:
        header = "**You have the following plans:**"

    if (planList == None) or (planList == emptyList):
        await ctx.send("I could not find any plans for you.")
    else:
        sendMessage = header + "\n"
        for rp in planList:
            rpChannel = await db.fetchval("SELECT channel FROM rps WHERE id = $1;",rp)
            rpCharacters = await db.fetchval("SELECT characters FROM rps WHERE id = $1;",rp)
            rpPartners = await db.fetchval("SELECT partners FROM rps WHERE id = $1;",rp)
            rpNotes = await db.fetchval("SELECT notes FROM rps WHERE id = $1;",rp)

            channelDict = {}
            cliffside = bot.get_guild(serverID)
            channelList = cliffside.channels
            for channel in channelList:
                channelDict[channel.name] = channel.id

            sendMessage += " " + str(rp) + ". "
            if rpChannel is not None:
                try:
                    sendMessage += "<#" + str(channelDict[rpChannel]) + ">"
                except:
                    sendMessage += rpChannel
                sendMessage += ": "
            if rpCharacters is not None:
                sendMessage += f"{rpCharacters} "
            if rpPartners is not None:
                sendMessage += f"with {rpPartners} "
            if rpNotes is not None:
                sendMessage += "[" + rpNotes + "]"
            sendMessage += "\n"
        await ctx.send(sendMessage)

@planner.command(aliases=["open"])
@is_admin()
async def _open(ctx, rpID: int):
    await db.execute("UPDATE rps SET status = 'OPEN' WHERE id = $1;",rpID)
    user = await db.fetchval("SELECT uid FROM rps WHERE id = $1;",rpID)
    rpList = await db.fetchval("SELECT plan_list FROM users WHERE uid = $1;",user)
    rpList.append(rpID)
    await db.execute("UPDATE users SET plan_list = $1 WHERE uid = $2;",rpList,user)
    await ctx.send(f"Plan #{rpID} has been reopened.")

@planner.command(aliases=["c","close"])
async def _close(ctx, rpID: int):
    user = ctx.message.author.id
    cliffside = bot.get_guild(serverID)
    serverMember = await cliffside.fetch_member(user)
    serverNickname = serverMember.display_name

    rpList = await db.fetchval("SELECT plan_list FROM users WHERE uid = $1;",user)

    if rpID in rpList:
        rpList.remove(rpID)
        await db.execute("UPDATE users SET plan_list = $1 WHERE uid = $2;",rpList,user)
        await db.execute("UPDATE rps SET status = 'CLOSED' WHERE id = $1;",rpID)
        await ctx.send("The plan has been closed and will no longer show in your planner :blush:")
    else:
        await ctx.send("Sorry, I couldn't find that plan. :worried:")

@planner.command()
async def start(ctx, planID: int):
    user = ctx.message.author.id
    cliffside = bot.get_guild(serverID)
    serverMember = await cliffside.fetch_member(user)
    serverNickname = serverMember.display_name

    planList = await db.fetchval("SELECT plan_list FROM users WHERE uid = $1;",user)
    rpList = await db.fetchval("SELECT rp_list FROM users WHERE uid = $1;",user)

    if planID in planList:
        planList.remove(planID)
        rpList.append(planID)
        await db.execute("UPDATE users SET plan_list = $1 WHERE uid = $2;",planList,user)
        await db.execute("UPDATE users SET rp_list = $1 WHERE uid = $2;",rpList,user)
        await ctx.send("The plan has been moved to your RP tracker! :blush:")
    elif planID in rpList:
        await ctx.send("Oops! It looks like this plan has already been moved to your planner!")
    else:
        await ctx.send("Sorry, I couldn't find that plan. :worried:")

@planner.command(aliases=["e","update","u","set","edit"])
async def _edit(ctx, rpID: int, editType: str, *, newValue: typing.Optional[str]):
    user = ctx.message.author.id
    rpList = await db.fetchval("SELECT plan_list FROM users WHERE uid = $1;",user)

    if editType not in ["channel","characters","partners","notes","players","location","humans","people","writers"]:
        await ctx.send("Please use one of the following: *channel, characters, partners, notes*")
    else:
        if rpID not in rpList:
            await ctx.send("Sorry, I couldn't find that plan. :worried:")
        else:
            if editType in ["players","humans","people","writers"]:
                editType = "partners"
            if editType == "location":
                editType = "channel"
            updateText = "UPDATE rps SET " + editType + " = $1 WHERE id = $2;"
            await db.execute(updateText,newValue,rpID)
            await ctx.send("Your plan has been updated!")

@planner.command(aliases=["s","sort"])
async def _sort(ctx, *, newList: str):
    user = ctx.message.author.id
    originalList = await db.fetchval("SELECT plan_list FROM users WHERE uid = $1;",user)

    originalList.sort()

    strList=list(newList.split())
    intList=list(map(int,strList))
    sortedList=list(map(int,strList))

    sortedList.sort()

    if sortedList != originalList:
        await ctx.send("Your list does not match. Perhaps you forgot a plan?")
    else:
        await db.execute("UPDATE users SET plan_list = $1 WHERE uid = $2;",intList,user)
        await ctx.send("Your list order has been updated.")

@planner.command(aliases=["header"])
async def _header(ctx, *, newHeader: typing.Optional[str]):
    user = ctx.message.author.id

    oldHeader = await db.fetchval("SELECT plan_header FROM users WHERE uid = $1;",user)

    if oldHeader is None:
        oldHeader = "*Default*"

    await db.execute("UPDATE users SET plan_header = $1 WHERE uid = $2;", newHeader, user)

    if newHeader is None:
        newHeader = "*Default*"

    await ctx.send("Your planner header has been updated.\n" + oldHeader + " ? " + newHeader)
    
async def dm_user(userID, text, type):
    user = await bot.fetch_user(userID)
    userDM = user.dm_channel
    mention = user.mention
    if userDM is None:
        try: # to create a DM channel
            userDM = await user.create_dm()
            if type == "Timer":
                await userDM.send("Your timer is finished: " + text)
            elif type == "Loot":
                await userDM.send("You have received the following loot: " + text)
            elif type == "Alert":
                await userDM.send(f"{text}")
        except: # not allowed, send in ctx
            if type == "Timer":
                await ctx.send("Your timer is finished: " + text)
            elif type == "Loot":
                await ctx.send("You have received the following loot: " + text)
            elif type == "Alert":
                await userDM.send(f"{text}")
    else:
        try: # to send in the pre-existing DM
            if type == "Timer":
                await userDM.send("Your timer is finished: " + text)
            elif type == "Loot":
                await userDM.send("You have received the following loot: " + text)
            elif type == "Alert":
                await userDM.send(f"{text}")
        except: # not allowed, send in ctx
            if type == "Timer":
                await ctx.send("Your timer is finished: " + text)
            elif type == "Loot":
                await ctx.send("You have received the following loot: " + text)
            elif type == "Alert":
                await userDM.send(f"{text}")


## Bot Setup & Activation ----------------------------------------------------------
asyncio.get_event_loop().run_until_complete(run())
bot.run(token)
