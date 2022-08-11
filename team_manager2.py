import discord
import random as rd
import traceback
import sys
from discord.ext import commands
from db_handler2 import DatabaseHandler as db2
from token1 import token_tm
from discord_slash import ButtonStyle, SlashCommand
from discord_slash.utils.manage_components import *
import asyncio

intents = discord.Intents.default()
intents.members = True

db_handler = db2("database_TM.db")

bot = commands.Bot(command_prefix = "*", intents = intents)
bot.remove_command("help")
slash = SlashCommand(bot, sync_commands=True)

def check_manager(ctx) -> bool:
    guild = ctx.guild
    member = ctx.author
    role_id = db_handler.get_team_info(guild.id)[5]
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
    embed.add_field(name = "Fonctionnement", value = "Pour utiliser le bot, vous devez d'abord créer une équipe avec la commande `*setup`.\nVous pouvez ensuite ajouter des joueurs à votre équipe en faisant `*add <mention>`.\nAprès un match d'esport, vous pouvez ajouter les résultats des joueurs et de l'équipe à l'aide des commandes ci-dessous.", inline = False)

    embed.add_field(name = "Commandes", value = """`setup`: initialise la base de données d'une équipe

    `match` : envoie un message de gestion de match

    `stats` (mention) : affiche les statistiques du joueur mentionné, ou les vôtres en l'absence de mention.

    `teamstats` : affiche les statistiques de l'équipe

    `add <mention>` : ajoute le joueur mentionné à l'équipe

    `remove` : permet d'enlever un joueur de l'équipe

    `players`: affiche la liste des joueurs de l'équipe

    `leaderboard <critère>`: affiche un classement des joueurs selon le critère. Critères disponibles:

    > - `wr` -> winrate
    > - `w` -> nombre de victoires
    > - `l` -> nombre de défaites
    > - `mvp` -> nombre de fois élu meilleur joueur""", inline = False)
    await ctx.send(embed = embed)


@bot.command()
# fonction de création d'équipe
async def setup(ctx):

    if db_handler.get_team_info(ctx.guild.id) == None:

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

        try:
            buttons = [
        create_button(
            style = ButtonStyle.blue,
            label = "Oui",
            custom_id = "1"),
        create_button(
            style = ButtonStyle.blue,
            label = 'Non',
            custom_id = "2")
    ]
            action_row_buttons = create_actionrow(*buttons)

            boutons = await ctx.send("Votre équipe a-t-elle déjà un nombre de victoires/défaites ?", components = [action_row_buttons])



            def check1(m):
                return m.author.id == ctx.author.id and m.origin_message.id == boutons.id


            button_ctx = await wait_for_component(bot, components = action_row_buttons, check = check1, timeout = 30)
            await button_ctx.defer(ignore=True)

            if button_ctx.custom_id == '1':
                await ctx.send("Combien de victoires votre équipe a-t-elle ?")
                nb_w = await bot.wait_for("message", timeout = 30, check = checkMessage)
                nb_w = int(nb_w.content)

                await ctx.send("Combien de défaites votre équipe a-t-elle ?")
                nb_l = await bot.wait_for("message", timeout = 30, check = checkMessage)
                nb_l = int(nb_l.content)
            else:
                nb_w = 0
                nb_l = 0

        except asyncio.TimeoutError:
            await ctx.send("Délai dépassé !")
            return




        db_handler.setup(ctx.guild.id, team_name, role, nb_w, nb_l)
        embed = discord.Embed(title = "", description = "Équipe créée !", color = blanc)
        embed.set_footer(text = "astuce : pour ajouter des joueurs à l'équipe, faites *add <mention>")
        await ctx.send(embed = embed)
    else:
        await ctx.send("Ce serveur possède déjà une équipe")


# classement des joueurs
@bot.command(aliases = ['lb'])
async def leaderboard(ctx, theme: str = None):
    if db_handler.get_team_info(ctx.guild.id) != None:
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
    else:
        await ctx.send("Ce serveur n'a pas encore d'équipe")

@bot.command()
async def teamstats(ctx):
    if db_handler.get_team_info(ctx.guild.id) != None:
        result = db_handler.get_team_info(ctx.guild.id)

        name = result[1]
        wins = result[2]
        losses = result[3]
        wr = [4]

        embed = discord.Embed(title = "", color = blanc)
        embed.add_field(name = f"Statistiques de {name}", value = f"""`nombre de victoires:` {wins}

        `nombre de défaites:` {losses}

        `nombre de matchs:` {wins+losses}

        `winrate:` {wr}%""")

        await ctx.send(embed = embed)
    else:
        await ctx.send("Ce serveur n'a pas encore d'équipe")


