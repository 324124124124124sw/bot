import random
import asyncio
import discord
import os
import random
import imageio
import PIL
from PIL import Image, ImageFont, ImageDraw
from pathlib import Path
from math import ceil, floor, log

from discord.ui import InputText, Modal, Select

from .logging import *



def checkIfUserinDB(user_ID):
    mycursor.execute(
        f"SELECT * FROM gambledb.points where authorID = {user_ID}"
    )
    table = mycursor.fetchall()

    return table


def addUserToDB(user_ID, author_display_name):
    mycursor.execute(
        f"INSERT INTO gambledb.points (authorID, authorName, points, gambleWin, gambleLose, gambleProfit, duelWin, duelLose, duelProfit, bjWin, bjLose, bjProfit) "
        f"VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
        (user_ID, author_display_name, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0))
    db.commit()


def pickCard():
    card_points = ['A', 'K', 'Q', 'J', '2', '3', '4', '5', '6', '7', '8', '9', '10']
    card_signs = ['Heart', 'CLUB', 'DIAMOND', 'SPADE']
    random_point = random.choice(card_points)
    random_sign = random.choice(card_signs)
    random_card = random_point, random_sign

    card_value = random_point
    list = ["K","Q","J"]
    if card_value in list:
        card_value = 10
    if card_value == "A":
        card_value = 11

    return random_point, card_value

class duelButton(discord.ui.View):
    # Define the actual button
    # When pressed, this increments the number displayed until it hits 5.
    # When it hits 5, the counter button is disabled and it turns green.
    # NOTE: The name of the function does not matter to the library
    @discord.ui.button(label="Accept duel", style=discord.ButtonStyle.green, emoji="🗡️")
    async def duel1(self, button: discord.ui.Button, interaction: discord.Interaction):
        embed = (interaction.message.embeds[0])
        embed_dict = embed.to_dict()
        #print(embed_dict)
        amount = str((embed_dict["fields"][0]["value"]))
        amount = int(amount.replace("`",""))
        #print(amount*2)

        opponent = interaction.user
        author_ID = int(embed_dict["footer"]["text"])  # CHECKS IF RIGHT ID
        guild = interaction.guild
        author_men = guild.get_member(author_ID)

        if interaction.user.id == author_ID: #REMOVE NOT
            await interaction.response.send_message(
                "y u duel uself????",ephemeral=True)
        else:
            author_table = checkIfUserinDB(author_ID)
            author_points = int(author_table[0][2])

            opponent_table = checkIfUserinDB(opponent.id)
            opponent_points = int(opponent_table[0][2])

            if author_points >= amount and opponent_points >= amount:
                embed = discord.Embed(
                    title=f"Duel for `{amount}` points has been accepted by `{interaction.user.display_name}` "
                          f"\n\n `{author_men.display_name}` vs `{opponent.display_name}`"
                          f"\n\n Starting within **5s** (yes i know its slow)"
                )
                try:
                    embed.set_author(name=f"{interaction.user.display_name}", icon_url=f"{interaction.user.avatar.url}")
                except:
                    embed.set_author(name=f"{interaction.user.display_name}", icon_url=f"{interaction.user.default_avatar.url}")

                await interaction.response.edit_message(embed=embed,view=None)
                mycursor.execute(
                    f"update gambledb.points set points = {author_points - amount}  where authorID = {author_ID}")
                mycursor.execute(
                    f"update gambledb.points set points = {opponent_points - amount} where authorID = {opponent.id}")
                db.commit()


                tent_max = 25
                author_hp = 99
                user_hp = 99
                pid_roll = random.randint(1, 2)
                author_hits = []
                author_hp_table = []
                user_hits = []
                user_hp_table = []
                hits = 0
                author_displayname = str(author_men.display_name)[0:min(len(author_men.display_name), 15)]
                print(author_displayname)
                user_display_name = str(opponent.display_name)[0:min(len(opponent.display_name), 15)]
                print(user_display_name)
                if pid_roll == 1:  # REMEMBER TO FIX FOR WINNER
                    pid_loser = author_displayname
                    pid_winner = opponent
                elif pid_roll == 2:
                    pid_loser = user_display_name
                    pid_winner = author_men

                while author_hp > 0 and user_hp > 0:
                    authoraccroll = random.uniform(0, 1)
                    useraccroll = random.uniform(0, 1)
                    if authoraccroll < 0.8:
                        author_dmg = random.randint(0, tent_max)
                        author_hits.append(author_dmg)
                    else:
                        author_dmg = 0
                        author_hits.append(author_dmg)

                    if useraccroll < 0.8:
                        user_dmg = random.randint(0, tent_max)
                        user_hits.append(user_dmg)
                    else:
                        user_dmg = 0
                        user_hits.append(user_dmg)
                    hits += 1

                    user_hp = max(0, user_hp - author_dmg)
                    user_hp_table.append(user_hp)
                    author_hp = max(0, author_hp - user_dmg)
                    author_hp_table.append(author_hp)

                # print(hits)
                # print(f"ATHOR HP {author_hp_table}")
                # print(author_hits)
                # print(f"user hp {user_hp_table}")
                # print(user_hits)

                # path of the folder containing the raw images
                inPath = "image_folder/"

                # path of the folder that will contain the modified image
                outPath = "gut/"
                ### START IMAGES
                for y in range(4):
                    for imagePath in os.listdir("start/"):
                        # imagePath contains name of the image
                        inputPath = os.path.join("start/", imagePath)

                        # inputPath contains the full directory name
                        img = Image.open(inputPath)
                        imagePath = str(imagePath).replace(".png", "")
                        fullOutPath = f"{outPath}/0-{imagePath}{y + 1}.png"
                        # fullOutPath contains the path of the output
                        # image that needs to be generated
                        # img = img.rotate(180)

                        img.save(fullOutPath, optimize=True, quality=95)

                        img.close()

                for x in range(hits):
                    for imagePath in os.listdir(inPath):
                        # imagePath contains name of the image
                        inputPath = os.path.join(inPath, imagePath)

                        # inputPath contains the full directory name
                        img = Image.open(inputPath)
                        if x < 8:
                            new_num = x
                        elif x == 8:
                            new_num = 98
                        elif x == 9:
                            new_num = 998
                        elif x == 10:
                            new_num = 9998
                        elif x == 11:
                            new_num = 99998
                        elif x == 12:
                            new_num = 999998
                        elif x == 13:
                            new_num = 9999998
                        elif x == 14:
                            new_num = 99999998
                        elif x == 15:
                            new_num = 99999998
                        elif x == 16:
                            new_num = 999999998
                        elif x == 17:
                            new_num = 9999999998
                        fullOutPath = f"{outPath}/{new_num + 1}-{imagePath}"
                        # fullOutPath contains the path of the output
                        # image that needs to be generated
                        # img = img.rotate(180)
                        title_font = ImageFont.truetype('osrs-font.ttf', 16)  # text and font size

                        image_editable = ImageDraw.Draw(img)

                        # AUTHOR NAME
                        author_name = str(f"{author_displayname}")  # text split up from arg
                        image_editable.text((51, 41), author_name, fill=(0, 0, 0), font=title_font)  # black shadow/outline
                        image_editable.text((50, 40), author_name, fill=(0, 255, 255), font=title_font)  # actual text
                        # USER NAME
                        user_name = str(f"{user_display_name}")  # text split up from arg
                        image_editable.text((174, 41), user_name, fill=(0, 0, 0), font=title_font)  # black shadow/outline
                        image_editable.text((173, 40), user_name, fill=(0, 255, 255), font=title_font)  # actual text

                        # ADD HP BARS
                        img = img.convert('RGBA')
                        # AUTHOR
                        foreground = Image.open(f"stuffs/{ceil((author_hp_table[x]) / 10) * 10}.png")
                        img.paste(foreground, (50, 58))

                        # USER
                        foreground = Image.open(f"stuffs/{ceil((user_hp_table[x]) / 10) * 10}.png")
                        img.paste(foreground, (167, 58))

                        # ADD HITSPLAT
                        if author_hits[x] == 0:
                            hitplat_img_auth = "stuffs/miss2.png"
                        else:
                            hitplat_img_auth = "stuffs/hit2.png"
                        image_editable = ImageDraw.Draw(img)
                        if user_hits[x] == 0:
                            hitplat_img_user = "stuffs/miss2.png"
                        else:
                            hitplat_img_user = "stuffs/hit2.png"
                        # author
                        foreground = Image.open(hitplat_img_user).convert("RGBA")
                        img.paste(foreground, (67, 150), foreground)

                        # user
                        foreground = Image.open(hitplat_img_auth).convert("RGBA")
                        img.paste(foreground, (189, 150), foreground)

                        # ADD DAMAGE TEXT
                        title_font = ImageFont.truetype('osrs-font.ttf', 26)
                        image_editable = ImageDraw.Draw(img)
                        if len(str(user_hits[x])) == 1:
                            extra_len_auth = 7
                        else:
                            extra_len_auth = 0

                        if len(str(author_hits[x])) == 1:
                            extra_len_user = 9
                        else:
                            extra_len_user = 0

                        author_hit = str(user_hits[x])  # text split up from arg
                        image_editable.text(((71 + extra_len_auth), 154), author_hit, fill=(0, 0, 0),
                                            font=title_font)  # black shadow/outline
                        image_editable.text(((70 + extra_len_auth), 153), author_hit, fill=(255, 255, 255),
                                            font=title_font)  # actual text
                        # USER NAME
                        user_hit = str(author_hits[x])  # text split up from arg
                        image_editable.text(((193 + extra_len_user), 154), user_hit, fill=(0, 0, 0),
                                            font=title_font)  # black shadow/outline
                        image_editable.text(((192 + extra_len_user), 153), user_hit, fill=(255, 255, 255),
                                            font=title_font)  # actual text

                        img.save(fullOutPath, optimize=True, quality=95)

                        img.close()

                        # print(fullOutPath)

                # DEATJ STUFF
                user_hp_end = user_hp_table[hits - 1]
                author_hp_end = author_hp_table[hits - 1]

                if user_hp_end == 0 and author_hp_end == 0:
                    dir_for_folder = "death/both"
                    sit_text = f"SIT {pid_loser}"
                    winner_id = pid_winner
                elif user_hp_end == 0:
                    dir_for_folder = "death/white"
                    sit_text = f"SIT {user_display_name}"
                    winner_id = author_men
                elif author_hp_end == 0:
                    dir_for_folder = "death/black"
                    sit_text = f"SIT {author_displayname}"
                    winner_id = opponent

                for z in range(2):
                    # get death folder
                    for imagePath in os.listdir(dir_for_folder):
                        # imagePath contains name of the image
                        inputPath = os.path.join(dir_for_folder, imagePath)

                        # inputPath contains the full directory name
                        img = Image.open(inputPath)

                        title_font = ImageFont.truetype('osrs-font.ttf', 16)  # text and font size

                        image_editable = ImageDraw.Draw(img)

                        # AUTHOR NAME
                        author_name = str(f"{author_displayname}")  # text split up from arg
                        image_editable.text((36, 245), author_name, fill=(0, 0, 0), font=title_font)  # black shadow/outline
                        image_editable.text((35, 244), author_name, fill=(0, 255, 255), font=title_font)  # actual text
                        # USER NAME
                        user_name = str(f"{user_display_name}")  # text split up from arg
                        image_editable.text((194, 245), user_name, fill=(0, 0, 0), font=title_font)  # black shadow/outline
                        image_editable.text((193, 244), user_name, fill=(0, 255, 255), font=title_font)  # actual text

                        # SIT
                        title_font = ImageFont.truetype('osrs-font.ttf', 40)  # text and font size
                        image_editable.text((10, 11), sit_text, fill=(0, 0, 0), font=title_font)  # black shadow/outline
                        image_editable.text((9, 10), sit_text, fill=(0, 255, 255), font=title_font)  # actual text

                        imagePath = str(imagePath).replace(".png", "")
                        fullOutPath = f"{outPath}/9999999999{imagePath}{z + 1}.png"
                        # fullOutPath contains the path of the output
                        # image that needs to be generated
                        # img = img.rotate(180)

                        img.save(fullOutPath, optimize=True, quality=95)

                        img.close()

                # make gif
                image_folder = 'gut/'

                images = []
                for file_name in sorted(os.listdir(image_folder)):
                    if file_name.endswith('.png'):
                        file_path = os.path.join(image_folder, file_name)
                        images.append(imageio.imread(file_path))
                imageio.mimsave('hehe.gif', images)

                # cleanup folder
                [f.unlink() for f in Path("gut").glob("*") if f.is_file()]

                msg1 = await interaction.channel.send(file=discord.File("hehe.gif"))
                await asyncio.sleep((2+(1*hits)+1)) #edit time to match gif

                #HAND OUT POINTS
                author_table = checkIfUserinDB(author_ID)
                author_points = int(author_table[0][2])

                opponent_table = checkIfUserinDB(opponent.id)
                opponent_points = int(opponent_table[0][2])

                winner_table = checkIfUserinDB(winner_id.id)
                winner_points = int(winner_table[0][2])

                if winner_id.id == author_ID:
                    mycursor.execute( #author WIN
                        f"update gambledb.points set points = {author_points + amount*2}, duelWin = {int(author_table[0][6])+1},duelProfit={int(author_table[0][8])+amount}  where authorID = {author_ID}")
                    mycursor.execute( #opponent LOSE
                        f"update gambledb.points set points = {opponent_points}, duelLose = {int(opponent_table[0][7]) + 1},duelProfit={int(opponent_table[0][8]) - amount}  where authorID = {opponent.id}")
                else:
                    mycursor.execute( #opponent WIN
                        f"update gambledb.points set points = {opponent_points + amount*2}, duelWin = {int(opponent_table[0][6])+1},duelProfit={int(opponent_table[0][8])+amount}  where authorID = {opponent.id}")
                    mycursor.execute( #author LOSE
                        f"update gambledb.points set points = {author_points}, duelLose = {int(author_table[0][7]) + 1},duelProfit={int(author_table[0][8]) - amount}  where authorID = {author_ID}")

                db.commit()


                await msg1.edit(f"gz on win **`{winner_id.display_name}`**. Gain `{amount}` points. Total points : {winner_points+amount*2}")


            else: #point check
                await interaction.response.send_message(f"<a:Begging:907745181254680576> either you or {author_men.display_name} miss points",ephemeral=True)

