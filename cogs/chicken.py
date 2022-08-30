from random import randint
import discord
from discord.ext import commands
from .gambling import mycursor, checkIfUserinDB, db

chickenPrice = 1000
chickenLives = 3

def checkChickenDB(user_ID):
    mycursor.execute(
        f"SELECT * FROM gambledb.chickenfight where authorID = {user_ID}"
    )
    table = mycursor.fetchall()

    return table

def authorPicEmbed(text, member):
    embed = discord.Embed(
        description=text
    )
    try:
        embed.set_author(name=f"{member.display_name}", icon_url=f"{member.avatar.url}")
    except:
        embed.set_author(name=f"{member.display_name}", icon_url=f"{member.default_avatar.url}")
    return embed

def changePoints(pointsBefore, changeAmount, userID):
    mycursor.execute(
        f"update gambledb.points set points = {pointsBefore + changeAmount}  where authorID = {userID}")
    db.commit()

def updateChickenLives(lives_before,userID):
    if lives_before > 1:
        mycursor.execute(
            f"update gambledb.chickenfight set chickenLives = {lives_before-1}  where authorID = {userID}")
        db.commit()
    else:
        mycursor.execute(
            f"delete from gambledb.chickenfight where authorID = {userID}")
        db.commit()

def updateChickenWR(userID, WR):
    if WR < 75:
        mycursor.execute(
            f"update gambledb.chickenfight set chickenWR = {WR + 1}  where authorID = {userID}")
        db.commit()



class Chicken(commands.Cog):
    def __init__(self, bot):
        self.client = bot

    @commands.command(aliases=["buychicken"])
    async def buyChicken(self, ctx, *, chickenName : str):
        """ Buy a chicken with 3 lives """
        table = checkIfUserinDB(ctx.author.id)
        author_points = int(table[0][2])
        if author_points >= chickenPrice:
            chickenTable = checkChickenDB(ctx.author.id)
            if len(chickenTable) < 1:
                mycursor.execute(
                    f"INSERT INTO gambledb.chickenfight (authorID, chickenName, chickenWR, chickenLives) "
                    f"VALUES (%s, %s, %s, %s)",
                    (ctx.author.id, chickenName, 50, chickenLives))
                db.commit()

                changePoints(author_points, -chickenPrice, ctx.author.id)

                embed = authorPicEmbed(f"**{ctx.author.display_name}** you got a new chicken named 🐔`{chickenName}`🐔 \n\n Keep him safe! If you lose 3 duels, you chicken is deadge <:deadge:998111636571303986>", ctx.author)
                await ctx.send(embed=embed)
            else:
                embed = authorPicEmbed(f"You already have a chicken named **{table[0][1]}** with `{chickenTable[0][2]}`% WR", ctx.author)
                await ctx.send(embed=embed)
        else:
            await ctx.send(f"Insufficient points. You have {author_points}. {chickenPrice} required")


    @commands.command(aliases=["chickenfight","cf"])
    async def chickenFight(self,ctx, amount : int):
        """Fight the bot to train your chicken"""
        table = checkIfUserinDB(ctx.author.id)
        author_points = int(table[0][2])
        amount = max(0,amount)
        if author_points >= amount:
            chickenTable = checkChickenDB(ctx.author.id)
            if len(chickenTable) > 0:
                wr = int(chickenTable[0][2])
                roll = randint(1,100)
                #print(roll)
                if wr > roll:
                    # win
                    changePoints(author_points,amount,ctx.author.id)
                    await ctx.send(f"you won `{amount}` points and {chickenTable[0][1]} grew stronger")
                    updateChickenWR(ctx.author.id,int(chickenTable[0][2]))
                else:
                    #lose + lose life
                    changePoints(author_points, -amount, ctx.author.id)
                    updateChickenLives(int(chickenTable[0][3]), ctx.author.id)
                    if int(chickenTable[0][3]) == 1:
                        await ctx.send(f"you lost `{amount}` points... and {chickenTable[0][1]} died f")
                    else:
                        await ctx.send(f"You lost `{amount}` points and {chickenTable[0][1]} took a hit and has {int(chickenTable[0][3])-1} lives left.")

            else:
                await ctx.send(f"You dont have a chicken. Buy one with !buychicken [name]")

        else:
            await ctx.send(f"Insufficient points. You have {author_points}")

    @commands.command()
    @commands.cooldown(1, 23, commands.BucketType.guild)
    async def chickenduel(self, ctx, amount: int):
        table = checkIfUserinDB(ctx.author.id)
        author_points = int(table[0][2])

        if author_points >= amount:
            embed = discord.Embed(
                title=f"Duel request - click \"Accept Duel\" to fight"
            )
            embed.add_field(name="Points at stake", value=f"`{amount}`")
            embed.set_footer(text=f"{ctx.author.id}")
            try:
                embed.set_author(name=f"{ctx.author.display_name}", icon_url=f"{ctx.author.avatar.url}")
            except:
                embed.set_author(name=f"{ctx.author.display_name}", icon_url=f"{ctx.author.default_avatar.url}%")

            await ctx.send(embed=embed, view=duelButton(timeout=15))
        else:
            await ctx.send(f"insufficient points. Balance {author_points}")

    @commands.command()
    async def chicken(self,ctx, user : discord.User = None):
        """ Check your own or someones chicken"""
        if not user:
            user = ctx.author

        chickenTable = checkChickenDB(user.id)
        if len(chickenTable) > 0:
            embed = authorPicEmbed(f"**{user.display_name}** has a chicken named **{chickenTable[0][1]}**"
                                   f"\n`{chickenTable[0][2]}`% WR"
                                   f"\n`{chickenTable[0][3]}` lives left", user)
        else:
            embed = authorPicEmbed(f"**{user.display_name}** has no chicken \nBuy one with !buychicken for {chickenPrice} points", user)

        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(Chicken(bot))