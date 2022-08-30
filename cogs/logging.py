import datetime
import sys
from datetime import datetime,date,timedelta
import discord
from discord.ext import commands
import mysql.connector
from mysql.connector import Error
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np

def STARTup(test): #setting
    if test == 2: #if 1 = test
        db_user = "root"
        token = 
        testingservers = [305380209366925312]
        bot_prefix = "¤"
    else:
        db_user = "admin"
        token = #
        testingservers = [783483960889966613, 305380209366925312, 989596371931787265]
        bot_prefix = "!"

    return db_user, token, testingservers, bot_prefix

def create_server_connection(host_name, user_name, user_password,database_name = None):  # setup SQL
    connection = None
    try:
        connection = mysql.connector.connect(
            host=host_name,
            user=user_name,
            passwd=user_password,
            database=database_name
        )
        print("MySQL Database connection successful")
    except Error as err:
        print(f"Error: '{err}'")

    return connection

db_user, token, testingservers, bot_prefix = STARTup(1)

db = create_server_connection("localhost", f"{db_user}", f"{db_user}")
mycursor = db.cursor()  # server cursor to DB idk


def extractFirst(lst):
    return [item[0] for item in lst]
def extractSecond(lst):
    return [int(item[1]) for item in lst]

class Logging(commands.Cog):
    def __init__(self, bot):
        self.client = bot

    @discord.slash_command(guild_ids=[305380209366925312])
    async def all_time(self,ctx):
        await ctx.respond("HI WORKING")

    @commands.command()
    async def setup(self, ctx):
        print(ctx.guild.id)
        try:
            mycursor.execute(
                f"CREATE SCHEMA `{ctx.guild.id}` ;"
            )

            mycursor.execute(
                f"CREATE TABLE `{ctx.guild.id}`.deletedmsgs "
                f"(userName VARCHAR(255), "
                f"messageContent VARCHAR(1000),"
                f"createdAt VARCHAR(255),"
                f"channelID VARCHAR(255),"
                f"guildID VARCHAR(255),"
                f"userID VARCHAR(255)"
                f");"
            )

            mycursor.execute(
                f"CREATE TABLE `{ctx.guild.id}`.customcommands "
                f"(commandName VARCHAR(55) NOT NULL,"
                f"commandContent VARCHAR(1000),"
                f"PRIMARY KEY (`commandName`));"
            )

            mycursor.execute(
                f"CREATE TABLE `{ctx.guild.id}`.loggedmsgs "
                f"(messageID VARCHAR(255), "
                f"authorID VARCHAR(255),"
                f"messageChan VARCHAR(255),"
                f"authorName VARCHAR(255),"
                f"guildID VARCHAR(255),"
                f"messageContent VARCHAR(1000),"
                f"datetimeMSG VARCHAR(255)"
                f");"
            )

            mycursor.execute(
                f"CREATE TABLE `{ctx.guild.id}`.gambletracker"
                f"(authorID varchar(255),"
                f"wins varchar(255),"
                f"losses varchar(255),"
                f"profit varchar(255)"
                f");"
            )

            mycursor.execute(
                f"CREATE TABLE `{ctx.guild.id}`.rolesaver"
                f"(authorID varchar(255),"
                f"roles varchar(6000)"
                f");"
            )
            db.commit()

            mycursor.execute(
                f"ALTER TABLE `{ctx.guild.id}`.loggedmsgs CHARACTER SET = utf8mb4, COLLATE = utf8mb4_general_ci ;")

            db.commit()

            await ctx.send("Databases have been created! Bot is ready to use")

        except Error as err:
            if "1007" in str(err):
                await ctx.send("Database has already been created")
            else:
                print(err)

    @commands.Cog.listener()
    async def on_message_delete(self,message):
        userName = message.author.name
        userID = message.author.id
        messageContent = message.content
        createdAt = message.created_at
        channelID = message.channel.id
        guildID = message.guild.id
        if not message.author.bot:
            if len(messageContent) > 999:
                messageContent = messageContent[0:998]

            try:
                mycursor.execute(
                    f"INSERT INTO `{message.guild.id}`.deletedmsgs (userName, messageContent, createdAt, channelID, guildID, userID) VALUES (%s, %s, %s, %s, %s, %s)",
                    (userName, messageContent, createdAt, channelID, guildID, userID))

                db.commit()
            except:
                print("table doesnt exist")
                return

    @commands.Cog.listener()
    async def on_message(self,message : discord.Message):
        #print(message.content)
        if message.guild:
            #print(message.content)
            message_id = int(message.id)
            message_chan = int(message.channel.id)
            author_id = int(message.author.id)
            author_name = str(message.author)
            guild_id = int(message.guild.id)
            message_content = str(message.content)
            message_creation = str(message.created_at)

            if len(message_content) > 999:
                message_content = message_content[0:998]

            message_content = message_content.encode("ascii", "ignore")
            message_content = message_content.decode()

            #try:
            mycursor.execute(
                f"INSERT INTO `{message.guild.id}`.loggedmsgs (messageID, authorID, messageChan, authorName, guildID, messageContent, datetimeMSG) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (message_id, author_id, message_chan, author_name, guild_id, message_content, message_creation))

            db.commit()
            #except:
                #print("table doesnt exist")
                #return
        else:
            return




    @commands.command()
    @commands.cooldown(1, 9999999999999, commands.BucketType.guild)
    async def logmsgs(self, ctx):  # logs every message from server- should add check if msg id in list
        if ctx.author.id == 228143014168625153:
            for channel in ctx.guild.text_channels:
                #print(channel)
                async for message in channel.history(limit=None):
                    #try:
                    #print(message)
                    message_id = int(message.id)
                    message_chan = int(message.channel.id)
                    author_id = int(message.author.id)
                    author_name = str(message.author)
                    guild_id = int(message.guild.id)
                    message_content = str(message.content)

                    #await ctx.send(message_content)
                    if len(message_content) > 999:
                        message_content = message_content[0:998]

                    message_content = message_content.encode("ascii", "ignore")
                    message_content = message_content.decode()

                    author_name = author_name.encode("ascii", "ignore")
                    author_name = author_name.decode()

                    message_creation = str(message.created_at)

                    mycursor.execute(
                        f"INSERT INTO `{ctx.guild.id}`.loggedmsgs (messageID, authorID, messageChan, authorName, guildID, messageContent, datetimeMSG) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                        (message_id, author_id, message_chan, author_name, guild_id, message_content,
                         message_creation))

                    db.commit()
                    #except:
                        #print("=============PASSED???============")
                        #continue


            await ctx.send("All channel logging has finished")
        else:
            await ctx.send("no")

    @discord.slash_command(guild_ids=testingservers, name="user", description="Shows info about specific user")
    async def user(self, ctx: discord.ApplicationContext,
                   user: discord.Option(discord.Member, "Pick a member"),
                   time_amount: discord.Option(int, "Past x hours", min_value=1, max_value=100000),
                   time_format: discord.Option(str, "Week, day or hour", choices=["Hour", "Day", "Week", "Alltime"])):
        mysql_time = time_amount
        if time_format == "Day":
            mysql_time = time_amount * 24
        if time_format == "Week":
            mysql_time = time_amount * 24 * 7
        if time_format == "Alltime":
            mysql_time = 100000
        mysql_time = min(mysql_time, 100000)
        # print(mysql_time)

        await ctx.defer()  # it avoids timeout when grabbing data from table
        mycursor.execute(f"SELECT authorName,COUNT(*) as count FROM `{ctx.guild.id}`.loggedmsgs "
                         f"WHERE date_format(datetimeMSG, '%Y-%m-%d-%T') >= (NOW() - INTERVAL {mysql_time} hour) "
                         f"and guildID = {user.guild.id} and authorID = {user.id} GROUP BY authorName ORDER BY count DESC")
        table = mycursor.fetchall()  # grabs table sorted
        # await ctx.send(f"test {table}")

        try:
            totalmsgs = table[0][1]
        except:
            totalmsgs = 0

        # get most used channels:
        mycursor.execute(f"SELECT messageChan,COUNT(*) as count FROM `{ctx.guild.id}`.loggedmsgs "
                         f" where date_format(datetimeMSG, '%Y-%m-%d-%T') >= (NOW() - INTERVAL {mysql_time} hour) "
                         f" and authorID = {user.id} and guildID = {user.guild.id}"
                         f" group by messageChan order by count desc")
        channel_table = mycursor.fetchall()  # grabs table sorted

        top_channel_str = ""

        for x in range(3):  # add top channels to table
            try:
                top_channel_str = top_channel_str + f"{x + 1}. <#{channel_table[x][0]}> - `{channel_table[x][1]}` msgs\n"
                # print("added")

            except:
                top_channel_str = top_channel_str + "."
                # print("FAILED")

        # print(len(top_channel_str))
        if len(top_channel_str) < 4:
            top_channel_str = "None"

        if totalmsgs == 0:
            MPH_message = 0
        else:
            MPH_message = round(totalmsgs / (mysql_time), 2)

        embed = discord.Embed(
            title=f"{user.name} - overview",
            description=f"`{totalmsgs}` messages sent past `{time_amount} {time_format}(s)` \n"
                        f" ** MPH ** : {MPH_message}",
            color=discord.Color.purple(),
        )
        try:
            embed.set_thumbnail(url=f"{user.avatar.url}")
        except:
            embed.set_thumbnail(url=f"{user.default_avatar.url}")

        embed.add_field(name=f"Most used channels",
                        value=f"{top_channel_str}",
                        inline=False)
        await ctx.respond(embed=embed)

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def snipe(self,ctx):
        """shows most recent deleted msg in channel (within 2min)"""
        guildID = ctx.guild.id
        channelID = ctx.channel.id
        now = datetime.now()
        # print(now)

        mycursor.execute(
            f"SELECT * FROM `{ctx.guild.id}`.deletedmsgs where guildID = {guildID} and channelID = {channelID} order by createdAt DESC;")
        deleted_msg_table = mycursor.fetchall()
        #print(deleted_msg_table)
        #print(deleted_msg_table[0])
        #print(deleted_msg_table[0][2])

        msg_time = deleted_msg_table[0][2]
        dif = now - msg_time
        two_min_time = timedelta(minutes=2)
        # print(dif)
        # print(two_min_time)

        if two_min_time > dif:
            member = ctx.guild.get_member(int(deleted_msg_table[0][5]))
            # print(member)
            # print(member.display_name)

            embed = discord.Embed(
                description=f"**{member.display_name}** deleted a message with following text : \n"
                            f"*{deleted_msg_table[0][1]}*",
                color=discord.Color.purple(),
            )
            msg_time = msg_time.strftime("%H:%M")
            try:
                av_url = f"{member.avatar.url}"
            except:
                av_url = f"{member.default_avatar.url}"
            embed.set_footer(text=f"Deleted at {msg_time}", icon_url=f"{av_url}")

            await ctx.send(embed=embed)
        else:
            await ctx.send(f"No msg has been deleted in {ctx.channel} past 2 minutes", delete_after=5)

    @discord.slash_command(guild_ids=testingservers, name="graphshit", description="graph who the fk cares")
    async def graphshit(self, ctx: discord.ApplicationContext,
                   time_amount: discord.Option(int, "Past x days", min_value=1, max_value=10000),
                       user: discord.Option(discord.Member, "Pick a member", required=False)):
        testthingstring = " "

        if user:
            testthingstring = f" and authorID = {user.id} "

        await ctx.defer()  # it avoids timeout when grabbing data from table
        mycursor.execute(f"SELECT datetimeMSG,count(*) FROM `{ctx.guild.id}`.loggedmsgs "
                         f"where date_format(datetimeMSG, '%Y-%m-%d-%T') >= (NOW() - INTERVAL {time_amount} day){testthingstring}group by date(datetimeMSG) order by datetimeMSG asc")
        table = mycursor.fetchall()
        #print(table)

        #print(table[0][0])
        try:
            format = "%Y-%m-%d %H:%M:%S"
            date_0 = datetime.strptime(str(table[0][0])[0:19], format)
        except ValueError:
            format = "%Y-%m-%d %H:%M:%S.%f"
            date_0 = datetime.strptime(str(table[0][0]), format)
        #print(type(date_0))
        date_now = datetime.now()
        #print(date_now)
        days_dif = int((date_now-date_0).days)
        days_dif2 = max(1,int(round(days_dif/10)))
        print(days_dif)

        datesExtracted = np.array(extractFirst(table))
        #print(datesExtracted)
        msgCountExtractted = np.array(extractSecond(table))
        #print(msgCountExtractted)
        idk = []
        """for x in range(len(msgCountExtractted)):
            idk.append(x)
        idk = np.array(idk)
        print(idk)"""
        #print(msgCountExtractted)
        #print(datesExtracted)

        #plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        #plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=days_dif2))

        plt.plot(datesExtracted, msgCountExtractted)
        #plt.gcf().autofmt_xdate()
        plt.xticks(rotation=25, ha='right')

        plt.savefig("graphshit.png")

        file = discord.File(f"graphshit.png",filename=f"graphshit.png")

        await ctx.respond(file=file)

    @discord.slash_command(guild_ids=testingservers, name="top_all", description="Show top chatters for all channels")
    async def top_all(self, ctx: discord.ApplicationContext,
                      time_amount: discord.Option(int, "Past x hours", min_value=1, max_value=100000),
                      time_format: discord.Option(str, "Week, day or hour", choices=["Hour", "Day", "Week", "Alltime"]),
                      top_x: discord.Option(int, "Amount of ppl on leaderboard", min_value=1, max_value=100,
                                            required=False)):
        if top_x is None:
            top_x = 10

        mysql_time = time_amount
        if time_format == "Day":
            mysql_time = time_amount * 24
        if time_format == "Week":
            mysql_time = time_amount * 24 * 7
        if time_format == "Alltime":
            mysql_time = 100000
        mysql_time = min(mysql_time, 100000)
        # print(mysql_time)

        await ctx.defer()  # it avoids timeout when grabbing data from table
        mycursor.execute(f"SELECT authorName,COUNT(*) as count,authorID FROM `{ctx.guild.id}`.loggedmsgs "
                         f"WHERE date_format(datetimeMSG, '%Y-%m-%d-%T') >= NOW() - INTERVAL {mysql_time} hour "
                         f"and guildID = {ctx.guild.id} GROUP BY authorID ORDER BY count DESC")
        table = mycursor.fetchall()  # grabs table sorted
        #print(f"test {table}")

        number_of_authors = 0
        totalmsgs = 0
        for x in table:  # get sum of count xd
            totalmsgs = totalmsgs + x[1]
            number_of_authors += 1  # get number of authors if <10

        number_of_authors = min(top_x, number_of_authors)  # to take specified amount, or less if less authors.

        if time_format == "Alltime":
            time_amount = " "

        mycursor.execute(f"SELECT messageChan,COUNT(*) as count FROM `{ctx.guild.id}`.loggedmsgs "
                         f" where date_format(datetimeMSG, '%Y-%m-%d-%T') >= (NOW() - INTERVAL {mysql_time} hour) "
                         f" and guildID = {ctx.guild.id}"
                         f" group by messageChan order by count desc")
        channel_table = mycursor.fetchall()  # grabs table sorted

        top_channel_str = ""

        for x in range(3):  # add top channels to table
            try:
                top_channel_str = top_channel_str + f"{x + 1}. <#{channel_table[x][0]}> - `{channel_table[x][1]}` msgs\n"
                # print("added")

            except:
                top_channel_str = top_channel_str + "."
                # print("FAILED")

        # print(len(top_channel_str))
        if len(top_channel_str) < 4:
            top_channel_str = "None"

        embed = discord.Embed(
            title=f"{ctx.guild.name} - All channels",
            description=f"`{totalmsgs}` messages sent past `{time_amount} {time_format}(s)` \n"
                        f" ** MPH ** : {round(totalmsgs / (mysql_time), 2)} ",
            color=discord.Color.purple(),
        )
        embed.set_thumbnail(url=f"{ctx.guild.icon.url}")

        embed_body = ""
        rank_number = 1
        for author in range(number_of_authors):
            number_x = table[author]
            ranked = rank_number  # avoid error with converting 1 to medal, then having medal +1
            if rank_number == 1:  # change 1.2.3.
                ranked = "🥇"
            if rank_number == 2:  # change 1.2.3.
                ranked = "🥈"
            if rank_number == 3:  # change 1.2.3.
                ranked = "🥉"
            if rank_number > 3:
                ranked = f"{rank_number}."  # adds dot at end, and not on medals
            embed_body = embed_body + f"{ranked} {number_x[0]} - `{number_x[1]}` \n"
            rank_number += 1

        if len(embed_body) > 1024:
            embed_body = embed_body[0:1022]

        embed.add_field(name=f"Most used channels", value=f"{top_channel_str}", inline=False)
        embed.add_field(name=f"Top Typers", value=f"{embed_body}", inline=False)
        await ctx.respond(embed=embed)

def setup(bot):
    bot.add_cog(Logging(bot))