def checkIfUserHasTickets(user_ID, lotteryID):
    mycursor.execute(
        f"SELECT * FROM gambledb.lottery where userID = {user_ID} and lotteryID = {lotteryID}"
    )
    table = mycursor.fetchall()

    return table


class MyView1(discord.ui.View):
    @discord.ui.select(  # the decorator that lets you specify the properties of the select menu
        placeholder="Which times are you available (IN GMT)!",  # the placeholder text that will be displayed if nothing is selected
        min_values=1,  # the minimum number of values that must be selected by the users
        max_values=24,  # the maxmimum number of values that can be selected by the users
        options=[  # the list of options from which users can choose, a required field
            discord.SelectOption(
                label="00-01",
            ), discord.SelectOption(
                label="01-02",
            ), discord.SelectOption(
                label="02-03",
            ), discord.SelectOption(
                label="03-04",
            ), discord.SelectOption(
                label="04-05",
            ), discord.SelectOption(
                label="05-06",
            ), discord.SelectOption(
                label="06-07",
            ), discord.SelectOption(
                label="07-08",
            ), discord.SelectOption(
                label="08-09",
            ), discord.SelectOption(
                label="09-10",
            ), discord.SelectOption(
                label="10-11",
            ), discord.SelectOption(
                label="11-12",
            ), discord.SelectOption(
                label="12-13",
            ), discord.SelectOption(
                label="13-14",
            ), discord.SelectOption(
                label="14-15",
            ), discord.SelectOption(
                label="15-16",
            ), discord.SelectOption(
                label="16-17",
            ), discord.SelectOption(
                label="17-18",
            ), discord.SelectOption(
                label="18-19",
            ), discord.SelectOption(
                label="19-20",
            ), discord.SelectOption(
                label="20-21",
            ), discord.SelectOption(
                label="21-22",
            ), discord.SelectOption(
                label="22-23",
            ), discord.SelectOption(
                label="23-24",
            )
        ]
    )
    async def select_callback(self, select,interaction):  # the function called when the user is done selecting options
        await interaction.response.send_message(
            f"{interaction.user.display_name}. Your available times {select.values} have been submitted", ephemeral=True)
        print(select.values)



