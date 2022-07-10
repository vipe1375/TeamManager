import discord
import random as rd
from discord.ext import commands
from discord.utils import get
import asyncio
import re
from database_handler_tm import DatabaseHandler
import players as p
import teams as t
import rosters as r

intents = discord.Intents.default()
intents.members = True

db_handler = DatabaseHandler("database_TM.db")

bot = commands.Bot(command_prefix = "*", intents = intents)
bot.remove_command("help")


def check_manager(ctx) -> bool:
    guild = ctx.guild
    member = ctx.author
    role_id = db_handler.get_role(guild.id)[0][0]
    role = guild.get_role(role_id)
    if role in member.roles:
        return True
    else:
        return False


@bot.event
async def on_ready():
    print("Prêt !")

@bot.command()
async def help(ctx):
    embed = discord.Embed(title = "Aide de TeamManager", color = blanc)
    embed.add_field(name = "Présentation", value = "TeamManager est un bot de gestion des statistiques et performances des joueurs esport.\n\nSon préfixe est `*`, n'hésitez pas à contacter ViPE#3037 en cas de suggestion ou de bug ! :)")
    embed.add_field(name = "Fonctionnement", value = "Pour utiliser le bot, vous devez d'abord créer une équipe avec la commande `*setup`.\nVous pouvez ensuite ajouter des joueurs à votre équipe en faisant `*add_player <mention>.\nAprès un match d'esport, vous pouvez ajouter les résultats des joueurs et de l'équipe à l'aide des commandes ci-dessous.", inline = False)
    embed.add_field(name = "Commandes des stats des joueurs", value = """`player add <mention>`: ajoute un joueur à la liste des joueurs

    `player win <joueur> (nombre)`: ajoute `nombre` victoires au joueur (par défaut: 1)

    `player loose <joueur> (nombre)`: ajoute `nombre` défaites au joueur (par défaut: 1)

    `player mvp <joueur>` : ajoute 1 au nombre de titres MVP du joueur

    `player stats <joueur>`: affiche les statistiques du joueur""", inline = False)

    embed.add_field(name = "Commandes des stats de team", value = """`team setup`: initialise la base de données d'une équipe
    
    `team win (nombre)`: ajoute une victoire à l'équipe
    
    `team loose (nombre)`: ajoute une défaite à l'équipe
    
    `team players`: affiche la liste des joueurs de l'équipe
    
    `team leaderboard <critère>`: affiche un classement des joueurs selon le critère. Critères disponibles:

    > - `wr` -> winrate
    > - `w` -> nombre de victoires
    > - `l` -> nombre de défaites
    > - `mvp` -> nombre de fois élu meilleur joueur""", inline = False)

    #embed.add_field(name = "Commandes de roster", value = """`roster new` : crée un roster dans l'équipe
    
    #`roster add <joueur>` : ajoute un joueur au roster

    #`roster players` : affiche la liste des joueurs du roster
    
    #`roster leaderboard <critère>`: affiche un classement des joueurs selon le critère. Critères disponibles:

    #> - `wr` -> winrate
    #> - `w` -> nombre de victoires
    #> - `l` -> nombre de défaites
    #> - `mvp` -> nombre de fois élu meilleur joueur""", inline = False)
    
    #await ctx.send(embed = embed)

#@bot.command()
#async def roster(ctx, action, opt = None):
#    if action == "new":
#        await r.roster_new(ctx, bot)
#
#    elif action == "add":
#        p_id = opt[3:-1]
#        await r.roster_add()


@bot.command()
async def player(ctx, action: str = None, player: discord.Member = None, nombre: int = 1):
    if action == 'win':
        await p.player_add_win(ctx, player, nombre)
    
    elif action == 'loose':
        await p.player_add_loose(ctx, player, nombre)

    elif action == 'mvp':
        await p.player_add_mvp(ctx, player)

    elif action == 'stats':
        await p.player_stats(ctx, player)

    elif action == 'add':
        await p.add_player(ctx, player)

    else:
        embed = discord.Embed(title = "Commandes des joueurs", description = """`player win <joueur> (nombre)`: ajoute `nombre` victoires au joueur (par défaut: 1)

    `player loose <joueur> (nombre)`: ajoute `nombre` défaites au joueur (par défaut: 1)

    `player mvp <joueur>` : ajoute 1 au nombre de titres MVP du joueur

    `player stats <joueur>`: affiche les statistiques du joueur
    
    `player add <mention>` : ajoute le joueur à l'équipe""", color = blanc)
        await ctx.send(embed = embed)

@bot.command()
async def team(ctx, action: str = None, opt: str = None):
    if action == "win":
        await t.team_win(ctx, int(opt))

    elif action == "loose":
        await t.team_loose(ctx, int(opt))

    elif action == "players":
        await t.players(ctx, bot)

    elif action == "leaderboard":
        await t.leaderboard(ctx, opt, bot)

    elif action == "setup":
        await t.setup(ctx, bot)

    else:
        embed = discord.Embed(title = "Commandes d'équipe", description = """`setup`: initialise la base de données d'une équipe
    
    `team win (nombre)`: ajoute une victoire à l'équipe
    
    `team loose (nombre)`: ajoute une défaite à l'équipe
    
    `team players`: affiche la liste des joueurs de l'équipe
    
    `team leaderboard <critère>`: affiche un classement des joueurs selon le critère. Critères disponibles:

    > - `wr` -> winrate
    > - `w` -> nombre de victoires
    > - `l` -> nombre de défaites
    > - `mvp` -> nombre de fois élu meilleur joueur""")
        await ctx.send(embed = embed)
    



# ----------------| COMMANDES DES TEAMS |---------------- #






"""
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Il manque un argument :x:")
    elif isinstance(error, commands.CommandNotFound):
        await ctx.send("Cette commande n'existe pas :x:")
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("Tu n'as pas les permissions pour faire ça :x:")
    elif isinstance(error, commands.UserInputError):
        await ctx.send("Argument invalide :x:")
    elif isinstance(error, commands.UserNotFound):
        await ctx.send("Cet utilisateur n'existe pas :x:")
    elif isinstance(error, commands.CheckFailure):
        await ctx.send("Tu n'as pas le droit de faire ça")
        
    else:
        await ctx.send("Erreur :x:")
        """

# Infos:
blanc = 0xFFFFFF
fleche = "<:fleche:965973335597002792>"
croix = "<:non:965984947842220132>"
check = "<:oui:965985031162052628>"

bot.run("token")
