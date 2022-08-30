import discord
from discord import SlashCommand, SlashCommandGroup
from discord.ext import commands
import mysql.connector
from mysql.connector import Error

class Setup(commands.Cog):
    def __init__(self, bot):
        self.client = bot


    

def setup(bot):
    bot.add_cog(Setup(bot))