class lotteryButton(discord.ui.View):
    # Define the actual button
    # When pressed, this increments the number displayed until it hits 5.
    # When it hits 5, the counter button is disabled and it turns green.
    # NOTE: The name of the function does not matter to the library
    @discord.ui.button(label="First ticket free", style=discord.ButtonStyle.green, emoji="🆓")
    async def get_free_ticket(self, button: discord.ui.Button, interaction: discord.Interaction):
        embed = (interaction.message.embeds[0])
        embed_dict = embed.to_dict()
        lotteryID = embed_dict["footer"]["text"]

        table_check = checkIfUserinDB(interaction.user.id)

        if len(table_check) > 0:
            table = checkIfUserHasTickets(interaction.user.id,lotteryID)

            if len(table) == 0:
                mycursor.execute(
                    f"INSERT INTO gambledb.lottery (userID, ticketAmount, displayName, lotteryID) "
                    f"VALUES (%s, %s, %s, %s)",
                    (interaction.user.id, 1, interaction.user.display_name, lotteryID))
                db.commit()
                await interaction.response.send_message("<:uwu:904501797069160488>You have gotten a free ticket! Total tickets: `1`<:uwu:904501797069160488>", ephemeral=True)
            else:
                await interaction.response.send_message("<:LaupIQ:809630782586224640>You already have tickets! Only first free!<:LaupIQ:809630782586224640>",ephemeral=True)
        else:
            addUserToDB(interaction.user.id, interaction.user.display_name)
            mycursor.execute(
                f"INSERT INTO gambledb.lottery (userID, ticketAmount, displayName, lotteryID) "
                f"VALUES (%s, %s, %s, %s)",
                (interaction.user.id, 1, interaction.user.display_name, lotteryID))
            db.commit()
            await interaction.response.send_message(
                "<:uwu:904501797069160488>You have gotten a free ticket! Total tickets: `1`<:uwu:904501797069160488>",
                ephemeral=True)


    @discord.ui.button(label="Buy 1 ticket", style=discord.ButtonStyle.primary, emoji="1️⃣")
    async def buy_one_ticket(self, button: discord.ui.Button, interaction: discord.Interaction):
        #print("buy 1")
        embed = (interaction.message.embeds[0])
        embed_dict = embed.to_dict()
        lotteryID = embed_dict["footer"]["text"]
        table = checkIfUserHasTickets(interaction.user.id, lotteryID)


        user_points_table = checkIfUserinDB(interaction.user.id)
        user_points = int(user_points_table[0][2])
        #print(user_points)

        if len(table) == 0 and user_points >= 1000:
            await interaction.response.send_message("Get a free ticket first!",ephemeral=True)
        elif len(table) > 0 and user_points >= 1000:
            user_tickets = int(table[0][1])
            mycursor.execute(
                f"update gambledb.lottery set ticketAmount = {user_tickets+1} where userID = {interaction.user.id} and lotteryID = {lotteryID}")
            mycursor.execute(
                f"update gambledb.points set points = {user_points-1000} where authorID = {interaction.user.id}")

            db.commit()

            await interaction.response.send_message(f"Total tickets {user_tickets+1}. Balance: {user_points-1000}", ephemeral=True)
        else:
            await interaction.response.send_message("<a:Begging:907745181254680576>Too poor fuck off<a:Begging:907745181254680576>",ephemeral=True)


    @discord.ui.button(label="Buy 10 tickets", style=discord.ButtonStyle.primary, emoji="🔟")
    async def buy_ten_tickets(self, button: discord.ui.Button, interaction: discord.Interaction):
        #print("buy 10")
        embed = (interaction.message.embeds[0])
        embed_dict = embed.to_dict()
        lotteryID = embed_dict["footer"]["text"]
        table = checkIfUserHasTickets(interaction.user.id, lotteryID)

        user_points_table = checkIfUserinDB(interaction.user.id)
        user_points = int(user_points_table[0][2])
        #print(user_points)

        if len(table) == 0 and user_points >= 10000:
            await interaction.response.send_message("Get a free ticket first!", ephemeral=True)
        elif len(table) > 0 and user_points >= 10000:
            user_tickets = int(table[0][1])
            mycursor.execute(
                f"update gambledb.lottery set ticketAmount = {user_tickets + 10} where userID = {interaction.user.id} and lotteryID = {lotteryID}")
            mycursor.execute(
                f"update gambledb.points set points = {user_points - 10000} where authorID = {interaction.user.id}")

            db.commit()

            await interaction.response.send_message(f"Total tickets {user_tickets + 10}. Balance: {user_points - 10000}",
                                                    ephemeral=True)
        else:
            await interaction.response.send_message("<a:Begging:907745181254680576>Too poor fuck off<a:Begging:907745181254680576>", ephemeral=True)

    @discord.ui.button(label="Lottery role(for ping)", style=discord.ButtonStyle.primary, emoji="🏓")
    async def get_lottery_role(self, button: discord.ui.Button, interaction: discord.Interaction):
        user_roles = [r.id for r in interaction.user.roles]
        role = discord.utils.get(interaction.user.guild.roles, id=996897096814837941)

        if 996897096814837941 in user_roles:
            await interaction.user.remove_roles(role)
            await interaction.response.send_message("Lottery role has been removed - react again to get it back",ephemeral=True)

        else:
            await interaction.user.add_roles(role)
            await interaction.response.send_message("Lottery role has been added - react again to remove",ephemeral=True)



