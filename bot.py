import datetime
import os
import discord
from discord.ext import tasks
from discord.ui import Modal, InputText
from cogs.xdd import commands
from cogs.logging import bot_prefix, token, mycursor, db, testingservers

intents = discord.Intents(messages=True, guilds=True, reactions=True, members=True, presences=True)
bot = discord.Bot()
bot = commands.Bot(command_prefix=f'{bot_prefix}', intents=discord.Intents.all())

@bot.command()
async def load(ctx, extension):
    bot.load_extension(f"cogs.{extension}")

@bot.command()
async def unload(ctx, extension):
    bot.unload_extension(f"cogs.{extension}")

for filename in os.listdir("./cogs"):
    if filename.endswith(".py"):
        bot.load_extension(f"cogs.{filename[:-3]}")


class MyModal(Modal):  # modal to edit msg
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.add_item(InputText(label="Submit suggestions", placeholder="Submit anything you want changed/added",
                                style=discord.InputTextStyle.long))

    async def callback(self, interaction: discord.Interaction):  # response to modal
        # await interaction.response.send_message(f"{self.children[0].value}")
        modal_content = self.children[0].value

        await interaction.response.send_message("Suggestions been submit", ephemeral=True)

        channel = bot.get_channel(977660721649299467)
        embed = discord.Embed(
            title=f"Suggestion by {interaction.user}",
            description=modal_content
        )
        embed.set_footer(text=f"{datetime.datetime.now()}")
        await channel.send(embed=embed)


class mergeButton(discord.ui.View):  # button
    def __init__(self):
        super().__init__(timeout=None)
        self.value = None

    # When the confirm button is pressed, set the inner value to `True` and
    # Stop the View from listening to more input.
    # We also send the user an ephemeral message that we're confirming their choice.
    @discord.ui.button(label="Submit suggestions", style=discord.ButtonStyle.blurple, emoji="💡")
    async def mergeButton(self, button: discord.ui.Button, interaction: discord.Interaction):
        modal = MyModal(title="Submit suggestions xDd")
        await interaction.response.send_modal(modal)

@bot.command()
async def suggestion(ctx):
    view = mergeButton()
    embed = discord.Embed(
        description="Submit any suggestions for xdd"
    )
    await ctx.send(embed=embed, view=view)


@bot.command()
@commands.cooldown(1,300,commands.BucketType.guild)
async def peggy(ctx):
    peggy = ctx.guild.get_member(157854569030746113) #157854569030746113
    await peggy.kick()
    await ctx.send("https://tenor.com/view/bye-bye-bye-donald-trump-gif-5648885")


@bot.event  # errorhandlign
async def on_command_error(ctx, error):
    if isinstance(error, commands.MemberNotFound):
        await ctx.send(f"{error.args[0]}")
    if isinstance(error, commands.CommandNotFound):
        print("Command not found xD")
    if isinstance(error, commands.CommandOnCooldown):
        await ctx.send('This command is on a %.2fs cooldown' % error.retry_after, delete_after=5)
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"{str(error.args[0])}")
    if isinstance(error, commands.MissingPermissions):
        await ctx.send(f"{str(error.args[0])}")
    if isinstance(error, (commands.MissingRole, commands.MissingAnyRole)):
        rolelist = ""
        print(error.missing_roles[0])
        for role in range(len(error.missing_roles)):
            rolelist = rolelist + f"{error.missing_roles[role]} "
        await ctx.send(f"You are missing any of these roles: {rolelist}")
    else:
        raise error


@tasks.loop(hours=24)  # loop - remove birthday if user not in guild/server
async def birthday_remover():
    mycursor.execute(
        f"SELECT * FROM gambledb.points"
    )
    table = mycursor.fetchall()
    number_of_ppl = len(table)

    guild = bot.get_guild(int(testingservers[0]))  # 305380209366925312 # 580855880426324106

    for x in range(number_of_ppl):
        try:
            user1 = guild.get_member(int(table[x][0]))
            display_name = user1.display_name
            #print(display_name)
            mycursor.execute(
                f"update gambledb.points set authorName = \"{display_name}\" where authorID = {table[x][0]}")
        except:
            print(f"FAIL on {int(table[x][0])}")

    db.commit()
    print("finished updating names")


@birthday_remover.before_loop  # REMOVES
async def before():
    await bot.wait_until_ready()

birthday_remover.start()



@bot.command()
async def roles(ctx, *, user: discord.Member = None):
    if not user:
        user = ctx.message.author
    rolelist = [r.mention for r in user.roles if r != ctx.guild.default_role]
    roles = ", ".join(rolelist)
    numberofroles = (roles.count("@"))

    embed = discord.Embed(title=f"{user} has {numberofroles} roles:",
                          description=f"{roles}", color=0xc32222)

    await ctx.send(embed=embed)


@bot.command()
async def allroles(ctx):
    embed = discord.Embed(title="All roles :",
                          description=", ".join([str(r.mention) for r in ctx.guild.roles]), color=0xc32222)
    await ctx.send(embed=embed)


@bot.command()
async def users(ctx, *, role: discord.Role):
    d = "\n".join(str(role) for role in role.members)  # number of users with each role
    d = str(d)
    d = d.count("#")

    embed = discord.Embed(title=f"{d} users with {role.name}",
                          description="\n".join(str(role) for role in role.members), color=0xc32222)
    await ctx.send(embed=embed)

bot.run(token)