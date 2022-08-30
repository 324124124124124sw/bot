import asyncio
import random
import re
import discord
from .logging import *
from .gambling import checkIfUserinDB, mycursor, db
import os


kick_price = 12345
change_nick_price = 1000
mute_price = 1000 #per min
unmute_price = 20000 #perma
makerole_price = 1000000

class Shop(commands.Cog):
    def __init__(self, bot):
        self.client = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print(f'Bot is ready !')

    @commands.command()
    async def ping(self,ctx:commands.Context):
        await ctx.send("HI WORKING")

    @commands.command()
    async def mute(self, ctx, user: discord.Member, *, time_min : int):
        """Mute for 1000 points a min"""
        time_min = min(60,time_min)
        user_roles = [r.id for r in user.roles]

        #check if muted
        if 996849243656560700 not in user_roles:
            #check points
            mute_cost = mute_price*time_min
            table = checkIfUserinDB(ctx.author.id)
            author_points = int(table[0][2])
            if author_points >= mute_cost:
                role = discord.utils.get(user.guild.roles,
                                         id=996849243656560700)  # add "muted" role to members joining
                await user.add_roles(role)
                embed = discord.Embed(description=f"{user} was muted for **{time_min}** minutes",color=0x0D8B0D)
                await ctx.send(embed=embed)

                mycursor.execute(
                    f"update gambledb.points set points = {author_points - mute_cost}  where authorID = {ctx.author.id}")
                db.commit()


                await asyncio.sleep(time_min*60)
                await user.remove_roles(role)

            else:
                embed = discord.Embed(
                    description=f"Insufficient points. You have {author_points}. 1k points per minute.",
                    color=0x0D8B0D)
                await ctx.send(embed=embed)

        else:
            embed = discord.Embed(
                description=f"{user.display_name} is already muted",
                color=0x0D8B0D)

            await ctx.send(embed=embed)

    @commands.command()
    async def tast(self, ctx):
        channel = discord.utils.get(self.client.get_all_channels(), id=872830642646302812)
        print(channel)


    @commands.command()
    @commands.has_any_role("Admin")
    async def megamute(self, ctx, user: discord.Member, time_min: int, reason : str = None):
        time_min = min(360, time_min)
        user_roles = [r.id for r in user.roles]

        # check if muted
        if 1010890618907664424 not in user_roles:
            # check points

            role = discord.utils.get(user.guild.roles,id=1010890618907664424)  # add "muted" role to members joining
            await user.add_roles(role)
            embed = discord.Embed(description=f"{user} was MEGAmuted for **{time_min}** minutes for {reason}", color=0x0D8B0D)
            await ctx.send(embed=embed)
            channel = discord.utils.get(self.client.get_all_channels(), id=1010890558073479188)

            await channel.send(f"pce {user.mention}. Reason: {reason}. Cya in  {time_min} minutes")

            await asyncio.sleep(time_min * 60)
            await user.remove_roles(role)

        else:
            embed = discord.Embed(description=f"{user.display_name} is already MEGAmuted",
                color=0x0D8B0D)

            await ctx.send(embed=embed)


    @commands.command(alias=["role", "Role", "Makerole"])
    @commands.cooldown(1, 300, commands.BucketType.guild)
    async def makerole(self,ctx, colorpick, *, rolename: str):
        points = checkIfUserinDB(ctx.author.id)
        author_points = int(points[0][2])


        if author_points >= makerole_price and rolename not in ctx.guild.roles:
            await ctx.guild.create_role(name=f"{rolename}")

            len_colro = len(colorpick)
            if "#" in ctx.message.content:
                colorpick = colorpick[1:(len_colro)]
                colorpick = int(colorpick, 16)
                role = discord.utils.get(ctx.guild.roles, name=f"{rolename}")
                await role.edit(color=colorpick, position=(len(ctx.guild.roles)-7))

                embed = discord.Embed(
                    title=f"{rolename} has been created and set to {colorpick}",
                    color=colorpick)
            else:
                colorpick = int(colorpick, 16)
                role = discord.utils.get(ctx.guild.roles, name=f"{rolename}")
                await role.edit(color=colorpick, position=(len(ctx.guild.roles)-7))

                embed = discord.Embed(
                    title=f"{rolename} has been created and set to {colorpick}",
                    color=colorpick)

            mycursor.execute(
                f"update gambledb.points set points = {author_points - makerole_price}  where authorID = {ctx.author.id}")
            db.commit()
            await ctx.send(embed=embed)
            role = discord.utils.get(ctx.guild.roles, name=f"{rolename}")
            await ctx.author.add_roles(role)
        else:
            await ctx.send(f"Insufficient points. `{makerole_price}` required - balance `{author_points}`")

    @commands.command()
    async def kiss(self,ctx, user: discord.Member):
        gifname = f"gay{random.randint(1, 15)}.gif"

        #await ctx.send()
        embed = discord.Embed(color=0x40cc88)
        embed.add_field(name="Kissers",value=f"{ctx.author.mention} has kissed {user.mention}")
        file = discord.File(f"gay/{gifname}", filename=f"{gifname}")
        embed.set_image(url=f"attachment://{gifname}")
        await ctx.send(file=file, embed=embed)

    @commands.command()
    @commands.cooldown(1,300,commands.BucketType.user)
    async def kick(self, ctx, *, member: discord.Member):
        points = checkIfUserinDB(ctx.author.id)
        author_points = int(points[0][2])

        rolelist = [r.id for r in member.roles]

        if 804494451245711360 in rolelist:
            await ctx.send(f"<a:nitroboost:904771364173525002> {ctx.author.display_name}, you cannot kick the boosters<a:nitroboost:903298742675992627>")
        else:
            if author_points > kick_price:
                try:
                    await member.send(
                        f"{ctx.author} spent {kick_price} points to kick you bad rng \n https://discord.gg/yWhJVfaJRG")
                    await member.kick()
                    await ctx.send(f'{member.display_name} was kicked by {ctx.author.display_name}')
                except discord.HTTPException:
                    await member.kick()
                    await ctx.send(f'{member.display_name} was kicked by {ctx.author.display_name}')
                mycursor.execute(
                    f"update gambledb.points set points = {(author_points - int(kick_price))}  where authorID = {ctx.author.id}")
                db.commit()
            else:
                await ctx.send(f"Insufficient points. `{kick_price}` required - balance `{author_points}`")

    @commands.command()
    async def setnick(self, ctx, member: discord.Member, *, nickName):
        """ Set nickname for 1000 points"""
        table = checkIfUserinDB(ctx.author.id)

        if int(table[0][2]) >= change_nick_price:
            member_nameb4 = member.display_name
            await member.edit(nick=nickName)
            await ctx.send(f'{member_nameb4} was changed to to {member.mention} ')
            mycursor.execute(
                f"update gambledb.points set points = {int(table[0][2]) - change_nick_price}  where authorID = {ctx.author.id}")
            db.commit()
        else:
            await ctx.send(f"insufficient points. {change_nick_price} required - you have: {table[0][2]}")

    @commands.command()
    async def multiplier(self, ctx):
        """Buy multiplier for !daily"""

    @commands.command()
    async def shop(self, ctx):
        embed = discord.Embed(
            title="Shop stuffs...",
            description=f"**!setnick [user] [new name]**: `{change_nick_price}` points \n"
                        f"**!mute [user] [time in minutes]**: `{mute_price}` points per min \n"
                        f"**!unmute [user]**: `{unmute_price}` points\n"
                        f"**!kick [user]**: `{kick_price}` points\n"
                        f"**!makerole [hexcolor] [rolename]**: `{makerole_price}` points"
        )

        await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        rolelist = [r.id for r in member.roles]
        #print(rolelist)
        #print(member.guild.id)
        try:
            mycursor.execute(
                f"INSERT INTO `{member.guild.id}`.rolesaver (authorID, roles) VALUES (%s, %s)",
                (member.id, str(rolelist)))
            db.commit()
        except:
            print(f"Error adding roles to {member.guild.id}.rolesaver table")
            return

    @commands.Cog.listener()
    async def on_member_join(self, member):
        mycursor.execute(
            f"select * from `{member.guild.id}`.rolesaver where authorID = {member.id}"
        )
        joiner_table = mycursor.fetchall()

        table_test = joiner_table[0][1]
        role_id_list = re.findall(r'\d+', table_test)
        for role in role_id_list:
            try:
                introle = int(role)
                role = discord.utils.get(member.guild.roles, id=introle)
                await member.add_roles(role)
            except:
                pass

        mycursor.execute(
            f"delete from `{member.guild.id}`.rolesaver where authorID = {member.id}"
        )
        db.commit()


    @commands.command()
    async def sound(self, ctx, * , number : int = None):
        arr = os.listdir('mp3/')

        if not number:
            string = ""
            count = 0
            for x in range(len(arr)):
                string = string + f"**{count+1}**. {arr[count]} \n"
                count += 1
            embed = discord.Embed(
                title="Sned sounds",
                description="Do sound [num] to get a .mp3 file \n\n"
                            f"{string}"

            )

            await ctx.send(embed=embed)
        else:
            #print(arr[number-1])
            teststring = f"mp3/{arr[number-1]}"
            #print(teststring)
            await ctx.send(file=discord.File(fr'{teststring}'))



def setup(bot):
    bot.add_cog(Shop(bot))