class BjButtons(discord.ui.View):
    # Define the actual button
    # When pressed, this increments the number displayed until it hits 5.
    # When it hits 5, the counter button is disabled and it turns green.
    # NOTE: The name of the function does not matter to the library
    @discord.ui.button(label="Hit", style=discord.ButtonStyle.green, emoji="🎯")
    async def count(self, button: discord.ui.Button, interaction: discord.Interaction):
        cardx, valuex = pickCard() #FOR AUTHOR
        #print(f"cardx {cardx}")
        #print(f"valuex {valuex}")

        embed = (interaction.message.embeds[0])
        embed_dict = embed.to_dict()

        interactionUserID = embed_dict["footer"]["text"] #CHECKS IF RIGHT ID
        if not interaction.user.id == int(interactionUserID):
            await interaction.response.send_message("<a:Begging:907745181254680576> Gamba on your own faggot <a:Begging:907745181254680576>",ephemeral=True)

        else:
            ############### GET PESOS AMOUNT
            pesos_amount = ""
            for m in str(embed_dict["title"]):
                if m.isdigit():
                    pesos_amount = pesos_amount + m
            pesos_amount = int(pesos_amount)

            #print(embed_dict)
            for field in embed_dict["fields"]:
                if "You" in field["name"]:
                    get_numbers = field["name"] #gets field of author_points
                    #print(get_numbers)
                    length_get = len(get_numbers) #len of strength
                    new_data = int(get_numbers[length_get-2:length_get]) #gets number (always last 2 letters cuz of space)
                    #print(f"newdata {new_data}")
                    get_cards = field["value"]
                    #print(f"getcards {get_cards}")


                    new_get_cards = f"{get_cards}, {cardx}" #added latest card draw
                    number_of_aces = new_get_cards.count("A")
                    #print(number_of_aces)

                    author_roll_total = new_data+int(valuex) #total including new roll
                    #print(f"total {author_roll_total}")
                    if author_roll_total > 21 and number_of_aces > 0:
                        author_roll_total = author_roll_total-10
                        new_get_cards = new_get_cards.replace("A","a")

                    # SETS NEW VALUES!
                    field["name"] = f"You | {author_roll_total}"
                    #print(field["value"])
                    field["value"] = new_get_cards

            table = checkIfUserinDB(interaction.user.id)
            author_points = int(table[0][2])
            embed = discord.Embed.from_dict(embed_dict)
            if author_roll_total == 21: #win
                mycursor.execute(
                    f"update gambledb.points set points = {author_points + (pesos_amount * 2)}, bjWin ={(int(table[0][9]))+1}, bjProfit = {(int(table[0][11]))+pesos_amount} where authorID = {interaction.user.id}")
                db.commit()
                embed.add_field(name="Winner", value=f"You won {pesos_amount} points. Total {author_points+(pesos_amount*2)}")  # ADD POINTS

                await interaction.response.edit_message(embed=embed, view=None)
            elif author_roll_total > 21: #LOSE
                embed.add_field(name="Loser", value=f"You lost {pesos_amount} points. Total {author_points}") #REMOVE POINTS
                mycursor.execute(
                    f"update gambledb.points set bjLose ={(int(table[0][10])) + 1}, bjProfit = {(int(table[0][11])) - pesos_amount} where authorID = {interaction.user.id}")
                db.commit()

                await interaction.response.edit_message(embed=embed,view=None)
            else: #hit again xD
                await interaction.response.edit_message(embed=embed, view=self)


    @discord.ui.button(label="Stand", style=discord.ButtonStyle.red, emoji="🛑")
    async def count1(self, button: discord.ui.Button, interaction: discord.Interaction):
        embed = (interaction.message.embeds[0])
        embed_dict = embed.to_dict()
        #print(embed_dict)

        interactionUserID = embed_dict["footer"]["text"]  # CHECKS IF RIGHT ID
        if not interaction.user.id == int(interactionUserID):
            await interaction.response.send_message(
                "<a:Begging:907745181254680576> Gamba on your own faggot <a:Begging:907745181254680576>",
                ephemeral=True)

        else:

            #GET PESOS AMOUNT
            ############### GET PESOS AMOUNT
            pesos_amount = ""
            for m in str(embed_dict["title"]):
                if m.isdigit():
                    pesos_amount = pesos_amount + m
            pesos_amount = int(pesos_amount)

            ############### DEALER DATA
            for field in embed_dict["fields"]:
                if "Dealer" in field["name"]:
                    get_numbers = field["name"]  # gets field of Dealer_points
                    #print(get_numbers)
                    length_get = len(get_numbers)  # len of strength
                    new_data = int(get_numbers[length_get - 2:length_get])  # gets number (always last 2 letters cuz of space)
                    #print(f"newdata {new_data}")
                    get_cards = field["value"]
                    #print(f"getcards {get_cards}")

                    new_get_cards = get_cards
                    ######### DRAW 1

                    cardx, valuex = pickCard()
                    #print(f"NEW DRAWWWWWW {cardx}")
                    new_get_cards = f"{new_get_cards}, {cardx}"  # added latest card draw
                    number_of_aces = new_get_cards.count("A")
                    #print(number_of_aces)

                    author_roll_total = new_data + int(valuex)  # total including new roll
                    #print(f"total {author_roll_total}")
                    if author_roll_total > 21 and number_of_aces > 0:
                        author_roll_total = author_roll_total - 10
                        new_get_cards = new_get_cards.replace("A", "a")


                    while author_roll_total < 17:
                        cardx1, valuex1 = pickCard()  # FOR DEALER

                        new_get_cards = f"{new_get_cards}, {cardx1}"  # added latest card draw
                        number_of_aces = new_get_cards.count("A")
                        #print(number_of_aces)

                        author_roll_total = author_roll_total + int(valuex1)  # total including new roll
                        #print(f"total {author_roll_total}")
                        if author_roll_total > 21 and number_of_aces > 0:
                            author_roll_total = author_roll_total - 10
                            new_get_cards = new_get_cards.replace("A", "a")


                    # SETS NEW VALUES!
                    field["name"] = f"Dealer | {author_roll_total}"
                    #print(field["value"])
                    field["value"] = new_get_cards

            DEALER_POINTS = author_roll_total

            ########## AUTHOR DATA
            for field in embed_dict["fields"]:
                if "You" in field["name"]:
                    get_numbers = field["name"]  # gets field of Authoir Points
                    #print(get_numbers)
                    length_get = len(get_numbers)  # len of strength
                    AUTHOR_POINTS = int(get_numbers[length_get - 2:length_get])  # gets number (always last 2 letters cuz of space)
                    #print(f"AUTHOR_POINTSAUTHOR_POINTSAUTHOR_POINTSAUTHOR_POINTS {AUTHOR_POINTS}")


            table = checkIfUserinDB(interaction.user.id)
            author_points = int(table[0][2])

            embed = discord.Embed.from_dict(embed_dict)


            if DEALER_POINTS > 21:
                embed.add_field(name="Winner",value=f"You won {pesos_amount} points. Total {author_points+(pesos_amount*2)}")
                mycursor.execute(
                    f"update gambledb.points set points = {author_points + (pesos_amount * 2)}, bjWin ={(int(table[0][9]))+1}, bjProfit = {(int(table[0][11]))+pesos_amount} where authorID = {interaction.user.id}")
                db.commit()

                await interaction.response.edit_message(embed=embed, view=None)
            elif DEALER_POINTS > AUTHOR_POINTS:
                embed.add_field(name="Loser",value=f"You lost {pesos_amount} points. Total {author_points}")
                mycursor.execute(
                    f"update gambledb.points set bjLose ={(int(table[0][10])) + 1}, bjProfit = {(int(table[0][11])) - pesos_amount} where authorID = {interaction.user.id}")
                db.commit()

                await interaction.response.edit_message(embed=embed, view=None)
            elif DEALER_POINTS < AUTHOR_POINTS:
                embed.add_field(name="Winner",value=f"You won {pesos_amount} points, Total {author_points+pesos_amount*2}")
                mycursor.execute(
                    f"update gambledb.points set points = {author_points + (pesos_amount * 2)}, bjWin ={(int(table[0][9]))+1}, bjProfit = {(int(table[0][11]))+pesos_amount} where authorID = {interaction.user.id}")
                db.commit()

                await interaction.response.edit_message(embed=embed, view=None)
            elif DEALER_POINTS == AUTHOR_POINTS:
                embed.add_field(name="Draw",value=f"No change")
                mycursor.execute(
                    f"update gambledb.points set points = {author_points + (pesos_amount)} where authorID = {interaction.user.id}")
                db.commit()
                await interaction.response.edit_message(embed=embed, view=None)


    @discord.ui.button(label="Double", style=discord.ButtonStyle.primary, emoji="⏭️")
    async def count2(self, button: discord.ui.Button, interaction: discord.Interaction):
        embed = (interaction.message.embeds[0])
        embed_dict = embed.to_dict()

        #print(embed_dict)

        interactionUserID = embed_dict["footer"]["text"]  # CHECKS IF RIGHT ID
        if not interaction.user.id == int(interactionUserID):
            await interaction.response.send_message("<a:Begging:907745181254680576> Gamba on your own faggot <a:Begging:907745181254680576>",ephemeral=True)
        else:
            pesos_amount = ""
            for m in str(embed_dict["title"]):
                if m.isdigit():
                    pesos_amount = pesos_amount + m
            pesos_amount = int(pesos_amount)

            table = checkIfUserinDB(interaction.user.id)
            author_points = int(table[0][2])

            if author_points >= pesos_amount:
                mycursor.execute(
                    f"update gambledb.points set points = {author_points - pesos_amount} where authorID = {interaction.user.id}")
                db.commit()

                #### author Draw one card
                cardx, valuex = pickCard()  # FOR AUTHOR
                # print(embed_dict)
                for field in embed_dict["fields"]:
                    if "You" in field["name"]:
                        get_numbers = field["name"]  # gets field of author_points
                        # print(get_numbers)
                        length_get = len(get_numbers)  # len of strength
                        new_data = int(
                            get_numbers[length_get - 2:length_get])  # gets number (always last 2 letters cuz of space)
                        # print(f"newdata {new_data}")
                        get_cards = field["value"]
                        # print(f"getcards {get_cards}")

                        new_get_cards = f"{get_cards}, {cardx}"  # added latest card draw
                        number_of_aces = new_get_cards.count("A")
                        # print(number_of_aces)

                        author_roll_total = new_data + int(valuex)  # total including new roll
                        # print(f"total {author_roll_total}")
                        if author_roll_total > 21 and number_of_aces > 0:
                            author_roll_total = author_roll_total - 10
                            new_get_cards = new_get_cards.replace("A", "a")

                        # SETS NEW VALUES!
                        field["name"] = f"You | {author_roll_total}"
                        # print(field["value"])
                        field["value"] = new_get_cards

                embed = discord.Embed.from_dict(embed_dict)
                new_authro_rollo = int(author_roll_total)

                table = checkIfUserinDB(interaction.user.id)
                author_points = int(table[0][2])
                #print(f"AUTHOR ROLLLLLLLLL {author_roll_total}")
                if author_roll_total > 21:
                    #LOSE
                    #print("LOSE 1")
                    mycursor.execute(
                        f"update gambledb.points set bjLose ={(int(table[0][10])) + 1}, bjProfit = {(int(table[0][11])) - pesos_amount * 2} where authorID = {interaction.user.id}")
                    db.commit()
                    embed.add_field(name="Loser", value=f"You lost {pesos_amount*2} points.  Total {author_points}")
                    await interaction.response.edit_message(embed=embed, view=None)
                elif author_roll_total == 21:
                    #WIN
                    #print("WIN2323")
                    mycursor.execute(
                        f"update gambledb.points set points = {author_points + (pesos_amount * 4)}, bjWin ={(int(table[0][9])) + 1}, bjProfit = {(int(table[0][11])) + pesos_amount * 2} where authorID = {interaction.user.id}")
                    db.commit()
                    embed.add_field(name="Winner",value=f"You won {pesos_amount*4} points, Total {author_points + pesos_amount * 4}")
                    await interaction.response.edit_message(embed=embed, view=None)
                else:
                    #print("DEALER ROLLS")
                    #DEALER ROLLS
                    embed_dict = embed.to_dict()
                    for field in embed_dict["fields"]:
                        if "Dealer" in field["name"]:
                            get_numbers = field["name"]  # gets field of Dealer_points
                            # print(get_numbers)
                            length_get = len(get_numbers)  # len of strength
                            new_data = int(get_numbers[
                                           length_get - 2:length_get])  # gets number (always last 2 letters cuz of space)
                            # print(f"newdata {new_data}")
                            get_cards = field["value"]
                            # print(f"getcards {get_cards}")

                            new_get_cards = get_cards
                            ######### DRAW 1

                            cardx, valuex = pickCard()
                            # print(f"NEW DRAWWWWWW {cardx}")
                            new_get_cards = f"{new_get_cards}, {cardx}"  # added latest card draw
                            number_of_aces = new_get_cards.count("A")
                            # print(number_of_aces)

                            author_roll_total = new_data + int(valuex)  # total including new roll
                            # print(f"total {author_roll_total}")
                            if author_roll_total > 21 and number_of_aces > 0:
                                author_roll_total = author_roll_total - 10
                                new_get_cards = new_get_cards.replace("A", "a")

                            while author_roll_total < 17:
                                cardx1, valuex1 = pickCard()  # FOR DEALER

                                new_get_cards = f"{new_get_cards}, {cardx1}"  # added latest card draw
                                number_of_aces = new_get_cards.count("A")
                                # print(number_of_aces)

                                author_roll_total = author_roll_total + int(valuex1)  # total including new roll
                                # print(f"total {author_roll_total}")
                                if author_roll_total > 21 and number_of_aces > 0:
                                    author_roll_total = author_roll_total - 10
                                    new_get_cards = new_get_cards.replace("A", "a")

                            # SETS NEW VALUES!
                            field["name"] = f"Dealer | {author_roll_total}"
                            # print(field["value"])
                            field["value"] = new_get_cards

                    DEALER_POINTS = author_roll_total
                    #print(f"DEALER POINTS {DEALER_POINTS}")

                    embed = discord.Embed.from_dict(embed_dict)
                    if DEALER_POINTS > 21:
                        #print("NEW 1")
                        embed.add_field(name="Winner",
                                        value=f"You won {pesos_amount*2} points. Total {author_points + (pesos_amount * 4)}")
                        mycursor.execute(
                            f"update gambledb.points set points = {author_points + (pesos_amount * 4)}, bjWin ={(int(table[0][9])) + 1}, bjProfit = {(int(table[0][11])) + pesos_amount * 2} where authorID = {interaction.user.id}")
                        db.commit()

                        await interaction.response.edit_message(embed=embed, view=None)
                    elif DEALER_POINTS > new_authro_rollo:
                        #print("NEW 2")
                        embed.add_field(name="Loser",
                                        value=f"You lost {pesos_amount*2} points. Total {author_points}")
                        mycursor.execute(
                            f"update gambledb.points set bjLose ={(int(table[0][10])) + 1}, bjProfit = {(int(table[0][11])) - pesos_amount*2} where authorID = {interaction.user.id}")
                        db.commit()

                        await interaction.response.edit_message(embed=embed, view=None)
                    elif DEALER_POINTS < new_authro_rollo:
                        #print("NEW 3")
                        embed.add_field(name="Winner",
                                        value=f"You won {pesos_amount*2} points, Total {author_points + pesos_amount * 4}")
                        mycursor.execute(
                            f"update gambledb.points set points = {author_points + (pesos_amount * 4)}, bjWin ={(int(table[0][9])) + 1}, bjProfit = {(int(table[0][11])) + pesos_amount*2} where authorID = {interaction.user.id}")
                        db.commit()

                        await interaction.response.edit_message(embed=embed, view=None)
                    elif DEALER_POINTS == new_authro_rollo:
                        #print("NEW 4")
                        embed.add_field(name="Draw", value=f"No change")
                        mycursor.execute(
                            f"update gambledb.points set points = {author_points + (pesos_amount*2)} where authorID = {interaction.user.id}")
                        db.commit()
                        await interaction.response.edit_message(embed=embed, view=None)


            else:
                button.disabled = True
                await interaction.response.edit_message(view=self)



