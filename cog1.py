from typing import Optional
import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import button, View, Button

from db_handler2 import DatabaseHandler
db_handler = DatabaseHandler("database_TM.db")

blanc = 0xFFFFFF
fleche = "<:fleche:965973335597002792>"
croix = "<:non:965984947842220132>"
check = "<:oui:965985031162052628>"

async def setup(bot: commands.Bot):
    await bot.add_cog(Cog1(bot))


#-------- classe de choix de joueur ---------#

class choose_player(discord.ui.Select):
    def __init__(self, guild: discord.Guild, logs, logs_f):
        self.guild = guild
        self.logs = logs
        self.logs_f = logs_f
        players = db_handler.players(guild.id)
        liste = []
        for i in range(1, len(players)+1):
            p = guild.get_member(players[i-1][0])
            liste.append(discord.SelectOption(label=p.name, value=p.id, ))
        super().__init__(placeholder="Choisissez un joueur",max_values=1,min_values=1,options=liste)

    async def callback(self, itr: discord.Interaction):
        
        if self.values[0] == '0':
            await itr.message.delete()
        else:
            player = self.guild.get_member(int(self.values[0]))
            embed2 = discord.Embed(color = blanc)
            embed2.add_field(name = f"Actions disponibles pour {player.name}", value = "Choisissez une action à l'aide des boutons ci-dessous\n\nAppuyez sur `changer de joueur` pour passer à un autre joueur\nAppuyez sur `terminer` pour passer aux résultats du match", inline = False)

            await itr.response.edit_message(embed = embed2, view=act_on_player(player.id, self.logs, self.logs_f))


class SelectView(View):
    def __init__(self, guild, logs, logs_f, timeout = None):
        super().__init__(timeout=timeout)
        self.add_item(choose_player(guild, logs, logs_f))


#-------- classe d'action sur un joueur --------#

class act_on_player(View):
    def __init__(self, player_id, logs, logs_f):
        super().__init__(timeout=None)
        self.player_id = player_id
        self.logs = logs
        self.logs_f = logs_f
    
    @button(label = "+1 victoire (0)", custom_id="win")
    async def win(self, interaction: discord.Interaction, button: Button):
        #db_handler.add_player_stat(self.player_id, interaction.guild_id, wins=1)
        self.logs[0] += 1
        self.logs_f[self.player_id] = self.logs

        button.label = f"+1 victoire ({self.logs[0]})"

        await interaction.response.edit_message(view = self)

    @button(label='+1 défaite (0)', custom_id='loose')
    async def loose(self, interaction: discord.Interaction, button: Button):
        self.logs[1] += 1
        self.logs_f[self.player_id] = self.logs

        button.label = f"+1 défaite ({self.logs[1]})"

        await interaction.response.edit_message(view = self)

    @button(label = "+1 MVP (0)", custom_id = 'MVP')
    async def mvp(self, itr: discord.Interaction, button: Button):
        self.logs[2] += 1
        self.logs_f[self.player_id] = self.logs

        button.label = f"+1 MVP ({self.logs[2]})"

        await itr.response.edit_message(view = self)

    @button(label = "changer de joueur")
    async def change_player(self, itr: discord.Interaction, button: Button):
        await itr.response.edit_message(view = SelectView(itr.guild, [0, 0, 0], self.logs_f))

    @button(label = "terminer", custom_id = "end")
    async def end(self, itr: discord.Interaction, button: Button):
        await itr.message.delete()
        await itr.response.send_message("Match terminé !")




# ------- commandes ---------#

class Cog1(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    
    # Help:

    @app_commands.command(
        name = 'help',
        description = "Commande d'aide de TeamManager")

    async def help(self, interaction: discord.Interaction):
        e = discord.Embed(title = "Aide de TeamManager", color = blanc)
        e.add_field(name = "Présentation", value = "TeamManager est un bot de gestion des statistiques et performances des joueurs esport.\n\nSon préfixe est `*`, n'hésitez pas à contacter ViPE#3037 en cas de suggestion ou de bug ! :)")
        e.add_field(name = "Fonctionnement", value = "Pour utiliser le bot, vous devez d'abord créer une équipe avec la commande `*setup`.\nVous pouvez ensuite ajouter des joueurs à votre équipe en faisant `*add <mention>`.\nAprès un match d'esport, vous pouvez ajouter les résultats des joueurs et de l'équipe à l'aide des commandes ci-dessous.", inline = False)

        e.add_field(name = "Commandes", value = """`setup`: initialise la base de données d'une équipe

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
        await interaction.response.send_message(embed=e)


    # Setup:

    @app_commands.command(
        name = "setup",
        description = "Initialisez votre équipe",)
    
    async def setup(self, interaction: discord.Interaction, team_name: str, manager_role: discord.Role, victoires: int = 0, défaites: int = 0):
        if db_handler.get_team_info(interaction.guild.id) == None:
            db_handler.setup(interaction.guild.id, team_name, manager_role.id, victoires, défaites)
            embed = discord.Embed(title = "", description = "Équipe créée !", color = blanc)
            embed.set_footer(text = "astuce : pour ajouter des joueurs à l'équipe, faites *add <mention>")
            await interaction.response.send_message(embed = embed)
        else:
            await interaction.response.send_message('Ce serveur a déjà une équipe')


    # Match
    
    @app_commands.command(
        name = "match",
        description = "Affiche le message de gestion de match")
    async def match(self, interaction: discord.Interaction):
        embed1 = discord.Embed(color = blanc)
        embed1.add_field(name = "Choix du joueur", value = "Choisissez un joueur à l'aide du menu ci-dessous")
        embed1.add_field(name = "Indications", value = "Cliquez sur `changer de joueur` pour modifier un autre joueur.")

        await interaction.response.send_message(embed = embed1, view = SelectView(interaction.guild, [0, 0, 0], {}))

    
    # Add

    @app_commands.command(
        name = "add",
        description= "Ajoutez un joueur à votre équipe")
    async def add(self, interaction: discord.Interaction, player: discord.Member):
        await interaction.response.send_message(type(interaction.guild_id))
        if db_handler.get_team_info(interaction.guild_id) != None:
            if not db_handler.is_in_team(player.id, interaction.guild.id):
                db_handler.add_player(player.id, interaction.guild_locale)
                await interaction.response.send_message("Joueur ajouté !")
            else:
                await interaction.response.send_message("Ce joueur est déjà dans l'équipe")
        else:
            await interaction.response.send_message("Ce serveur n'a pas encore d'équipe")

    
    # Remove

    @app_commands.command(
        name = 'remove',
        description= 'Retirez un joueur de votre équipe')
    async def remove(self, itr: discord.Interaction):
        players = db_handler.players(itr.guild_id)
        