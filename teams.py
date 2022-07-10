# commandes pour la gestion d'équipe

import discord
import random as rd
from discord.ext import commands
from discord.utils import get
import asyncio
import re
from database_handler_tm import DatabaseHandler

db_handler = DatabaseHandler("database_TM.db")

def check_manager(ctx) -> bool:
    guild = ctx.guild
    member = ctx.author
    role_id = db_handler.get_role(guild.id)[0][0]
    role = guild.get_role(role_id)
    if role in member.roles:
        return True
    else:
        return False

# fonction de création d'équipe
async def setup(ctx, bot):
    if db_handler.get_team_id(ctx.guild.id) == None:

        def checkMessage(message):
            return message.author == ctx.message.author and ctx.message.channel == message.channel

        try:
            await ctx.send("Quel est le nom de votre équipe ?")
            team_name = await bot.wait_for("message", timeout = 30, check = checkMessage)
            team_name = team_name.content
        except asyncio.TimeoutError:
            await ctx.send('Délai dépassé !')
            return

        try:
            await ctx.send("Quel est le rôle discord Manager de votre équipe ?")
            role = await bot.wait_for("message", timeout = 30, check = checkMessage)
            role = str(role.content)
            role = role[3:-1]
        except asyncio.TimeoutError:
            await ctx.send("Délai dépassé !")
            return
        

        db_handler.setup(ctx.guild.id, team_name, role)
        embed = discord.Embed(title = "", description = "Équipe créée !", color = blanc)
        embed.set_footer(text = "astuce : pour ajouter des joueurs à l'équipe, faites *player add <mention>")
        await ctx.send(embed = embed)
    else:
        await ctx.send("Ce serveur possède déjà une équipe")


# classement des joueurs
async def leaderboard(ctx, theme: str, bot):
    if theme == None:
        theme = "wr"
    
    if theme != "wr" and theme != "w" and theme != "l" and theme != "mvp":
        await ctx.send("Cette catégorie n'existe pas :x:")
    
    else:

        result = db_handler.get_lb(ctx.guild.id, theme)
        embed = discord.Embed(title = "Classement des joueurs", color = blanc)

        for i in range(len(result)):
            if theme == "wr":
                str_theme = f"winrate : {result[i][1]}%"
            elif theme == "w":
                str_theme = f"{result[i][1]} victoires"
            elif theme == "l":
                str_theme = f"{result[i][1]} défaites"
            elif theme == "mvp":
                str_theme = f"{result[i][1]} fois élu MVP"
            player_id = result[i][0]
            player = bot.get_user(player_id)
            embed.add_field(name = f"{i+1} : {player.name}", value = f"{str_theme}", inline = False)

        await ctx.send(embed = embed)


# ajout d'une victoire à l'équipe
async def team_win(ctx, nombre: int = 1):
    if check_manager(ctx):
        db_handler.team_win(ctx.guild.id, nombre)
        await ctx.send("Victoire ajoutée !")
    else:
        await ctx.send("Tu n'as pas le droit de faire ça")


# ajout d'une défaite à l'équipe
async def team_loose(ctx, nombre: int = 1):
    if check_manager(ctx):
        db_handler.team_loose(ctx.guild.id, nombre)
        await ctx.send("Défaite ajoutée !")
    else:
        await ctx.send("Tu n'as pas le droit de faire ça")


# statisqtiques d'équipe
async def teamstats(ctx):
    result = db_handler.teamstats(ctx.guild.id)

    name = result[0][0]
    wins = result[0][1]
    losses = result[0][2]
    wr = result[0][3]

    embed = discord.Embed(title = "", color = blanc)
    embed.add_field(name = f"Statistiques de {name}", value = f"""`nombre de victoires:` {wins}

    `nombre de défaites:` {losses}

    `nombre de matchs:` {wins+losses}

    `winrate:` {wr}%""")

    await ctx.send(embed = embed)


# liste des joueurs
async def players(ctx, bot):
    result = db_handler.players(ctx.guild.id)
    if result == []:
        await ctx.send("Pas encore de joueurs dans l'équipe")
    else:
    
        players_name = ""
        for i in range(len(result)):
            player_id = result[i][0]
            player = bot.get_user(player_id)
            players_name = players_name + fleche + str(player.name) + '\n\n'
            
        embed = discord.Embed(title = "Liste des joueurs", color = blanc, description = players_name)
        embed.set_footer(text = "Pour ajouter un joueur, faites la commande *add_player !")

        await ctx.send(embed = embed)



# Infos:
blanc = 0xFFFFFF
fleche = "<:fleche:965973335597002792>"
croix = "<:non:965984947842220132>"
check = "<:oui:965985031162052628>"