import discord # import discord.py
from discord.ext import commands # import additional discord.py functionality
#import random # RNG
import typing # allow parameters to be optional
import os # import the OS details, including our hidden bot token
import asyncpg # import async/await postgres
import asyncio

db = None
serverID = 769343298749202452 #cliffside
serverID = 817445327686467655 # personal bs

## Connecting the DB ----------------------------------------------------------
async def run():
    global db
    
    dbURL = os.environ.get('DATABASE_URL')
    db = await asyncpg.connect(dsn=dbURL, ssl='require')
    
## Bot Setup ----------------------------------------------------------
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
async def close(ctx, rpID: int, event: typing.Optional[str]):
    user = ctx.message.author.id
    cliffside = bot.get_guild(serverID)
    serverMember = await cliffside.fetch_member(user)
    serverNickname = serverMember.display_name
    sendChannel = bot.get_channel(eventLoggingChannelID)

    rpList = await db.fetchval("SELECT rp_list FROM users WHERE uid = $1;",user)

    if rpID in rpList:
        rpList.remove(rpID)
        await db.execute("UPDATE users SET rp_list = $1 WHERE uid = $2;",rpList,user)
        await db.execute("UPDATE rps SET status = 'CLOSED' WHERE id = $1;",rpID)
        await ctx.send("The RP has been closed and will no longer show in your tracker :blush:")
        if event == "event":
            rpChannel = await db.fetchval("SELECT channel FROM rps WHERE id = $1;",rpID)
            rpCharacters = await db.fetchval("SELECT characters FROM rps WHERE id = $1;",rpID)
            rpPartners = await db.fetchval("SELECT partners FROM rps WHERE id = $1;",rpID)
            rpNotes = await db.fetchval("SELECT notes FROM rps WHERE id = $1;",rpID)

            channelDict = {}
            channelList = cliffside.channels
            for channel in channelList:
                channelDict[channel.name] = channel.id

            sendMessage = serverNickname + " has logged: \n"
            sendMessage += " " + str(rpID) + ". "
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
            await sendChannel.send(sendMessage)
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

    await ctx.send("Your tracker header has been updated.\n" + oldHeader + " → " + newHeader)

@commands.group(invoke_without_command=True, aliases=["plan","pl"])
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
async def _new(ctx, *, notes: typing.Optional[str]):
    user = ctx.message.author.id
    emptyList = []

    await db.execute("INSERT INTO rps (uid, status, notes) VALUES ($1,'OPEN',$2);",user,notes)

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

    await ctx.send("Your planner header has been updated.\n" + oldHeader + " → " + newHeader)


## Bot Setup & Activation ----------------------------------------------------------
asyncio.get_event_loop().run_until_complete(run())
bot.run(token)
