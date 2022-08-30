import discord

from .logging import *

class CustomCommands(commands.Cog):
    def __init__(self, bot):
        self.client = bot

    @commands.command()
    #@commands.has_permissions(manage_channels=True)
    async def add(self,ctx, commandName : str, *, commandContent : str):
        """Add a custom command to the list"""
        #print(commandName)
        #print(commandContent)
        commandName = f"{commandName.lower()}"
        try:
            mycursor.execute(f"INSERT INTO `{ctx.guild.id}`.customcommands (commandName, commandContent) VALUES (%s, %s)",
                    (commandName, commandContent))

            db.commit()
            await ctx.send(f"{commandName} has been added with `{commandContent}`")
        except Error as err:
            if err.errno == 1062:
                await ctx.send(f"Command `{commandName}` already added. Remove first to re-add")
            else:
                await ctx.send(err)

    @commands.command()
    async def list(self,ctx, value = None):
        if not value:
            value = ""
        """Shows which custom commands are added to the server"""
        mycursor.execute(f"SELECT * FROM `{ctx.guild.id}`.customcommands where commandName like \"%{value}%\" order by commandName asc")
        table = mycursor.fetchall()

        commandNames = ""
        for x in range(len(table)):
            command1 = str(table[x][0])
            #print(command1)
            commandNames = f"{commandNames}{command1}, "

        embed = discord.Embed(
            title=f"Commands ({len(table)}) in {ctx.guild.name}",
            description=commandNames
        )

        await ctx.send(embed=embed)

    @commands.command()
    @commands.has_permissions(manage_channels=True)
    async def remove(self, ctx, commandName: str):
        """Remove a custom command from the list"""
        # print(commandName)
        # print(commandContent)
        commandName = f"{commandName.lower()}"
        mycursor.execute(f"DELETE FROM `{ctx.guild.id}`.customcommands where commandName = \"{commandName}\"")
        db.commit()

        await ctx.send(f"{commandName} has been removed")

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        # print(message.content)
        if message.author.bot:
            return
        else:
            if message.content.startswith(bot_prefix):
                mycursor.execute(f"SELECT * FROM `{message.guild.id}`.customcommands")
                table = mycursor.fetchall()
                command_list = []
                for comm in range(len(table)):
                    command_list.append(f"{bot_prefix}{table[comm][0]}")

                first_word = (message.content).lower().split(" ")[0]

                if first_word in command_list:
                    list_id = command_list.index(first_word)
                    await message.channel.send(table[list_id][1])
                else:
                    return
            else:
                return


def setup(bot):
    bot.add_cog(CustomCommands(bot))