@bot.command()
async def stats(ctx, player: discord.Member = None):
    if db_handler.get_team_info(ctx.guild.id) != None:
        if player == None:
            player = ctx.author
        result = db_handler.get_player_info(player.id, ctx.guild.id)
        if result == None:
            await ctx.send("Ce joueur n'est pas dans l'équipe")
        else:
            wins = result[2]
            losses = result[3]
            wr = result[4]
            mvp = result[5]

            embed = discord.Embed(title = "", color = blanc)
            embed.add_field(name = f"Statistiques de {player.name}", value = f"""`nombre de victoires:` {wins}

            `nombre de défaites:` {losses}

            `nombre de matchs:` {wins+losses}

            `winrate:` {wr}%

            `nombre de titres MVP:` {mvp}""")
            await ctx.send(embed = embed)
    else:
        await ctx.send("Ce serveur n'a pas encore d'équipe")


@bot.command()
async def add(ctx, player: discord.Member):
    if db_handler.get_team_info(ctx.guild.id) != None:
        if check_manager(ctx):
            if not db_handler.is_in_team(player.id, ctx.guild.id):
                db_handler.add_player(player.id, ctx.guild.id)
                await ctx.send("Joueur ajouté !")
            else:
                await ctx.send("Ce joueur est déjà dans l'équipe")
        else:
            await ctx.send("Vous n'avez pas les permissions pour faire ça :x:")
    else:
        await ctx.send("Ce serveur n'a pas encore d'équipe")

# remove

@bot.command()
async def remove(ctx, user: discord.Member = None):
    if user == None:
        
        embed1 = discord.Embed(color = blanc)
        embed1.add_field(name = "Choix du joueur", value = "Choisissez un joueur à l'aide du menu ci-dessous")
        embed1.add_field(name = "Indications", value = "Cliquez sur `changer de joueur` pour modifier un autre joueur.\nCliquez sur `terminer` lorsque la CW est terminée.")

        players = db_handler.players(ctx.guild.id)
        liste = []
        for i in range(1, len(players)+1):
            p = bot.get_user(players[i-1][0])
            liste.append(create_select_option(p.name, value = str(i)))
        liste.append(create_select_option('Terminer', value = '0'))
        select = create_select(
            liste,
            placeholder="choisis un joueur",
            min_values=1,
            max_values=1
        )
        menu = await ctx.send(embed = embed1, components=[create_actionrow(select)])

        def check_menu(m):
            return m.author.id == ctx.author.id and m.origin_message.id == menu.id

        choice_ctx = await wait_for_component(bot, components=select, check=check_menu)
        await choice_ctx.defer(ignore=True)
        deleted = bot.get_user(players[int(choice_ctx.values[0])-1][0])
        await menu.delete()
    
    else:
        deleted = user

    if db_handler.is_in_team(deleted.id, ctx.guild.id):
        embed2 = discord.Embed(color = blanc)
        embed2.add_field(name = f"Êtes-vous sûr de vouloir supprimer {deleted.name} de l'équipe ?", value = "Cette action est irréversible, et les statistiques de ce joueur avec votre équipe seront perdues")
        buttons = [
            create_button(
                style = ButtonStyle.danger,
                label = "oui",
                custom_id = "1"),
            create_button(
                style = ButtonStyle.gray,
                label = 'non',
                custom_id = "2")
                ]
        action_row_buttons = create_actionrow(*buttons)

        boutons = await ctx.send(embed = embed2, components = [action_row_buttons])

        def check1(m):
            return m.author.id == ctx.author.id and m.origin_message.id == boutons.id

        button_ctx = await wait_for_component(bot, components = action_row_buttons, check = check1, timeout=30)
        await button_ctx.defer(ignore=True)


        if button_ctx.custom_id == '1':
            
            await boutons.delete()
            await ctx.send('Joueur supprimé !')
            db_handler.remove_player(deleted.id, ctx.guild.id)
        elif button_ctx.custom_id == '2':
            await boutons.delete()
            await ctx.send('Commande annulée !')
    else:
        await ctx.send("Ce joueur n'est pas dans l'équipe")



@bot.command()
async def players(ctx):
    if db_handler.get_team_info(ctx.guild.id) != None:
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
            embed.set_footer(text = "Pour ajouter un joueur, faites la commande *add <mention>")

            await ctx.send(embed = embed)
    else:
        await ctx.send("Ce serveur n'a pas encore d'équipe")





@bot.command()
async def match(ctx):
    if db_handler.get_team_info(ctx.guild.id) != None:
        if check_manager(ctx):
            logs = [0, 0, 0]
            logs_f = {}
            await choose_player(ctx, logs, logs_f)
        else:
            await ctx.send("Vous n'avez pas les permissions pour faire ça")
    else:
        await ctx.send("Ce serveur n'a pas encore d'équipe")



async def choose_player(ctx, logs, logs_f):
    # Menu select:
    embed1 = discord.Embed(color = blanc)
    embed1.add_field(name = "Choix du joueur", value = "Choisissez un joueur à l'aide du menu ci-dessous")
    embed1.add_field(name = "Indications", value = "Cliquez sur `changer de joueur` pour modifier un autre joueur.\nCliquez sur `terminer` lorsque la CW est terminée.")

    players = db_handler.players(ctx.guild.id)
    liste = []
    for i in range(1, len(players)+1):
        p = bot.get_user(players[i-1][0])
        liste.append(create_select_option(p.name, value = str(i)))
    liste.append(create_select_option('Terminer', value = '0'))
    select = create_select(
        liste,
        placeholder="choisis un joueur",
        min_values=1,
        max_values=1
    )
    menu = await ctx.send(embed = embed1, components=[create_actionrow(select)])

    def check_menu(m):
        return m.author.id == ctx.author.id and m.origin_message.id == menu.id

    choice_ctx = await wait_for_component(bot, components=select, check=check_menu)
    await choice_ctx.defer(ignore=True)
    if choice_ctx.values[0] == '0':
        await menu.delete()
        await end_cw(ctx, logs_f)
        return
    act_player = bot.get_user(players[int(choice_ctx.values[0])-1][0])

    await menu.delete()
    await edit_player(ctx, act_player, logs, logs_f)



