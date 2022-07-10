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





# ajout d'un joueur à l'équipe
async def add_player(ctx, player: discord.Member):
    db_handler.add_player(player.id, ctx.guild.id)
    await ctx.send(f'Joueur ajouté !')


# ajout d'une victoire à un joueur
async def player_add_win(ctx, player: discord.Member, nombre: int):
    if check_manager(ctx):
        if db_handler.is_in_team(player.id, ctx.guild.id):
            db_handler.add_win(player.id, nombre, ctx.guild.id)
            await ctx.send(f"Victoire ajoutée !")
        else:
            await ctx.send("Ce joueur n'est pas dans l'équipe")
    else:
        await ctx.send("Tu n'as pas le droit de faire ça.")


# ajout d'une défaite à un joueur
async def player_add_loose(ctx, player: discord.Member, nombre: int):
    if check_manager(ctx):
        try:
            db_handler.add_loss(player.id, nombre, ctx.guild.id)
            await ctx.send(f"Défaite ajoutée !")
        except IndexError:
            await ctx.send("Ce joueur n'est pas dans l'équipe")
    else:
        await ctx.send("Tu n'as pas le droit de faire ça.")


# statistiques du joueur
async def player_stats(ctx, player: discord.Member = None):
    if player == None:
        player = ctx.author
    result = db_handler.stats(player.id, ctx.guild.id)
    if result == []:
        await ctx.send("Ce joueur n'est pas dans l'équipe")
    else:
        wins = result[0][0]
        losses = result[0][1]
        wr = result[0][2]
        mvp = result[0][3]

        embed = discord.Embed(title = "", color = blanc)
        embed.add_field(name = f"Statistiques de {player.name}", value = f"""`nombre de victoires:` {wins}

        `nombre de défaites:` {losses}

        `nombre de matchs:` {wins+losses}

        `winrate:` {wr}%

        `nombre de titres MVP:` {mvp}""")
        await ctx.send(embed = embed)


# ajout d'un titre au joueur
async def player_add_mvp(ctx, player):
    if check_manager(ctx):
        try:
            db_handler.add_mvp(player.id, ctx.guild.id)
            await ctx.send(f"Titre ajouté !")
        except IndexError:
            await ctx.send("Ce joueur n'est pas dans l'équipe")
    else:
        await ctx.send("Tu n'as pas le droit de faire ça.")


# Infos:
blanc = 0xFFFFFF
fleche = "<:fleche:965973335597002792>"
croix = "<:non:965984947842220132>"
check = "<:oui:965985031162052628>"