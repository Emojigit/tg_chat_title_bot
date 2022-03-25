import sys
exit = sys.exit

try:
    import config
except ImportError:
    print("config.py not found, copying one for you...")
    import shutil
    try:
        shutil.copyfile("config.example.py","config.py")
        print("Config file copied, follow the instructions inside to config the bot.")
    except FileNotFoundError:
        print("config.example.py not found, make sure you're in the script's directory!")
    exit(1)

import asyncio, json, random
from telethon import TelegramClient, functions, types, events
from telethon.errors import *
from telethon.tl.functions.channels import LeaveChannelRequest

try:
    dataF = open("data.json","r+")
except FileNotFoundError:
    print("Please create data.json with `{}` first!")
    exit(1)
try:
    data = json.load(dataF)
except json.decoder.JSONDecodeError:
    print("data.json contains invalid data!")
    exit(1)

def save():
    print("Saving `{}`".format(data))
    dataF.seek(0)
    json.dump(data,dataF)
    dataF.truncate()
    print("Saving done!")

def setV(chan,key,val):
    try:
        currD = data[str(chan)]
    except KeyError:
        currD = {}
    if type(currD) == str:
        currD = {"title":currD}
    if val == None:
        currD.pop(key,None)
    else:
        currD[str(key)] = val
    data[str(chan)] = currD
    save()

def getV(chan,key):
    try:
        currD = data[str(chan)]
    except KeyError:
        return None
    if type(currD) == str:
        return currD if str(key) == "title" else None
    try:
        return currD[str(key)]
    except KeyError:
        return None

bot = TelegramClient('bot', config.api_id, config.api_hash).start(bot_token=config.bot_token)

client = bot # For easier copying examples XD

helps = "\n".join([
    "Hi! I'm the group title bot. Use me to configure temporay group title for fun!",
    "Avaliable commands:",
    "/start : This message!",
    "/setnormaltitle : Set the title that's used normally",
    "/settitle : Set the temporary title (supply no args to set to the default one)",
    "/normaltitle : Set the default title back",
    "/conf : Raw config interface",
    "/dumpconf : dump the configs in this group",
    "/ping : Pong!",
    "I can only be used by admins with the right \"Change group informations\"."
])

async def Ctitle(event,title):
    chat = event.chat
    msgBase = "Changing title to `{}`...".format(title)
    msgEnd = msgBase + " {}"
    msg = await event.respond(msgBase)
    try:
        await client(functions.channels.EditTitleRequest(
            channel=chat.id,
            title=title
        ))
    except ChatNotModifiedError:
        await client.edit_message(msg, msgEnd.format("Still the same!"))
    except ChatAdminRequiredError:
        await client.edit_message(msg, msgEnd.format("How come I still cannot do that!"))
    except ChannelInvalidError:
        await client.edit_message(msg, msgEnd.format("Am I really in a channel?"))
    else:
        await client.edit_message(msg, msgEnd.format("Done!"))

@bot.on(events.NewMessage(pattern='/start'))
async def start(event):
    await event.respond(helps)
    raise events.StopPropagation

pongs = ['Pong!','Have Fun!','Ping Pong!','Table Tennis!','Whiff-Whaff!','Prepare your Table Tennis Balls!','404 Responce not found (joking)']
@bot.on(events.NewMessage(pattern='/ping'))
async def ping(event):
    await event.respond(random.choice(pongs))
    raise events.StopPropagation

@bot.on(events.NewMessage(pattern='/myid'))
async def myid(event):
    await event.respond(str(event.sender.id))
    raise events.StopPropagation

@bot.on(events.NewMessage(pattern='/chatid'))
async def chatid(event):
    await event.respond(str(event.chat.id))
    raise events.StopPropagation

@bot.on(events.NewMessage(pattern='/checkpriv'))
async def checkpriv(event):
    chat = event.chat
    user = event.sender
    try:
        privs = await client.get_permissions(chat, user)
        mypriv = await client.get_permissions(chat, await client.get_me())
        if privs.change_info:
            await event.respond("You can!")
        else:
            await event.respond("You cannot!")
        if mypriv.change_info:
            await event.respond("I can!")
        else:
            await event.respond("I cannot!")
    except ValueError:
        await event.respond("You're not in a channel!")
    finally:
        raise events.StopPropagation

