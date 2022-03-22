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

import asyncio, json
from telethon import TelegramClient, functions, types, events
from telethon.errors import *

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

bot = TelegramClient('bot', config.api_id, config.api_hash).start(bot_token=config.bot_token)

client = bot # For easier copying examples XD
"""
asyncio.run(client(functions.bots.SetBotCommandsRequest(
    scope=types.BotCommandScopeDefault(),
    lang_code='en',
    commands=[types.BotCommand(
        command='start',
        description='Show help of this bot'
    ),types.BotCommand(
        command='setnormaltitle',
        description='Set the title that\'s used normally'
    ),types.BotCommand(
        command='settitle',
        description='Set the temporary title (supply no args to set to the default one)'
    ),types.BotCommand(
        command='normaltitle',
        description='Set the default title back'
    )]
)))
"""

helps = "\n".join([
    "Hi! I'm the group title bot. Use me to configure temporay group title for fun!",
    "Avaliable commands:",
    "/start : This message!",
    "/setnormaltitle : Set the title that's used normally",
    "/settitle : Set the temporary title (supply no args to set to the default one)",
    "/normaltitle : Set the default title back",
    "I can only be used by admins with the right \"Change group informations\"."
])

@bot.on(events.NewMessage(pattern='/start'))
async def start(event):
    await event.respond(helps)
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
                    await event.respond("Changing title to `{}`...".format(event.text.split(" ",1)[1]))
                    data[str(chat.id)] = event.text.split(" ",1)[1]
                    print(data)
                    save()
                    #await client(functions.messages.EditChatTitleRequest(
                    await client(functions.channels.EditTitleRequest(
                        #chat_id=chat.id,
                        channel=chat.id,
                        title=title
                    ))
                    await event.respond("Done!")
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
                    try:
                        title = data[str(chat.id)]
                    except IndexError:
                        await event.respond("No record and no args! Use /settitle <title>!")
                if title != "":
                    await event.respond("Changing title to `{}`...".format(title))
                    await client(functions.channels.EditTitleRequest(
                        #chat_id=chat.id,
                        channel=chat.id,
                        title=title
                    ))
                    await event.respond("Done!")
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
                try:
                    title = data[str(chat.id)]
                except IndexError:
                    await event.respond("No record and no args! Use /setnormaltitle <title>!")
                if title != "":
                    await event.respond("Changing title to `{}`...".format(title))
                    await client(functions.channels.EditTitleRequest(
                        #chat_id=chat.id,
                        channel=chat.id,
                        title=title
                    ))
                    await event.respond("Done!")
    except ValueError:
        await event.respond("You're not in a channel!")
    finally:
        raise events.StopPropagation


bot.run_until_disconnected()



