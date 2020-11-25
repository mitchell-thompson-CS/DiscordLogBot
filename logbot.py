import os

import discord
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

client = discord.Client()

parent_path = "ServerLogs/" #parent path where all server logs will be put

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')
    for guild in client.guilds: #finds every guild that the bot is connected to and makes a file for it
        folderName = guild.name + " (" + str(guild.id) + ")/"
        if not(os.path.isdir(parent_path + folderName)): #creates directory for the guild if not there
            os.mkdir(parent_path + folderName)

        for categoryChannel in guild.categories: #runs through each category in the guild
            categoryName = categoryChannel.name + " (" + str(categoryChannel.id) + ")/"
            if not(os.path.isdir(parent_path + folderName + categoryName)): #creates directory for the category if not there
                os.mkdir(parent_path + folderName + categoryName)

            for channel in categoryChannel.channels: #each channel under each category will have its own text file
                fileName = channel.name + " (" + str(channel.id) + ").txt"
                f = open(parent_path + folderName + categoryName + fileName, "a")
                f.write(client.user.name + " has connected to " + channel.name + "!\n")
                f.close()
    
@client.event
async def on_guild_join(guild):
    folderName = guild.name + " (" + str(guild.id) + ")/"
    if not(os.path.isdir(parent_path + folderName)): #creates directory if not yet there
        os.mkdir(parent_path + folderName)

    for categoryChannel in guild.categories: #runs through all the categories and makes folder for each of them
        categoryName = categoryChannel.name + " (" + str(categoryChannel.id) + ")/"
        if not(os.path.isdir(parent_path + folderName + categoryName)):
            os.mkdir(parent_path + folderName + categoryName)

        for channel in categoryChannel.channels: #each channel in each category will get a file
            fileName = channel.name + " (" + str(channel.id) + ").txt"
            f = open(parent_path + folderName + categoryName + fileName, "a")
            f.write(client.user.name + " has connected to " + channel.name + "!\n")
            f.close()

@client.event
async def on_guild_update(before, after):
    path = parent_path + before.name + ' (' + str(before.id) + ")/"
    if(before.name != after.name): #checks if the name of the server has changed
        newName = after.name + " (" + str(after.id) + ")" #new folder name of the server
        os.rename(path, parent_path + newName) #renames previous folder
        return
    if(before.categories != after.categories): #left off yesterday
        print("test")


client.run(TOKEN)