class Gambling(commands.Cog):
    def __init__(self, bot):
        self.client = bot

    @commands.command(aliases=["pts","Points"])
    async def points(self, ctx, member_check : discord.Member = None):
        if not member_check:
            member_check = ctx.author

        table = checkIfUserinDB(member_check.id)

        if len(table) < 1:
            addUserToDB(member_check.id, member_check.display_name)
        else:
            await ctx.send(f"{member_check.display_name} has {table[0][2]} points")


    @commands.command()
    @commands.cooldown(1,3600,commands.BucketType.user)
    async def rob(self, ctx, *, rob_member):
        #######ADD remove cd
        #print(rob_member)
        try:
            member = discord.utils.get(ctx.guild.members, name=f"{rob_member}")
        except:
            pass
        if not member:
            try:
                member = discord.utils.get(ctx.guild.members, display_name=f"{rob_member}")
            except:
                pass
        if not member:
            #print("1")
            try: #GETS member from ID
                member = ctx.message.guild.get_member(int(rob_member))
            except:
                pass
        if not member:
            #print("2")
            try:
                if len(ctx.message.mentions) > 0: #ping
                    member = ctx.message.guild.get_member(int(ctx.message.mentions[0].id))
            except:
                pass

        #print(member.display_name)

        if not member:
            self.rob.reset_cooldown(ctx)
            embed = discord.Embed(
                description=f"Could not find {rob_member}"
            )
            await ctx.send(embed=embed, delete_after=5)
        else:
            member_table = checkIfUserinDB(member.id)
            author_table = checkIfUserinDB(ctx.author.id)
            author_points = int(author_table[0][2])
            member_points = int(member_table[0][2])
            #print(author_points)
            #print(member_points)

            if len(member_table) < 1:
                await ctx.send(f"{member} is not added. Do !points / !daily to get points")
            if len(author_table) < 1:
                await ctx.send(f"{ctx.author} is not added. Do !points / !daily to get points")

            rob_roll = random.randint(0,100)

            if rob_roll < 11:
                #rob fail<
                rob_lose_percent = random.uniform(0.05,0.5)
                loss = round(rob_lose_percent*author_points)
                #print(loss)
                mycursor.execute(  # takes author points
                    f"update gambledb.points set points = {author_points - loss} where authorID = {ctx.author.id}")
                db.commit()
                mycursor.execute(  # gives member points
                    f"update gambledb.points set points = {member_points + loss} where authorID = {member.id}")
                db.commit()

                await ctx.send(f"Man u dumb as fk. {member.display_name} slapped you and took {loss} points.")

            elif rob_roll > 10 and rob_roll < 21:
                #rob success
                rob_win_percent = random.uniform(0.1, 0.5)
                win = round(rob_win_percent * member_points)
                #print(win)
                mycursor.execute(  # gives author points
                    f"update gambledb.points set points = {author_points + win} where authorID = {ctx.author.id}")
                db.commit()
                mycursor.execute(  # takes member points
                    f"update gambledb.points set points = {member_points - win} where authorID = {member.id}")
                db.commit()

                await ctx.send(f"Good shit nigga. You fked up {member.display_name} and took {win} points")

            else:
                rob_gifs = ["https://c.tenor.com/LoQoNueBMw0AAAAd/travis-scott-travis-scott-apology.gif",
                            "https://tenor.com/view/shitter-alert-cake-gif-19194039",
                            "https://i.imgur.com/ydb4bgT.mp4",
                            "https://tenor.com/view/stealing-with-class-throw-bricks-hit-head-robber-fail-burglar-fail-gif-12487079",
                            "https://tenor.com/view/gun-fail-robber-crime-gif-13607306",
                            "https://tenor.com/view/glass-bump-head-robberyfail-crime-does-not-pay-gif-14054904",
                            "https://tenor.com/view/thief-stole-fail-thief-fail-gif-14524400",
                            "https://tenor.com/view/smart-fail-attempt-fat-criminal-gif-4565900",
                            "https://tenor.com/view/kick-smash-fight-thief-robbery-gif-16929456",
                            "https://gfycat.com/forkedindeliblebagworm",
                            "https://gfycat.com/jubilantdelayedkingsnake",
                            "https://gfycat.com/leadingdarlingacornbarnacle",
                            "https://gfycat.com/relievedelaborateblackbird",
                            "https://gfycat.com/unhappyinfamousacornweevil",
                            "https://c.tenor.com/YRfbbNtKwjsAAAAd/punching-boxing.gif",
                            "https://c.tenor.com/FVWRijjY-eEAAAAd/froze-stop-moving.gif"]
                await ctx.send(random.choice(rob_gifs))

    @commands.command(aliases=["lbs","LB","LBS","Lb"])
    async def lb(self, ctx, amount : int = None):
        """ LEADERBOARD FOR POINTS XDDD"""
        if not amount:
            amount = 10
        mycursor.execute(
            f"SELECT * FROM gambledb.points order by abs(points) desc limit {amount};"
        )
        table = mycursor.fetchall()

        msg_str = ""
        for num in range(min(len(table),amount)):
            rank_number = num+1
            ranked = num+1
            if rank_number == 1:  # change 1.2.3.
                ranked = "🥇"
            if rank_number == 2:  # change 1.2.3.
                ranked = "🥈"
            if rank_number == 3:  # change 1.2.3.
                ranked = "🥉"
            if rank_number > 3:
                ranked = f"{ranked}."  # adds dot at end, and not on medals

            msg_str = msg_str + f"{ranked} {table[num][1]}: `{table[num][2]}` \n"

        #print(msg_str)

        embed = discord.Embed(
            title=f"Point leaderboard xDd",
            description=f"{msg_str}",
            colour=7419530
        )

        await ctx.send(embed=embed)

    @commands.command()
    @commands.cooldown(1,22222,commands.BucketType.user) #76400
    async def daily(self, ctx):

        ############# check if user is in table already
        table = checkIfUserinDB(ctx.author.id)

        if len(table) < 1:
            addUserToDB(ctx.author.id,ctx.author.display_name)

        numberRoll = random.randint(0,100)
        if numberRoll > 49 and numberRoll < 80:
            amount = random.randint(1000,3000)
        elif numberRoll > 79:
            amount = random.randint(3000,10000)
        else:
            amount = 1000

        ########### MULTIPLIER
        mycursor.execute(f"SELECT authorID,COUNT(*) as count FROM `{ctx.guild.id}`.loggedmsgs "
                         f"WHERE date_format(datetimeMSG, '%Y-%m-%d-%T') >= NOW() - INTERVAL 24 hour "
                         f"and guildID = {ctx.guild.id} GROUP BY authorID ORDER BY count DESC")
        table = mycursor.fetchall()  # grabs table sorted

        #print(table)
        #print("================")
        result = max(range(len(table)),key=lambda i: table[i][0] == str(ctx.author.id)) #gets index of user ID, 0 if user not in list (0msgs for the day)

        #print(table[result])
        if table[result][0] == str(ctx.author.id): #extra check if user is right spot - 0 msgs return 0.
            message_rank_multipler = int(result)+1
        else:
            message_rank_multipler = 1000

        message_rank_multipler = round(max(1,3.5-log(message_rank_multipler)),2)
        #print(message_rank_multipler)

        ######### Booster rank multiplier
        author_roles = [r.id for r in ctx.author.roles]
        if 804494451245711360 in author_roles:
            boost_multiplier = 2
        else:
            boost_multiplier = 1

        amount = round(amount * (boost_multiplier*message_rank_multipler))
        #adding 1000 points to user
        mycursor.execute(
            f"select * from gambledb.points where authorID = {ctx.author.id}"
        )
        table = mycursor.fetchall()
        current_points = int(table[0][2])

        ##################
        bought_multiplier = 1

        mycursor.execute( #gives daily points
            f"update gambledb.points set points = {current_points+amount} where authorID = {ctx.author.id}")
        db.commit()

        embed = discord.Embed(
            title=f"✨ Daily Points ✨",
            description=f"Message multiplier: x{message_rank_multipler}\n"
                        f"Server boost multiplier: x{boost_multiplier}\n"
                        f"Bought multiplier: x{bought_multiplier}\n\n"
                        f"total multiplier: x{message_rank_multipler*boost_multiplier*bought_multiplier}\n\n"
                        f"**{ctx.author.display_name}** has received `{amount}` points. Balance: `{current_points+amount}`"
        )
        await ctx.send(embed=embed)

    @commands.command()
    async def gamble(self, ctx, amount):
        table = checkIfUserinDB(ctx.author.id)

        if len(table) < 1:
            addUserToDB(ctx.author.id, ctx.author.display_name)
            await ctx.send(f"Added {ctx.author.mention}. Use !daily to get some points")
        else:
            current_points = int(table[0][2])
            if amount == "all":
                amount = current_points
            amount = max(0,int(amount))

            if current_points >= amount:
                #take points from user. fuck double dippers
                mycursor.execute(
                    f"update gambledb.points set points = {current_points - amount} where authorID = {ctx.author.id}")
                db.commit()

                #gamble
                dice1 = random.randint(1, 100)
                dice2 = random.randint(1, 100)
                dice3 = random.randint(1, 100)
                dice4 = random.randint(1, 100)
                dice5 = random.randint(1, 100)
                finaldice = random.randint(1, 100)

                msg1 = await ctx.send("Rolling Dice...")
                await msg1.edit(content=f"<a:dice:906239227455475743>...**{dice1}** <a:dice:906239227455475743>")
                await asyncio.sleep(0.3)
                await msg1.edit(content=f"<a:dice:906239227455475743>...**{dice2}** <a:dice:906239227455475743>")
                await asyncio.sleep(0.3)
                await msg1.edit(content=f"<a:dice:906239227455475743>...**{dice3}** <a:dice:906239227455475743>")
                await asyncio.sleep(0.3)
                await msg1.edit(content=f"<a:dice:906239227455475743>...**{dice4}** <a:dice:906239227455475743>")
                await asyncio.sleep(0.3)
                await msg1.edit(content=f"<a:dice:906239227455475743>...**{dice5}** <a:dice:906239227455475743>")
                await asyncio.sleep(0.3)
                await msg1.edit(content=f"<a:dice:906239227455475743>...**{finaldice}** <a:dice:906239227455475743>")
                await asyncio.sleep(0.5)

                table = checkIfUserinDB(ctx.author.id)
                current_points = int(table[0][2])
                gambleprofit = int(table[0][5])
                gambleWins = int(table[0][3])
                gambleLose = int(table[0][4])
                if finaldice > 54: #win

                    mycursor.execute(
                        f"update gambledb.points set points = {current_points+amount*2}, gambleProfit = {gambleprofit+amount}, gambleWin = {gambleWins+1} where authorID = {ctx.author.id}")
                    db.commit()
                    await msg1.edit(
                        content=f"<:pokiooupurplee:845472604658597898>Gz... you rolled: {finaldice}. You now have {current_points + amount*2} points<:PogGottem:898627342925189143>")

                else: #lose
                    mycursor.execute(
                        f"update gambledb.points set points = {current_points}, gambleProfit = {gambleprofit - amount}, gambleLose = {gambleLose + 1} where authorID = {ctx.author.id}")
                    db.commit()
                    await msg1.edit(
                        content=f"<:KEKL:846417220593647656> Bad rng... you rolled: {finaldice} and lost {amount} points. "
                                f"You now have {current_points} points<:KEKL:846417220593647656>")


            else:
                await ctx.send(f"Insufficient points. You have {current_points}")


    @commands.command(aliases=["BJ","blackjack","Blackjack"])
    async def bj(self, ctx, amount):
        table = checkIfUserinDB(ctx.author.id)
        #print(table)
        author_points = int(table[0][2])

        if amount == "all":
            amount = author_points
        elif amount =="half":
            amount =  floor(author_points/2)

        amount = max(0, int(amount))


        if amount > author_points:
            await ctx.send(f"Insufficient points. You have {author_points}")
        else:
            # take points from user. fuck double dippers
            mycursor.execute(
                f"update gambledb.points set points = {author_points - amount} where authorID = {ctx.author.id}")
            db.commit()

            card1, value1 = pickCard()
            card2, value2 = pickCard()
            card3, value3 = pickCard()

            author_num = int(value1) + int(value2)
            dealer_num = int(value3)


            if card1 == "A" and card2 == "A": #if double ace start
                author_num = 12

            embed = discord.Embed(
                title=f"BlackJack | `{amount}` pesos",
                colour=discord.Colour.red()
            )
            embed.add_field(name=f"You | {author_num}", value=f"{card1}, {card2}", inline=False)
            embed.add_field(name=f"Dealer | {dealer_num}",value=f"{card3}", inline=False)
            #description = f"You | {author_num}\n\nDealer | {dealer_num}",
            try:
                embed.set_author(name=f"{ctx.author.display_name}",icon_url=f"{ctx.author.avatar.url}")
            except:
                embed.set_author(name=f"{ctx.author.display_name}", icon_url=f"{ctx.author.default_avatar.url}")
            embed.set_footer(text=f"{ctx.author.id}")

            if author_num == 21: #if win
                embed.add_field(name="Winner", value=f"You won {round(amount*1.5)} points. Total {author_points+(round(amount*1.5))}", inline=False)

                mycursor.execute(
                    f"update gambledb.points set points = {author_points + round(amount*1.5)}, bjWin ={(int(table[0][9]))+1}, bjProfit = {(int(table[0][11]))+round(amount*1.5)} where authorID = {ctx.author.id}")
                db.commit()

                await ctx.send(embed=embed, view=None)
            else: #if lose
                await ctx.send(embed=embed, view=BjButtons(timeout=300))

    @commands.command()
    async def give(self,ctx, member : discord.Member,  amount : int):
        author_table = checkIfUserinDB(ctx.author.id)
        member_table = checkIfUserinDB(member.id)
        author_points = int(author_table[0][2])
        member_points = int(member_table[0][2])

        amount = max(0,amount)

        if author_points >= amount:
            member_exist = 0
            author_exist = 0
            if len(author_table) > 0:
                author_exist = 1
            else:
                addUserToDB(ctx.author.id,ctx.author.display_name)
            if len(member_table) > 0:
                member_exist = 1
            else:
                addUserToDB(member.id,member.display_name)

            if member_exist + author_exist == 2:
                mycursor.execute(
                    f"update gambledb.points set points = {author_points - amount} where authorID = {ctx.author.id}")
                mycursor.execute(
                    f"update gambledb.points set points = {member_points + amount} where authorID = {member.id}")
                db.commit()

                await ctx.send(f"You gave {member.display_name} {amount} points. They now have {member_points+amount} points")

            else:
                await ctx.send("Try again")
        else:
            await ctx.send(f"Insufficient points. Balance: {author_points}")


    @commands.command(aliases=["Board","stats","Stats"])
    async def board(self, ctx):
        """Shows the best and worst gamblers"""
        mycursor.execute(
            f"SELECT * FROM gambledb.points order by abs(points) desc limit 3;"
        )
        point_table = mycursor.fetchall()

        embed = discord.Embed(
            title=f"Misc stats {ctx.guild.name}",
        )
        embed.add_field(name="Top points", value=f"🥇**{point_table[0][1]}**: `{point_table[0][2]}` \n"
                                                 f"🥈**{point_table[1][1]}**: `{point_table[1][2]}` \n"
                                                 f"🥉**{point_table[2][1]}**: `{point_table[2][2]}` \n",
                        inline=False)
        ####### gambles
        mycursor.execute(
            f"SELECT * FROM gambledb.points order by abs(gambleWin+gambleLose) desc"
        )
        most_addict = mycursor.fetchall()

        mycursor.execute(
            f"SELECT * FROM gambledb.points order by gambleProfit+0 desc "
        )
        most_wins = mycursor.fetchall()

        mycursor.execute(
            f"SELECT * FROM gambledb.points order by gambleProfit+0 asc "
        )
        most_lost = mycursor.fetchall()

        embed.add_field(name="Gamblers", value=f"Most Addict: **{most_addict[0][1]}** with `{int(most_addict[0][3])+int(most_addict[0][4])}` gambles \n"
                                               f"Biggest winner: **{most_wins[0][1]}** with `{most_wins[0][5]}` profit \n"
                                               f"Biggest loser: **{most_lost[0][1]}** with `{most_lost[0][5]}` profit xdd \n",
                        inline=False)
        ####### blackjack
        mycursor.execute(
            f"SELECT * FROM gambledb.points order by abs(bjWin+bjLose) desc"
        )
        most_addict = mycursor.fetchall()

        mycursor.execute(
            f"SELECT * FROM gambledb.points order by bjProfit+0 desc "
        )
        most_wins = mycursor.fetchall()

        mycursor.execute(
            f"SELECT * FROM gambledb.points order by bjProfit+0 asc "
        )
        most_lost = mycursor.fetchall()

        embed.add_field(name="Blackjackers (bj)", value=f"Most Addict: **{most_addict[0][1]}** with `{int(most_addict[0][9])+int(most_addict[0][10])}` bjs \n"
                                               f"Biggest winner: **{most_wins[0][1]}** with `{most_wins[0][11]}` profit \n"
                                               f"Biggest loser: **{most_lost[0][1]}** with `{most_lost[0][11]}` profit xdd \n",
                        inline=False)

        ####### DUELS
        mycursor.execute(
            f"SELECT * FROM gambledb.points order by abs(duelWin+duelLose) desc"
        )
        most_addict = mycursor.fetchall()

        mycursor.execute(
            f"SELECT * FROM gambledb.points order by duelProfit+0 desc "
        )
        most_wins = mycursor.fetchall()

        mycursor.execute(
            f"SELECT * FROM gambledb.points order by duelProfit+0 asc "
        )
        most_lost = mycursor.fetchall()

        mycursor.execute(
            f"SELECT * FROM gambledb.points where abs(duelWin+duelLose) > 8 order by abs(duelLose/(duelWin+duelLose)) desc  "
        )
        worst_winrate = mycursor.fetchall() #with more than 9 duels

        mycursor.execute(
            f"SELECT * FROM gambledb.points where abs(duelWin+duelLose) > 8 order by abs(duelLose/(duelWin+duelLose)) asc  "
        )
        best_winrate = mycursor.fetchall()  # with more than 9 duels

        embed.add_field(name="DUELERS (strong white whippers)",
                        value=f"Most Addict: **{most_addict[0][1]}** with `{int(most_addict[0][6]) + int(most_addict[0][7])}` duels \n"
                              f"Biggest winner: **{most_wins[0][1]}** with `{most_wins[0][8]}` profit \n"
                              f"Biggest loser: **{most_lost[0][1]}** with `{most_lost[0][8]}` profit xdd \n"
                              f"WORST winrate: **{worst_winrate[0][1]}** with `{round((int(worst_winrate[0][6])/(int(worst_winrate[0][7])+int(worst_winrate[0][6])))*100,2)}`% \n"
                              f"Best winrate: **{best_winrate[0][1]}** with `{round((int(best_winrate[0][6]) / (int(best_winrate[0][6]) + int(best_winrate[0][7]))) * 100, 2)}`% \n",
                        inline=False)

        await ctx.send(embed=embed)


    @commands.command()
    @commands.cooldown(1,23,commands.BucketType.guild)
    async def duel(self,ctx, amount : int):
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

            await ctx.send(embed=embed,view=duelButton(timeout=15))
        else:
            await ctx.send(f"insufficient points. Balance {author_points}")


    @commands.command(aliases=["Duels"])
    async def duels(self, ctx, member : discord.Member = None):
        if not member:
            member = ctx.author

        table = checkIfUserinDB(member.id)

        embed = discord.Embed(
            title=f"Duels for **{member.display_name}**",
            description=f"Wins: `{table[0][6]}`. Losses `{table[0][7]}`. Profit `{table[0][8]}`\n"
                        f"Winrate: {round((int(table[0][6])/(int(table[0][6])+int(table[0][7])))*100,2)}%"
        )

        try:
            embed.set_author(name=f"{member.display_name}", icon_url=f"{member.avatar.url}")
        except:
            embed.set_author(name=f"{member.display_name}", icon_url=f"{member.default_avatar.url}")

        await ctx.send(embed=embed)

    @commands.command(aliases=["Gambles"])
    async def gambles(self, ctx, member: discord.Member = None):
        if not member:
            member = ctx.author

        table = checkIfUserinDB(member.id)

        embed = discord.Embed(
            title=f"Gambles for **{member.display_name}**",
            description=f"Wins: `{table[0][3]}`. Losses `{table[0][4]}`. Profit `{table[0][5]}`\n"
                        f"Winrate: {round((int(table[0][3]) / (int(table[0][3]) + int(table[0][4])))*100,2)}%"
        )

        try:
            embed.set_author(name=f"{member.display_name}", icon_url=f"{member.avatar.url}")
        except:
            embed.set_author(name=f"{member.display_name}", icon_url=f"{member.default_avatar.url}")

        await ctx.send(embed=embed)


    @commands.command(aliases=["Bjs","BJS","BJs"])
    async def bjs(self, ctx, member: discord.Member = None):
        if not member:
            member = ctx.author

        table = checkIfUserinDB(member.id)

        embed = discord.Embed(
            title=f"BJs for **{member.display_name}**",
            description=f"Wins: `{table[0][9]}`. Losses `{table[0][10]}`. Profit `{table[0][11]}`\n"
                        f"Winrate: {round((int(table[0][9]) / (int(table[0][10]) + int(table[0][9])))*100,2)}"
        )
        try:
            embed.set_author(name=f"{member.display_name}", icon_url=f"{member.avatar.url}")
        except:
            embed.set_author(name=f"{member.display_name}", icon_url=f"{member.default_avatar.url}")

        await ctx.send(embed=embed)


    @commands.command()
    @commands.cooldown(1,1111,commands.BucketType.guild)
    async def lottery(self,ctx, lottery_time : int, prize_pool_amount : int, lottery_ID = None):
        if ctx.author.id == 228143014168625153:
            await ctx.message.delete()
            if not lottery_ID:
                lottery_ID = random.randint(1,100000000)
            prize_pool_amount = min(prize_pool_amount,250000)
            embed = discord.Embed(
                title=f"🎉**{ctx.guild.name.upper()}** LOTTERY!🎉",
            )
            embed.set_footer(text=f"{lottery_ID}")
            prize_pool = embed.add_field(name="💰**Prize Pool**💰",value=f"The lottery currently has a prize pool of `{prize_pool_amount}` points. \n Each ticket is 1.000 points (first free)", inline=False)
            time_left = embed.add_field(name="⏰**Time left**⏰", value=f"This lottery is running for another `{lottery_time}` minute(s)", inline=False)
            new_field = embed.add_field(name="💲Current entries:💲", value="NOBODY?!", inline=False)

            await ctx.send("<@&996897096814837941>")
            message1 = await ctx.send(embed=embed, view=lotteryButton())

            count = 0
            for x in range(lottery_time*3):
                await asyncio.sleep(19)  # change to 20
                minutes_left = ceil(lottery_time-(count/3))
                #print(minutes_left)

                #get points / tickets / entries from db
                embed.set_field_at(1,name="⏰**Time left**⏰",
                                            value=f"Less than `{minutes_left}` minutes left",
                                            inline=False)


                # whoever bought tickets gets added
                mycursor.execute(
                    f"SELECT * FROM gambledb.lottery where lotteryID = {lottery_ID}"
                )
                entries_so_far = mycursor.fetchall()

                entri_message = ""
                for x in range(len(entries_so_far)):
                    entri_message = f"{entri_message}**{entries_so_far[x][2]}**: `{entries_so_far[x][1]}` tickets\n"
                if len(entri_message) == 0:
                    entri_message = "Nobody <:Sadge:915989666824609804>"

                embed.set_field_at(2, name="💲Current entries:💲", value=f"\n{entri_message}", inline=False)


                ######### prize pool
                mycursor.execute(
                    f"SELECT sum(ticketAmount) FROM gambledb.lottery where lotteryID = {lottery_ID};"
                )
                total_tickets = mycursor.fetchall()

                if not str(total_tickets[0][0]) == "None":
                    new_prize_pool_amount = prize_pool_amount + (int(total_tickets[0][0])*800)
                else:
                    continue
                embed.set_field_at(0, name="💰**Prize Pool**💰",value=f"The lottery currently has a prize pool of `{new_prize_pool_amount}` points. \n Each ticket is 1.000 points (first free)", inline=False)

                count += 1

                await message1.edit(embed=embed, view=lotteryButton())

            #PICK WINNER NOW
            mycursor.execute(
                f"SELECT * FROM gambledb.lottery where lotteryID = {lottery_ID};"
            )
            all_entries = mycursor.fetchall()
            all_entries_list = []
            entry_id_list = []
            number_of_tickets_each = []
            for y in range(len(all_entries)):
                all_entries_list.append(all_entries[y][2])
                entry_id_list.append(all_entries[y][0])
                number_of_tickets_each.append(int(all_entries[y][1]))


            winner_id = random.choices(
                entry_id_list, weights=number_of_tickets_each)[0]

            print(winner_id) ########################S
            winner_num = entry_id_list.index(winner_id)
            winner_name = all_entries_list[winner_num]


            mycursor.execute(
                f"SELECT * FROM gambledb.lottery where lotteryID = {lottery_ID}"
            )
            entries_so_far = mycursor.fetchall()

            mycursor.execute(
                f"SELECT * FROM gambledb.lottery where lotteryID = {lottery_ID} and userID = {winner_id}"
            )
            winner_table = mycursor.fetchall()

            embed = discord.Embed(
                title=f"🎉**{ctx.guild.name.upper()}** LOTTERY!🎉",
                description=f"**Winner of Lottery**\n \n 💰**Prize Pool**💰\n\n `{new_prize_pool_amount}` points has been won by **{winner_name}**!"
                            f"\n\n"
                            f"{winner_name} had `{winner_table[0][1]}` ticket(s)"
                            f"\n\n**Total**:\n `{len(entries_so_far)}` Shitters entered with {round(total_tickets[0][0])} tickets "
            )

            await message1.edit(embed=embed, view=None)
            await ctx.send(f"gz {winner_name}!")
            winner_points = checkIfUserinDB(winner_id)

            mycursor.execute(
                f"update gambledb.points set points = {int(winner_points[0][2]) + new_prize_pool_amount}  where authorID = {winner_id}")
            db.commit()


    """@commands.command()
    async def timezone(self, ctx):
        await ctx.send("Choose a timezone!", view=MyView1())"""

def setup(bot):
    bot.add_cog(Gambling(bot))