async def edit_player(ctx, player, logs, logs_f):

    embed2 = discord.Embed(color = blanc)
    embed2.add_field(name = f"Actions disponibles pour {player.name}", value = "Choisissez une action à l'aide des boutons ci-dessous", inline = False)
    embed2.add_field(name = f"Historique des actions pour {player.name}", value = f"{logs[0]} victoires, {logs[1]} défaites, {logs[2]} titres")


    # Boutons:

    buttons = [
        create_button(
            style = ButtonStyle.blue,
            label = "victoire",
            custom_id = "1"),
        create_button(
            style = ButtonStyle.blue,
            label = 'défaite',
            custom_id = "2"),
        create_button(
            style = ButtonStyle.blue,
            label = 'titre de MVP',
            custom_id = "3"),
        create_button(
            style = ButtonStyle.blue,
            label = "changer de joueur",
            custom_id= '4'),
        create_button(
            style = ButtonStyle.blue,
            label = "terminer",
            custom_id= '5')
    ]
    action_row_buttons = create_actionrow(*buttons)

    boutons = await ctx.send(embed = embed2, components = [action_row_buttons])



    def check1(m):
        return m.author.id == ctx.author.id and m.origin_message.id == boutons.id


    button_ctx = await wait_for_component(bot, components = action_row_buttons, check = check1)

    # Victoire
    if button_ctx.custom_id == '1':
        logs[0] += 1
        logs_f[player.id] = logs
        db_handler.add_win(player.id, 1, ctx.guild.id)
        await boutons.delete()
        await edit_player(ctx, player, logs, logs_f)

    # Défaite
    elif button_ctx.custom_id == '2':
        logs[1] += 1
        logs_f[player.id] = logs
        await boutons.delete()
        await edit_player(ctx, player, logs, logs_f)

    # MVP
    elif button_ctx.custom_id == '3':
        logs[2] += 1
        logs_f[player.id] = logs
        await boutons.delete()
        await edit_player(ctx, player, logs, logs_f)


    # Changement de joueur
    elif button_ctx.custom_id == '4':
        await boutons.delete()
        await choose_player(ctx, [0, 0, 0], logs_f)

    # Terminer
    elif button_ctx.custom_id == '5':
        await boutons.delete()
        await end_cw(ctx, logs_f)


async def end_cw(ctx, logs_f:dict):
    embed1 = discord.Embed(title = "Quel est le résultat de ce match pour l'équipe ?", color = blanc, description = "Choisissez un résultat à l'aide des boutons ci-dessous")
    buttons = [
        create_button(
            style=ButtonStyle.blue,
            label = "Victoire",
            custom_id = '1'),
        create_button(
            style=ButtonStyle.blue,
            label = 'Défaite',
            custom_id = '2'),
        create_button(
            style=ButtonStyle.blue,
            label="Pas de résultat",
            custom_id="3")
    ]
    action_row_buttons = create_actionrow(*buttons)

    boutons = await ctx.send(embed = embed1, components = [action_row_buttons])

    def check1(m):
        return m.author.id == ctx.author.id and m.origin_message.id == boutons.id


    button_ctx = await wait_for_component(bot, components = action_row_buttons, check = check1, timeout = 30)
    txt = ""

    if button_ctx.custom_id == '1':
        await boutons.delete()
        db_handler.team_win(ctx.guild.id, 1)
        await ctx.send("Victoire ajoutée à l'équipe !")
        txt += "**Victoire**\n\n"

    elif button_ctx.custom_id == '2':
        db_handler.team_loose(ctx.guild.id, 1)
        await boutons.delete()
        await ctx.send("Défaite ajoutée à l'équipe !")
        txt += "**Défaite**\n\n"

    elif button_ctx.custom_id == '3':
        await boutons.delete()
        txt += "**Pas de résultat**\n\n"



    for i in logs_f.items():
        p = bot.get_user(i[0])
        txt = txt + f"{p.name} : {str(i[1][0])} victoires, {str(i[1][1])} défaites, {str(i[1][2])} titres\n\n"
    embed2 = discord.Embed(title = "Récapitulatif de match", color = blanc, description = txt)
    await ctx.send(embed = embed2)

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
        
        await ctx.send('Erreur')
"""



# Infos:
blanc = 0xFFFFFF
fleche = "<:fleche:965973335597002792>"
croix = "<:non:965984947842220132>"
check = "<:oui:965985031162052628>"

bot.run(token_tm)
