import os
import time
import datetime
from datetime import datetime, timedelta
from os import listdir
from secrets import TOKEN

import discord
from multipledispatch import dispatch


client = discord.Client()

parent_path = "ServerLogs/" #parent path where all server logs will be put
if not(os.path.isdir(parent_path)): #creates directory for the parent_path if not there
    os.mkdir(parent_path)

people_blacklist = []
channel_blacklist = []
role_blacklist = []
voice_notifications = True
message_notifications = True

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')
    for guild in client.guilds: #finds every guild that the bot is connected to and makes a file for it
        generateGuild(guild)
    print(datetime.now())
    
@client.event
async def on_message(message):
    if(message_notifications):
        guild = message.guild
        category = message.channel.category
        channel = message.channel
        path = findPath(guild, category, channel)
        isBlocked = False
        for channelB in channel_blacklist:
            if(channelB == channel):
                isBlocked = True
        if not(isBlocked):
            f = open(path, "a") #append file
            f.write(formatFileName(message.author) + " at " + str(datetime.now()) + ": " + message.content + "\n")
            f.close()

    commands(message)

@client.event
async def on_message_delete(message):
    if(message_notifications):
        guild = message.guild
        category = message.channel.category
        channel = message.channel
        path = findPath(guild, category, channel)
        isBlocked = False
        for channelB in channel_blacklist:
            if(channelB == channel):
                isBlocked = True
        if not(isBlocked):
            f = open(path, "a") #append file
            f.write("MESSAGE DELETED at " + str(datetime.now()) + " from " + str(message.created_at - timedelta(hours=8)) + ": " + formatFileName(message.author) + ": " + message.content + "\n")
            f.close()

@client.event
async def on_message_edit(before, after):
    if(message_notifications):
        guild = before.guild
        category = before.channel.category
        channel = before.channel
        path = findPath(guild, category, channel)
        isBlocked = False
        for channelB in channel_blacklist:
            if(channelB == channel):
                isBlocked = True
        if not(isBlocked):
            f = open(path, "a") #append file
            f.write(formatFileName(before.author) + " MESSAGE EDITED at " + str(datetime.now()) + " from \"" + before.content + "\" TO \"" + after.content + "\"\n")
            f.close()

@client.event
async def on_voice_state_update(member, before, after):
    print("test")

@client.event
async def on_guild_join(guild):
    generateGuild(guild)

@client.event
async def on_guild_update(before, after):
    path = findPath(before)
    if(before.name != after.name): #checks if the name of the server has changed
        newName = formatFileName(after) #new folder name of the server
        os.rename(path, parent_path + newName) #renames previous folder
        return

@client.event
async def on_guild_channel_update(before, after):
    if type(before) == discord.CategoryChannel:
        path = findPath(before.guild, before)
        if before.name != after.name:
            os.rename(path, findPath(after.guild, after))
            return
        return
    else:
        path = findPath(before.guild, before.category, before)
        if before.name != after.name:
            os.rename(path, findPath(after.guild, after.category, after))

@client.event
async def on_guild_channel_create(channel):
    if type(channel) == discord.CategoryChannel:
        os.mkdir(findPath(channel.guild, channel))
    else:
        beginningOfConnection(channel, findPath(channel.guild, channel.category, channel), channel.name + " has been created at " + str(datetime.now()))

@client.event
async def on_guild_channel_delete(channel):
    path = findPath(channel.guild, channel.category, channel)
    f = open(path, "a")
    f.write(channel.name + " has been DELETED at " + str(datetime.now()))
    f.close()

def formatFileName(channel): #returns "channel.name (channel.id)"
    return channel.name + " (" + str(channel.id) + ")"

@dispatch(object)
def findPath(guild):
    return parent_path + formatFileName(guild) + "/"

@dispatch(object, object)
def findPath(guild, category):
    return findPath(guild) + formatFileName(category) + "/"

@dispatch(object, object, object)
def findPath(guild, category, channel):
    return findPath(guild, category) + formatFileName(channel) + ".txt"

def generateGuild(guild):
    folderName = findPath(guild)
    if not(os.path.isdir(folderName)): #creates directory for the guild if not there
        os.mkdir(folderName)

    for categoryChannel in guild.categories: #runs through each category in the guild
        categoryName = findPath(guild, categoryChannel)

        changeIdInDirectory(guild, categoryChannel)

        for channel in categoryChannel.channels: #each channel under each category will have its own text file
            changeIdInDirectory(guild, categoryChannel, channel)
            fileName = findPath(guild, categoryChannel, channel)
            beginningOfConnection(channel, fileName)

@dispatch(object, object)
def changeIdInDirectory(guild, category):
    files = os.listdir(findPath(guild))
    for file in files:
        if str(category.id) in file:
            if not(formatFileName(category) == file):
                os.rename(findPath(guild) + file, findPath(guild, category))
            return
    os.mkdir(findPath(guild, category))

@dispatch(object, object, object)
def changeIdInDirectory(guild, category, channel):
    files = os.listdir(findPath(guild, category))
    for file in files:
        if str(channel.id) in file:
            if not(formatFileName(channel) == file):
                os.rename(findPath(guild, category) + file, findPath(guild, category, channel))
            return
    return

@dispatch(object, str)
def beginningOfConnection(channel, path):
    f = open(path, "a")
    f.write(client.user.name + " has connected to " + channel.name + " at " + str(datetime.now()) + "!\n")
    f.close()

@dispatch(object, str, str)
def beginningOfConnection(channel, path, addMessage):
    f = open(path, "a")
    f.write(client.user.name + " has connected to " + channel.name + " at " + str(datetime.now()) + "!\n")
    f.write(addMessage + "\n")
    f.close()

async def commands(message):
    if(message.content.startswith("!logbot")):
        content = message.content[8:]
        if content.startswith("blacklist"):
            #ADD THAT ONLY ADMINISTRATORS CAN USE THIS FUNCTION
            content = content[10:]
            if content.startswith("add"):
                await blacklist_add(message, content)

def addToPeopleBlackList(newPerson, guild):
    for info in people_blacklist:
        if (newPerson == info[0]) and (guild == info[1]):
            return
    people_blacklist.append([newPerson, guild])

def addToChannelBlackList(newChannel, guild):
    for info in channel_blacklist:
        if (newChannel == info[0]) and (guild == info[1]):
            return
    channel_blacklist.append([newChannel, guild])

def addToRoleBlackList(newRole, guild):
    for info in role_blacklist:
        if(newRole == info[0]) and (guild == info[1]):
            return
    role_blacklist.append([newRole, guild])

async def blacklist_add(message, content):
    if len(message.channel_mentions) > 0 and len(message.mentions) == 0 and len(message.role_mentions) == 0:
        for channelB in message.channel_mentions:
            addToChannelBlackList(channelB, message.guild)
    elif len(message.mentions) > 0 and len(message.channel_mentions) == 0 and len(message.role_mentions) == 0:
        for personB in message.mentions:
            addToPeopleBlackList(personB, message.guild)
    elif len(message.role_mentions) > 0 and len(message.channel_mentions) == 0 and len(message.mentions) == 0:
        for rolesB in message.role_mentions:
            addToRoleBlackList(rolesB, message.guild)
    else:
        await message.channel.send("That is not a valid format to add in! Accepted formats: \"!logbot blacklist add @person @person ...\" and \"!logbot blacklist add #channel #channel ...\" and \"!logbot blacklist add @role @role ...\"")

client.run(TOKEN)