@bot.on(events.NewMessage(pattern='/parsecmd'))
async def parsecmd(event):
    try:
        await event.respond(event.text.split(" ",1)[1])
    except IndexError:
        await event.respond("No args!")
    finally:
        raise events.StopPropagation

@bot.on(events.NewMessage(pattern='/setnormaltitle'))
async def setnormaltitle(event):
    chat = event.chat
    user = event.sender
    try:
        privs = await client.get_permissions(chat, user)
        mypriv = await client.get_permissions(chat, await client.get_me())
        if not mypriv.change_info:
            await event.respond("I cannot do that! Contact the group admins!")
        else:
            if not privs.change_info:
                await event.respond("You cannot do that!")
            else:
                try:
                    title = event.text.split(" ",1)[1]
                    await event.respond("Changing title to `{}`...".format(title))
                    setV(chat.id,"title",title)
                    await Ctitle(event,title)
                except IndexError:
                    await event.respond("Use /setnormaltitle <title>!")

    except ValueError:
        await event.respond("You're not in a channel!")
    finally:
        raise events.StopPropagation

@bot.on(events.NewMessage(pattern='/settitle'))
async def settitle(event):
    chat = event.chat
    user = event.sender
    try:
        privs = await client.get_permissions(chat, user)
        mypriv = await client.get_permissions(chat, await client.get_me())
        if not mypriv.change_info:
            await event.respond("I cannot do that! Contact the group admins!")
        else:
            if not privs.change_info:
                await event.respond("You cannot do that!")
            else:
                title = ""
                try:
                    title = event.text.split(" ",1)[1]
                except IndexError:
                    title = getV(chat.id,"title")
                    if title == None:
                        await event.respond("No record and no args! Use /settitle <title>!")
                        title == ""
                if title != "":
                    await Ctitle(event,title)
    except ValueError:
        await event.respond("You're not in a channel!")
    finally:
        raise events.StopPropagation

@bot.on(events.NewMessage(pattern='/normaltitle'))
async def normaltitle(event):
    chat = event.chat
    user = event.sender
    try:
        privs = await client.get_permissions(chat, user)
        mypriv = await client.get_permissions(chat, await client.get_me())
        if not mypriv.change_info:
            await event.respond("I cannot do that! Contact the group admins!")
        else:
            if not privs.change_info:
                await event.respond("You cannot do that!")
            else:
                title = getV(chat.id,"title")
                if title == None:
                    await event.respond("No record! Use /setnormaltitle <title>!")
                else:
                    await Ctitle(event,title)
    except ValueError:
        await event.respond("You're not in a channel!")
    finally:
        raise events.StopPropagation

allow_confs = ["title"]

@bot.on(events.NewMessage(pattern='/conf'))
async def conf(event):
    chat = event.chat
    user = event.sender
    try:
        privs = await client.get_permissions(chat, user)
        mypriv = await client.get_permissions(chat, await client.get_me())
        if not mypriv.change_info:
            await event.respond("I cannot do that! Contact the group admins!")
        else:
            if not privs.change_info:
                await event.respond("You cannot do that!")
            else:
                args = event.text.split(" ",2)
                if len(args) == 1:
                    await event.respond("Allowed config keys: " + ", ".join(allow_confs))
                else:
                    key = args[1]
                    if args[1] in allow_confs:
                        if len(args) == 2:
                            val = getV(chat.id,key)
                            await event.respond("{} = {}".format(key,(val if val != None else "<not set>")))
                        else:
                            val = args[2]
                            if val == "None": val = None
                            setV(chat.id,key,val)
                            await event.respond("{} = {}".format(key,(val if val != None else "<not set>")))
                    else:
                        await event.respond("Invalid config key! Allowed keys: " + ", ".join(allow_confs))
    except ValueError:
        await event.respond("You're not in a channel!")
    finally:
        raise events.StopPropagation

@bot.on(events.NewMessage(pattern='/dumpconf'))
async def conf(event):
    chat = event.chat
    try:
        await event.respond(str(data[str(chat.id)]))
    except KeyError:
        await event.respond("{}")
    finally:
        raise events.StopPropagation

@bot.on(events.ChatAction)
async def chataction(event):
    chat = event.chat
    me = await client.get_me()
    if event.user_kicked and event.user_id == me.id:
        data.pop(str(chat.id),None)
        save()
    raise events.StopPropagation

bot.run_until_disconnected()



